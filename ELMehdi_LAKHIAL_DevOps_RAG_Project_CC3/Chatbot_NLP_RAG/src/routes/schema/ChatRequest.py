from pydantic import BaseModel

class ChatRequest(BaseModel):
    question: str
    max_token : int = 2000
    temperature : float = 0.2