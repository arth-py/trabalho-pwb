from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import UserResponse, UserCreate
from app.models.token import Token, ForgotPasswordRequest, ResetPasswordRequest, RefreshTokenRequest
from app.repositories.user_repository import get_user_by_username, create_user, get_user_by_email, update_user_password
from app.utils.auth_utils import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user
)
from app.utils.db_utils import get_async_session
from typing import Optional

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_create: UserCreate, db: AsyncSession = Depends(get_async_session)):
    user = await get_user_by_username(db, user_create.email)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user_create.password)
    new_user = await create_user(db, user_create.email, hashed_password, user_create.full_name)
    return new_user

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_async_session)):
    user = await get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token({"user_id": user.id})
    refresh_token = create_refresh_token({"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user=Depends(get_current_user)):
    return current_user

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: AsyncSession = Depends(get_async_session)):
    user = await get_user_by_email(db, request.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    recovery_token = create_access_token({"user_id": user.id}, expires_delta=900)  
    print(f"Recovery token for {user.email}: {recovery_token}")
    return {"message": "Recovery email sent"}

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: AsyncSession = Depends(get_async_session)):
    payload = decode_token(request.token_recuperacao)
    if payload is None:
        raise HTTPException(status_code=400, detail="Invalid or expired recovery token")
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid recovery token data")
    hashed_password = get_password_hash(request.nova_senha)
    await update_user_password(db, user_id, hashed_password)
    return {"message": "Password updated successfully"}

@router.post("/refresh", response_model=Token)
async def refresh_token(request: RefreshTokenRequest):
    payload = decode_token(request.refresh_token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token data")
    access_token = create_access_token({"user_id": user_id})
    return {"access_token": access_token, "token_type": "bearer"}
