"""
TenderWise AI - Authentication Dependencies
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from core.database import get_db
from auth.auth import decode_access_token, get_user_by_email
from models.user import User

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    # Get user email from token
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    # Get user from database
    user = get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user

async def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current superuser"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

def get_optional_current_user(
    token: Optional[str] = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if token is provided (optional)"""
    if not token:
        return None
    
    try:
        payload = decode_access_token(token)
        if payload is None:
            return None
        
        email: str = payload.get("sub")
        if email is None:
            return None
        
        user = get_user_by_email(db, email=email)
        return user
    except Exception:
        return None