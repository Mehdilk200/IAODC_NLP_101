"""
Authentication Routes.
Handles user registration and JWT login.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import timedelta

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
)
from app.database.connection import get_database
from app.core.config import settings

router = APIRouter()


class UserRegister(BaseModel):
    username: str
    password: str
    email: str = ""


class Token(BaseModel):
    access_token: str
    token_type: str
    username: str


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """Register a new recruiter account."""
    db = get_database()
    users_col = db["users"]

    # Check if username already exists
    existing = await users_col.find_one({"username": user_data.username})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Hash password and store user
    hashed_pw = get_password_hash(user_data.password)
    new_user = {
        "username": user_data.username,
        "email": user_data.email,
        "hashed_password": hashed_pw,
    }
    await users_col.insert_one(new_user)

    # Return token immediately after registration
    token = create_access_token(
        data={"sub": user_data.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(access_token=token, token_type="bearer", username=user_data.username)


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate a recruiter and return a JWT token."""
    db = get_database()
    users_col = db["users"]

    user = await users_col.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(access_token=token, token_type="bearer", username=user["username"])


@router.get("/me")
async def get_me(token_data: dict = Depends(lambda: None)):
    """Get current user info (placeholder for token validation)."""
    return {"message": "Authenticated"}
