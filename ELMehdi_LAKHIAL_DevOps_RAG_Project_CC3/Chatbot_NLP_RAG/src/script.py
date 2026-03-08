from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv(".env")

from src.routes.chain import chain_router 
from routes.data_load import data_load_router
from src.routes.user import router_user , ensure_users_collection_and_admin
from routes.auth.auth import router_auth 
from routes.users.user_cl import router_users 
from routes.conversation import router_conversations
from fastapi.security import HTTPBearer
from helpers.config import get_settings
from motor.motor_asyncio import AsyncIOMotorClient
from startup.checkpoints import ensure_chat_collections
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os

app = FastAPI()
security = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:5500",      # Live Server (VS Code)
        "http://127.0.0.1:5500",
        "http://127.0.0.1",
        "http://0.0.0.0:8000",
        "*",                          # ← Remove this in production!
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
        settings = get_settings()
        app.mongodb_client = AsyncIOMotorClient(settings.MONGODB_URI)
        app.mongodb = app.mongodb_client[settings.MONGODB_DB_NAME]
        
        await ensure_chat_collections(app.mongodb)
        await ensure_users_collection_and_admin(app)
        print("Connected to MongoDB")
        print("MONGODB_URI =", settings.MONGODB_URI)
        print("MONGODB_DB_NAME =", settings.MONGODB_DB_NAME)
        
@app.on_event("shutdown")
async def shutdown_db_client():
        app.mongodb_client.close()
        print("Disconnected from MongoDB")



app.include_router(router_users)
app.include_router(router_user)
app.include_router(router_auth)
app.include_router(chain_router)
app.include_router(router_conversations)
app.include_router(data_load_router)

