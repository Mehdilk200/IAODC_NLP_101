from pydantic import BaseModel, Field
from typing import Literal, Optional, Any, Dict, List


class CreateConversationRequest(BaseModel):
    title: str = Field(default="New conversation", max_length=120)
    


class AddMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=6000)


class MessageResponse(BaseModel):
    id: str
    role: Literal["user", "assistant", "system"]
    content: str
    sources: Optional[List[Dict[str, Any]]] = None