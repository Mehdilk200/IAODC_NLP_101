from fastapi import APIRouter, Request, HTTPException
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os

from database.deps import get_db
from models.UserModel import UserModel
from .schema import LoginRequest, LoginResponse

router_auth = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = os.getenv("JWT_SECRET", "SUPER_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router_auth.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, request: Request):
    db = get_db(request)
    user_model = UserModel(db)

    user = await user_model.get_by_email(payload.email)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user_model.verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="User disabled")

    token = create_access_token({
        "user_id": str(user["_id"]),
        "role": user["role"]
    })

    return {"access_token": token}