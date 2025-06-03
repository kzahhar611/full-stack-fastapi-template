"""
TenderWise AI - Authentication Schemas
"""

from typing import Optional
from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str
    user: "UserResponse"

class TokenData(BaseModel):
    """Token data schema"""
    email: Optional[str] = None

class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """User response schema"""
    id: int
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool
    is_verified: bool
    organization: Optional[str] = None
    position: Optional[str] = None
    language: str = "en"
    timezone: str = "UTC"

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    """User creation schema"""
    email: EmailStr
    password: str
    full_name: str
    organization: Optional[str] = None
    position: Optional[str] = None
    language: str = "en"
    timezone: str = "UTC"

class UserUpdate(BaseModel):
    """User update schema"""
    full_name: Optional[str] = None
    organization: Optional[str] = None
    position: Optional[str] = None
    phone: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None

class PasswordChange(BaseModel):
    """Password change schema"""
    current_password: str
    new_password: str