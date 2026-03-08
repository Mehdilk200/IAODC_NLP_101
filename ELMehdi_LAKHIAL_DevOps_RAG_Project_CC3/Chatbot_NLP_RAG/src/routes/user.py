from fastapi import APIRouter, Request , Query
from database.deps import get_db
from models.UserModel import UserModel
import os
from models.enums.roles import roles 



router_user = APIRouter()


async def ensure_users_collection_and_admin(app):
    db = app.mongodb

    # 1) create users collection if not exists
    existing = await db.list_collection_names()
    if "users" not in existing:
        await db.create_collection("users")

    users_col = db["users"]

    # 2) create indexes (safe)
    await users_col.create_index("email", unique=True, name="email_unique_index")
    await users_col.create_index("role", name="role_index")
    await users_col.create_index("created_by", name="created_by_index")
    await users_col.create_index("is_active", name="is_active_index")

    # 3) bootstrap admin if none
    admin = await users_col.find_one({"role": "admin", "is_active": True})

    if admin is None:
        admin_email = os.getenv("ADMIN_EMAIL", "lakhial@local.test").strip().lower()
        admin_password = os.getenv("ADMIN_PASSWORD", "admin_super")

        user_model = UserModel(db)
        await user_model.create_user(
            email=admin_email,
            password=admin_password,
            role="admin",
            created_by=None
        )
        print("Bootstrap admin created:", admin_email)
    else:
        print("Admin already exists:", admin.get("email"))



@router_user.get("/test-users")
async def test_users(request: Request, email: str = Query(...)):
    db = get_db(request)
    user_model = UserModel(db)

    normalized = email.strip().lower()
    u = await user_model.get_by_email(normalized)

    if not u:
        return {"found": False}

    u["_id"] = str(u["_id"])
    return {"found": True, "user": u}