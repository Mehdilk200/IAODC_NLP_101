from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime


class Conversation(BaseModel):
    _id: Optional[ObjectId] = None

    user_id: str = Field(..., min_length=1)  # owner user id
    title: str = Field(default="New conversation")

    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True
    )

    @classmethod
    def get_indexes(cls):
        return [
            {"key": [("user_id", 1)], "name": "conversation_user_id_index", "unique": False},
            {"key": [("updated_at", -1)], "name": "conversation_updated_at_index", "unique": False},
        ]