from pydantic import BaseModel, Field , ConfigDict
from typing import Optional , List
from bson.objectid import ObjectId
from models.enums.roles import roles
from datetime import datetime



class ChunkMetadata(BaseModel):
    source: str
    section: str
    has_code: bool
    allowed_roles: roles

class DataChunk(BaseModel):
        
        _id: Optional[ObjectId]
        file_name: str = Field(..., min_length=1)
        chunk_project_id: str = Field(..., min_length=1)
        chunk_order: int
        chunk_text: str
        chunk_date_pushed : datetime = Field(default_factory=lambda: datetime.now())
        metadata: ChunkMetadata
        model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True
      )
        
        @classmethod
        def get_indexes(cls):
            return [
                {
                    "key": [("chunk_project_id", 1)],
                    "name": "chunk_project_id_index",
                    "unique": False
                },
                {
                    "key": [("file_name", 1)],
                    "name": "file_name_index",
                    "unique": False
                }
            ]