from typing import Optional
from pydantic import BaseModel

class DataValidationRequest(BaseModel):
        file_name: str 
        overlap_size : Optional[int] = 20
        chunk_size: Optional[int] = 200
        re_set : Optional[int]= 0
