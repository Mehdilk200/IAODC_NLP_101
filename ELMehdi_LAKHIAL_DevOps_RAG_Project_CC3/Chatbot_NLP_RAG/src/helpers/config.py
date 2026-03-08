from pydantic_settings import BaseSettings , SettingsConfigDict 
from pydantic import BaseModel
from pydantic import field_validator
import json

class settings(BaseSettings):

        model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

        APP_NAME: str 
        APP_VERSION: str 
        KEY_GEMINI: str 
        MAX_TOKENS: int
        MAX_FILE_SIZE: int
        FILE_ALLOWED_EXTNSIONS: list[str] = []
        FILE_UPLOAD_CHANK_SIZE: int 
        
        MONGODB_URI: str
        MONGODB_DB_NAME: str
        MONGODB_COLLECTION_NAME: str
        MONGODB_PROJECT_COLLECTION: str
        @field_validator("FILE_ALLOWED_EXTNSIONS", mode="before")
        @classmethod
        def parse_list(cls, v):
                if isinstance(v, str):
                        return json.loads(v)
                return v
        
def get_settings() -> settings:
    return settings()

