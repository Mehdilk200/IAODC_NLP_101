"""
MongoDB connection management using Motor (async driver).
"""

import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

logger = logging.getLogger(__name__)

# Module-level state
client: AsyncIOMotorClient = None
database = None


async def connect_to_mongo():
    """Connect to MongoDB using Motor async client."""
    global client, database
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    database = client[settings.DATABASE_NAME]
    logger.info(f"Connected to MongoDB: {settings.DATABASE_NAME}")


async def close_mongo_connection():
    """Close the MongoDB connection."""
    global client
    if client:
        client.close()
        logger.info("MongoDB connection closed")


def get_database():
    """Return the database instance."""
    return database
