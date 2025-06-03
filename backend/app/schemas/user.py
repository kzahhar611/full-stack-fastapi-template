"""
User related Pydantic schemas
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime

from .common import TimestampMixin, UUIDMixin, OrganizationReference


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    display_name: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    timezone: str = Field("UTC", max_length=50)
    language: str = Field("en", pattern="^(en|ar)$")


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(min_length=8, max_length=100)
    role: str = Field("user", pattern="^(super_admin|admin|manager|user|viewer)$")
    organization_id: Optional[int] = None
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v


class UserUpdate(BaseModel):
    """User update schema"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    display_name: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    timezone: Optional[str] = Field(None, max_length=50)
    language: Optional[str] = Field(None, pattern="^(en|ar)$")
    avatar_url: Optional[str] = Field(None, max_length=500)
    preferences: Optional[Dict[str, Any]] = None


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str
    remember_me: bool = False


class UserResponse(UserBase, UUIDMixin, TimestampMixin):
    """User response schema"""
    id: int
    role: str
    status: str
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str] = None
    last_login: Optional[str] = None
    organization: Optional[OrganizationReference] = None
    preferences: Dict[str, Any] = {}
    
    class Config:
        from_attributes = True
        
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}".strip()


class UserListResponse(BaseModel):
    """User list item response"""
    id: int
    uuid: str
    email: str
    first_name: str
    last_name: str
    display_name: Optional[str] = None
    role: str
    status: str
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str] = None
    last_login: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
        
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}".strip()


class UserProfile(BaseModel):
    """User profile schema (current user)"""
    id: int
    uuid: str
    email: str
    first_name: str
    last_name: str
    display_name: Optional[str] = None
    phone: Optional[str] = None
    timezone: str
    language: str
    role: str
    status: str
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str] = None
    last_login: Optional[str] = None
    organization: Optional[OrganizationReference] = None
    preferences: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}".strip()


class UserStats(BaseModel):
    """User statistics"""
    total_rfps_created: int = 0
    total_proposals_created: int = 0
    total_workflows_created: int = 0
    total_workflow_executions: int = 0
    last_activity: Optional[datetime] = None