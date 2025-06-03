"""
Organization related Pydantic schemas
"""
from typing import Optional, Dict, Any, Union
from pydantic import BaseModel, EmailStr, Field, validator, field_serializer
from datetime import datetime
from uuid import UUID

from .common import TimestampMixin, UUIDMixin


class OrganizationBase(BaseModel):
    """Base organization schema"""
    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    website: Optional[str] = Field(None, max_length=500)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    
    # Address
    address_line1: Optional[str] = Field(None, max_length=200)
    address_line2: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    
    # Organization details
    organization_type: str = Field(pattern="^(government|private|non_profit|education|healthcare|technology|consulting|other)$")
    industry: Optional[str] = Field(None, max_length=100)
    size: Optional[str] = Field(None, pattern="^(small|medium|large|enterprise)$")


class OrganizationCreate(OrganizationBase):
    """Organization creation schema"""
    slug: str = Field(min_length=3, max_length=100, pattern="^[a-z0-9-]+$")
    
    @validator('slug')
    def validate_slug(cls, v):
        """Validate slug format"""
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Slug can only contain lowercase letters, numbers, and hyphens')
        if v.startswith('-') or v.endswith('-'):
            raise ValueError('Slug cannot start or end with a hyphen')
        return v.lower()


class OrganizationUpdate(BaseModel):
    """Organization update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    website: Optional[str] = Field(None, max_length=500)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    
    # Address
    address_line1: Optional[str] = Field(None, max_length=200)
    address_line2: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    
    # Organization details
    industry: Optional[str] = Field(None, max_length=100)
    size: Optional[str] = Field(None, pattern="^(small|medium|large|enterprise)$")
    
    # Branding
    logo_url: Optional[str] = Field(None, max_length=500)
    primary_color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    secondary_color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    
    # Settings
    settings: Optional[Dict[str, Any]] = None


class OrganizationResponse(OrganizationBase, UUIDMixin, TimestampMixin):
    """Organization response schema"""
    id: int
    slug: str
    status: str
    subscription_tier: str
    is_active: bool
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    settings: Dict[str, Any] = {}
    user_count: int = 0
    
    @field_serializer('uuid')
    def serialize_uuid(self, uuid_val: Union[UUID, str]) -> str:
        """Convert UUID to string"""
        return str(uuid_val)
    
    class Config:
        from_attributes = True


class OrganizationListResponse(BaseModel):
    """Organization list item response"""
    id: int
    uuid: str
    name: str
    slug: str
    organization_type: str
    status: str
    subscription_tier: str
    is_active: bool
    logo_url: Optional[str] = None
    user_count: int = 0
    created_at: datetime
    
    @field_serializer('uuid')
    def serialize_uuid(self, uuid_val: Union[UUID, str]) -> str:
        """Convert UUID to string"""
        return str(uuid_val)
    
    class Config:
        from_attributes = True


class OrganizationStats(BaseModel):
    """Organization statistics"""
    total_users: int = 0
    active_users: int = 0
    total_rfps: int = 0
    total_proposals: int = 0
    total_workflows: int = 0
    total_workflow_executions: int = 0
    storage_used: int = 0  # bytes
    api_calls_this_month: int = 0


class OrganizationSettings(BaseModel):
    """Organization settings schema"""
    default_language: str = Field("en", pattern="^(en|ar)$")
    default_timezone: str = "UTC"
    features: Dict[str, bool] = {}
    branding: Dict[str, Any] = {}
    integrations: Dict[str, Any] = {}
    notifications: Dict[str, Any] = {}
    security: Dict[str, Any] = {}