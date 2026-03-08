from bson import ObjectId
from datetime import datetime


class ConversationModel:
    collection_name = "conversations"

    def __init__(self, db):
        self.db = db
        self.collection = self.db[self.collection_name]

    async def create(self, user_id: str, title: str = "New conversation"):
        doc = {
            "user_id": user_id,
            "title": title,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        res = await self.collection.insert_one(doc)
        return str(res.inserted_id)

    async def list_by_user(self, user_id: str, limit: int = 50):
        cursor = (
            self.collection.find({"user_id": user_id})
            .sort("updated_at", -1)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def get_by_id(self, conversation_id: str):
        return await self.collection.find_one({"_id": ObjectId(conversation_id)})

    async def touch(self, conversation_id: str):
        await self.collection.update_one(
            {"_id": ObjectId(conversation_id)},
            {"$set": {"updated_at": datetime.utcnow()}}
        )

    async def delete(self, conversation_id: str, user_id: str):
        # owner only
        await self.collection.delete_one(
            {"_id": ObjectId(conversation_id), "user_id": user_id}

        )

    async def delete_conv(self, conversation_id: str):
        from bson import ObjectId
        await self.db["conversations"].delete_one(
            {"_id": ObjectId(conversation_id)}
        )