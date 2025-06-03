"""
Authentication endpoints
"""
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.security import (
    verify_password, 
    create_access_token, 
    create_refresh_token,
    verify_token,
    create_password_reset_token,
    verify_password_reset_token,
    create_email_verification_token,
    verify_email_verification_token,
    get_password_hash
)
from ...core.config import settings
from ...models.user import User
from ...schemas.auth import (
    Token, 
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    EmailVerificationRequest,
    EmailVerificationConfirm,
    ChangePasswordRequest
)
from ...schemas.user import UserLogin, UserResponse
from ...schemas.common import StatusResponse
from ...api.dependencies import get_current_user

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


@router.post("/login/oauth2", response_model=Token)
async def login_oauth2(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """
    OAuth2 compatible token login (form data format)
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
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
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
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


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_request: RefreshTokenRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Refresh access token using refresh token
    """
    payload = verify_token(token_request.refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/password-reset", response_model=StatusResponse)
async def request_password_reset(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Request password reset
    """
    user = db.query(User).filter(User.email == request.email).first()
    
    # Always return success to prevent email enumeration
    if user and user.is_active:
        # Generate password reset token
        reset_token = create_password_reset_token(user.email)
        
        # Store token in user record (in production, you might want to store this in Redis)
        user.password_reset_token = reset_token
        db.commit()
        
        # TODO: Send email with reset token
        # await send_password_reset_email(user.email, reset_token)
    
    return StatusResponse(
        success=True,
        message="If the email exists, a password reset link has been sent"
    )


@router.post("/password-reset/confirm", response_model=StatusResponse)
async def confirm_password_reset(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db)
) -> Any:
    """
    Confirm password reset with token
    """
    email = verify_password_reset_token(request.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token"
        )
    
    user = db.query(User).filter(User.email == email).first()
    if not user or user.password_reset_token != request.token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid password reset token"
        )
    
    # Update password
    user.hashed_password = get_password_hash(request.new_password)
    user.password_reset_token = None
    db.commit()
    
    return StatusResponse(
        success=True,
        message="Password reset successfully"
    )


@router.post("/email-verification", response_model=StatusResponse)
async def request_email_verification(
    request: EmailVerificationRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Request email verification
    """
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_verified:
        return StatusResponse(
            success=True,
            message="Email is already verified"
        )
    
    # Generate verification token
    verification_token = create_email_verification_token(user.email)
    
    # Store token in user record
    user.email_verification_token = verification_token
    db.commit()
    
    # TODO: Send verification email
    # await send_email_verification(user.email, verification_token)
    
    return StatusResponse(
        success=True,
        message="Verification email sent"
    )


@router.post("/email-verification/confirm", response_model=StatusResponse)
async def confirm_email_verification(
    request: EmailVerificationConfirm,
    db: Session = Depends(get_db)
) -> Any:
    """
    Confirm email verification with token
    """
    email = verify_email_verification_token(request.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    user = db.query(User).filter(User.email == email).first()
    if not user or user.email_verification_token != request.token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    
    # Mark email as verified
    user.is_verified = True
    user.email_verification_token = None
    db.commit()
    
    return StatusResponse(
        success=True,
        message="Email verified successfully"
    )


@router.post("/change-password", response_model=StatusResponse)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Change user password (requires current password)
    """
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(request.new_password)
    db.commit()
    
    return StatusResponse(
        success=True,
        message="Password changed successfully"
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get current user information
    """
    # Refresh user from database to get latest data
    db.refresh(current_user)
    return current_user


@router.post("/logout", response_model=StatusResponse)
async def logout(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Logout (token invalidation would be handled by client)
    """
    # In a production system, you might want to:
    # 1. Add token to a blacklist (Redis)
    # 2. Update last_logout timestamp
    # 3. Log the logout event
    
    return StatusResponse(
        success=True,
        message="Logged out successfully"
    )