"""
Authentication related Pydantic schemas
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenData(BaseModel):
    """Token payload data"""
    user_id: int
    email: str
    role: str
    organization_id: Optional[int] = None


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str
    new_password: str = Field(min_length=8, max_length=100)


class EmailVerificationRequest(BaseModel):
    """Email verification request"""
    email: EmailStr


class EmailVerificationConfirm(BaseModel):
    """Email verification confirmation"""
    token: str


class ChangePasswordRequest(BaseModel):
    """Change password request"""
    current_password: str
    new_password: str = Field(min_length=8, max_length=100)