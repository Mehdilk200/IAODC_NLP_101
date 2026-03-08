from pydantic import BaseModel, Field, EmailStr
from typing import Literal, Optional


Role = Literal["admin", "manager", "user"]


class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: Role


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    role: Role
    created_by: Optional[str] = None
    is_active: bool