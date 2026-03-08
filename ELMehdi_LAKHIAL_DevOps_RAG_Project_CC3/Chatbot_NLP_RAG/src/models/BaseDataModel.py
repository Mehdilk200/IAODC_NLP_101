

from helpers.config import get_settings
from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId

class BaseDataModel:
    def __init__(self, db_client: AsyncIOMotorClient):
        self.db_client = db_client
        self.app_settings = get_settings()
        config_dict = self.app_settings.model_dump()
        db_name = config_dict.get("MONGODB_DB_NAME", "chatbot_db_rag")
        self.db = self.db_client[db_name]