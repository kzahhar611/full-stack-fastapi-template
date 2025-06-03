"""
Simplified authentication endpoints for Release 1
"""
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ...core.database_simple import get_db
from ...core.security import (
    verify_password, 
    create_access_token, 
    create_refresh_token,
    get_password_hash
)
from ...core.config import settings
from ...models.user_simple import User
from ...schemas.auth import Token
from ...schemas.user import UserLogin, UserResponse
from ...schemas.common import StatusResponse
from ...api.dependencies_simple import get_current_user

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    if user.status.value != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is not active"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    # Create refresh token
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Update last login
    from datetime import datetime
    user.last_login = datetime.utcnow().isoformat()
    db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.get("/me", response_model=dict)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get current user information
    """
    # Refresh user from database to get latest data
    db.refresh(current_user)
    return {
        "id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "full_name": current_user.full_name,
        "role": current_user.role.value,
        "status": current_user.status.value,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "last_login": current_user.last_login,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at
    }


@router.post("/logout", response_model=StatusResponse)
async def logout(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Logout (token invalidation would be handled by client)
    """
    return StatusResponse(
        success=True,
        message="Logged out successfully"
    )