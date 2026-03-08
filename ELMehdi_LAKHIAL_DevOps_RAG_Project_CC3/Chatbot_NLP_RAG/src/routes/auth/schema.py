from pydantic import BaseModel , EmailStr


class LoginRequest(BaseModel):
    email: str # EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"