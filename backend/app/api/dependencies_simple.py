"""
Simplified API dependencies for Release 1
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..core.database_simple import get_db
from ..core.security import verify_token
from ..models.user_simple import User

# HTTP Bearer scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify the token
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
            
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except Exception:
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (additional check for user status)
    """
    if current_user.status.value != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is not active"
        )
    return current_user


async def get_user_from_token(token: str, db: Session) -> Optional[User]:
    """
    Get user from JWT token (for WebSocket authentication)
    """
    try:
        # Verify the token
        payload = verify_token(token)
        if payload is None:
            return None
            
        user_id: int = payload.get("sub")
        if user_id is None:
            return None
            
        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        if user is None or not user.is_active:
            return None
        
        return user
        
    except Exception:
        return None