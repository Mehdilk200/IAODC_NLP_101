from fastapi import APIRouter, Request, HTTPException, Depends , status
from database.deps import get_db
from models.UserModel import UserModel
from middlewares.auth_guard import get_current_user
from .schema import CreateUserRequest
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from bson import ObjectId
from jose import JWTError, jwt
import os
from helpers.config import get_settings
router_users = APIRouter(prefix="/users", tags=["users"])


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _can_create(actor_role: str, target_role: str) -> bool:
    if actor_role == "admin":
        return target_role in ["manager", "user"]
    if actor_role == "manager":
        return target_role == "user"
    return False


async def _assert_manager_scope(db, actor_id: str, target_user_id: str) -> bool:
    
    users = db["users"]
    target = await users.find_one({"_id": __import__("bson").ObjectId(target_user_id)})
    if not target:
        return False
    return target.get("created_by") == actor_id


@router_users.post("")
async def create_user(
    payload: CreateUserRequest,
    request: Request,
    current=Depends(get_current_user)
):
    db = get_db(request)
    user_model = UserModel(db)

    actor_role = current.get("role")
    actor_id = current.get("user_id")

    if not _can_create(actor_role, payload.role):
        raise HTTPException(status_code=403, detail="Forbidden")

    email = _normalize_email(payload.email)

    # prevent duplicate emails
    exists = await user_model.get_by_email(email)
    if exists:
        raise HTTPException(status_code=409, detail="Email already exists")

    created_by = None
    if actor_role in ["admin", "manager"]:
        created_by = actor_id

    new_id = await user_model.create_user(
        email=email,
        password=payload.password,
        role=payload.role,
        created_by=created_by
    )

    return {"id": new_id, "email": email, "role": payload.role, "created_by": created_by}


@router_users.get("/me")
async def me(request: Request, current=Depends(get_current_user)):
    db = get_db(request)
    user_model = UserModel(db)

    user = await user_model.get_by_id(current["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "role": user["role"],
        "created_by": user.get("created_by"),
        "is_active": user.get("is_active", True)
    }




router_users_list = APIRouter(tags=["users"])



# ================================================================
#  JWT decode helper — reuse whatever you already have
# ================================================================
def decode_token(token: str) -> dict:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return decode_token(credentials.credentials)


# ================================================================
#  GET /users  —  list users based on role hierarchy
#
#  admin   → sees ALL users (admin + manager + user)
#            ?created_by=me  → only users HE created
#  manager → sees only users with role=user that HE created
#  user    → 403 Forbidden
# ================================================================
from fastapi import Request

@router_users_list.get("/users", summary="List users (hierarchy-based)")
async def list_users(
    request: Request,
    created_by_me: bool = False,          # ?created_by_me=true
    role_filter: Optional[str] = None,    # ?role_filter=manager
    current_user: dict = Depends(get_current_user),
):
    """
    Returns users visible to the authenticated user based on role hierarchy.

    - **admin**   : sees all users. Optionally filter by ?created_by_me=true
    - **manager** : sees only `role=user` users that this manager created
    - **user**    : 403 Forbidden
    """
    caller_role = current_user.get("role")
    caller_id   = current_user.get("user_id")

    if caller_role == "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Users with role 'user' cannot list other users"
        )

    db = request.app.mongodb
    query = {}

    if caller_role == "admin":
        # Admin sees everyone — optionally filter
        if created_by_me:
            # created_by is stored as plain string (not ObjectId) in your DB
            query["created_by"] = caller_id
        if role_filter and role_filter in ("admin", "manager", "user"):
            query["role"] = role_filter

    elif caller_role == "manager":
        # Manager sees ONLY role=user that he created
        # created_by stored as plain string
        query["role"]       = "user"
        query["created_by"] = caller_id   # plain string match

    # Fetch from MongoDB
    cursor = db["users"].find(query, {
        "_id":        1,
        "email":      1,
        "role":       1,
        "is_active":  1,
        "created_by": 1,
        "created_at": 1,
    })

    users = []
    async for doc in cursor:
        users.append({
            "id":         str(doc["_id"]),
            "email":      doc.get("email", ""),
            "role":       doc.get("role", "user"),
            "is_active":  doc.get("is_active", True),
            "created_by": str(doc["created_by"]) if doc.get("created_by") else None,
            "created_at": str(doc.get("created_at", "")),
        })

    return {
        "total":  len(users),
        "caller": {"id": caller_id, "role": caller_role},
        "items":  users,
    }