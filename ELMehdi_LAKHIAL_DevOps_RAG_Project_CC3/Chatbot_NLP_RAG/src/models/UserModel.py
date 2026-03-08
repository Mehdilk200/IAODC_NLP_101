from typing import Optional
from bson import ObjectId
from datetime import datetime
from passlib.context import CryptContext

from database.db_schema.user_s import User

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class UserModel:
    collection_name = "users"

    def __init__(self, db):
        self.db = db
        self.collection = self.db[self.collection_name]

    # Password utils
    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)

    # Create user
    async def create_user(
        self,
        email: str,
        password: str,
        role: str,
        created_by: Optional[str] = None
    ):
        password_hash = self.hash_password(password)

        user = User(
            email=email,
            password_hash=password_hash,
            role=role,
            created_by=created_by,
            is_active=True,
            created_at=datetime.now()
        )

        result = await self.collection.insert_one(user.model_dump(by_alias=True))
        return str(result.inserted_id)

    async def get_by_email(self, email: str):
        return await self.collection.find_one({"email": email})

    async def get_by_id(self, user_id: str):
        return await self.collection.find_one({"_id": ObjectId(user_id)})

    async def get_users_by_creator(self, creator_id: str):
        return self.collection.find({"created_by": creator_id})

    async def update_role(self, user_id: str, new_role: str):
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"role": new_role}}
        )

    async def disable_user(self, user_id: str):
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_active": False}}
        )