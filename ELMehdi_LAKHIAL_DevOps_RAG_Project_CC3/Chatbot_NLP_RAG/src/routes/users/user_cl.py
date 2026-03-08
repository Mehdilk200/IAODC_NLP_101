from fastapi import APIRouter, Request, HTTPException, Depends, status
from database.deps import get_db
from models.UserModel import UserModel
from middlewares.auth_guard import get_current_user   # ← only one definition
from .schema import CreateUserRequest
from typing import Optional
from bson import ObjectId

# ================================================================
#  ROUTER 1 — /users  (POST create + GET me + GET list)
# ================================================================
router_users = APIRouter(prefix="/users", tags=["users"])


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _can_create(actor_role: str, target_role: str) -> bool:
    if actor_role == "admin":
        return target_role in ["manager", "user"]
    if actor_role == "manager":
        return target_role == "user"
    return False


# ── POST /users ──────────────────────────────────────────────────
@router_users.post("")
async def create_user(
    payload: CreateUserRequest,
    request: Request,
    current=Depends(get_current_user)
):
    db         = get_db(request)
    user_model = UserModel(db)
    actor_role = current.get("role")
    actor_id   = current.get("user_id")

    if not _can_create(actor_role, payload.role):
        raise HTTPException(status_code=403, detail="Forbidden")

    email = _normalize_email(payload.email)

    exists = await user_model.get_by_email(email)
    if exists:
        raise HTTPException(status_code=409, detail="Email already exists")

    created_by = actor_id if actor_role in ["admin", "manager"] else None

    new_id = await user_model.create_user(
        email=email,
        password=payload.password,
        role=payload.role,
        created_by=created_by
    )

    return {
        "id":         new_id,
        "email":      email,
        "role":       payload.role,
        "created_by": created_by
    }


# ── GET /users/me ────────────────────────────────────────────────
@router_users.get("/me")
async def me(request: Request, current=Depends(get_current_user)):
    db         = get_db(request)
    user_model = UserModel(db)

    user = await user_model.get_by_id(current["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id":         str(user["_id"]),
        "email":      user["email"],
        "role":       user["role"],
        "created_by": user.get("created_by"),
        "is_active":  user.get("is_active", True)
    }


# ── GET /users  —  hierarchy-based listing ───────────────────────
#
#  admin   → ga3 les users  |  +?created_by_me=true  |  +?role_filter=manager
#  manager → role=user li huwa crea f9at
#  user    → 403
# ─────────────────────────────────────────────────────────────────
@router_users.get("")
async def list_users(
    request:       Request,
    created_by_me: bool            = False,
    role_filter:   Optional[str]   = None,
    current=Depends(get_current_user),
):
    caller_role = current.get("role")
    caller_id   = current.get("user_id")   # plain string e.g. "69a67c9e7dea2ce331201542"

    # ── permission check ──
    if caller_role == "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Role 'user' cannot list users"
        )

    db    = request.app.mongodb
    query = {}

    if caller_role == "admin":
        # admin sees everyone; optional filters
        if created_by_me:
            query["created_by"] = caller_id          # stored as plain string
        if role_filter in ("admin", "manager", "user"):
            query["role"] = role_filter

    elif caller_role == "manager":
        # manager sees only the users HE created
        query["role"]       = "user"
        query["created_by"] = caller_id              # plain string match

    # ── fetch ──
    projection = {
        "_id":        1,
        "email":      1,
        "role":       1,
        "is_active":  1,
        "created_by": 1,
        "created_at": 1,
    }
    cursor = db["users"].find(query, projection)

    items = []
    async for doc in cursor:
        items.append({
            "id":         str(doc["_id"]),
            "email":      doc.get("email", ""),
            "role":       doc.get("role", "user"),
            "is_active":  doc.get("is_active", True),
            "created_by": doc.get("created_by"),     # already a plain string
            "created_at": str(doc.get("created_at", "")),
        })

    return {
        "total":  len(items),
        "caller": {"id": caller_id, "role": caller_role},
        "items":  items,
    }