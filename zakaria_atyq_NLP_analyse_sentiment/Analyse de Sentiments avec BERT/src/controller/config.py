import os
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
MODEL_DIR = os.getenv("MODEL_DIR", "./model")
MODEL_NAME = os.getenv("MODEL_FALLBACK", "bert-base-uncased")
MAX_LEN = int(os.getenv("MAX_LEN", 128))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")