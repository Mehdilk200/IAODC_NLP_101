from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime
from models.enums.roles import roles


class User(BaseModel):
    _id: Optional[ObjectId] = None

    email: str = Field(..., min_length=5)
    password_hash: str = Field(..., min_length=10)

    role: roles = Field(default=roles.USER)

    # Hierarchy ownership
    # admin: created_by = None
    # manager: created_by = admin_id
    # user: created_by = manager_id or admin_id
    created_by: Optional[str] = None

    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now())

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True
    )

    @classmethod
    def get_indexes(cls):
        return [
            {"key": [("email", 1)], "name": "email_unique_index", "unique": True},
            {"key": [("role", 1)], "name": "role_index", "unique": False},
            {"key": [("created_by", 1)], "name": "created_by_index", "unique": False},
            {"key": [("is_active", 1)], "name": "is_active_index", "unique": False},
        ]