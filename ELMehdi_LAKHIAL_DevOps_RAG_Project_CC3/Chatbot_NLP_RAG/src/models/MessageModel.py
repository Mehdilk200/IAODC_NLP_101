from bson import ObjectId
from datetime import datetime
from typing import Optional, List, Dict, Any


class MessageModel:
    collection_name = "messages"

    def __init__(self, db):
        self.db = db
        self.collection = self.db[self.collection_name]

    async def add(
        self,
        conversation_id: str,
        role: str,
        content: str,
        sources: Optional[List[Dict[str, Any]]] = None
    ):
        doc = {
            "conversation_id": conversation_id,
            "role": role,  
            "content": content,
            "sources": sources,
            "created_at": datetime.utcnow(),
        }
        res = await self.collection.insert_one(doc)
        return str(res.inserted_id)

    async def list_by_conversation(self, conversation_id: str, limit: int = 200):
        cursor = (
            self.collection.find({"conversation_id": conversation_id})
            .sort("created_at", 1)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def delete_by_conversation(self, conversation_id: str):
        await self.collection.delete_many({"conversation_id": conversation_id})

    async def get_last_message(self, conversation_id: str):
        last = await (
            self.collection.find({"conversation_id": conversation_id})
            .sort("created_at", -1)
            .limit(1)
            .to_list(length=1)
        )
        return last[0] if last else None

    async def count_by_conversation(self, conversation_id: str) -> int:
        return await self.collection.count_documents({"conversation_id": conversation_id})
    
    async def delete_by_conversation(self, conversation_id: str):
        await self.db["messages"].delete_many(
            {"conversation_id": conversation_id}
        )