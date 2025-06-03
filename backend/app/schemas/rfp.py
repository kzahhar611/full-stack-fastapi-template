"""
RFP related Pydantic schemas
"""
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field, field_validator, field_serializer
from datetime import date, datetime
from uuid import UUID

from .common import TimestampMixin, UUIDMixin, OrganizationReference, UserReference


class RFPBase(BaseModel):
    """Base RFP schema"""
    title: str = Field(min_length=1, max_length=300)
    description: Optional[str] = None
    rfp_number: str = Field(min_length=1, max_length=100)
    rfp_type: str = Field(pattern="^(goods|services|construction|consulting|technology|other)$")
    issue_date: date
    submission_deadline: date
    estimated_budget: Optional[float] = Field(None, ge=0)
    currency: str = Field("USD", max_length=3)
    requirements: Dict[str, Any] = {}
    contact_person: Optional[str] = Field(None, max_length=200)
    contact_email: Optional[str] = Field(None, max_length=255)
    
    @field_validator('submission_deadline')
    @classmethod
    def validate_submission_deadline(cls, v, info):
        """Ensure submission deadline is after issue date"""
        if 'issue_date' in info.data and v <= info.data['issue_date']:
            raise ValueError('Submission deadline must be after issue date')
        return v


class RFPCreate(RFPBase):
    """RFP creation schema"""
    organization_id: Optional[int] = None  # Will be set automatically if not provided


class RFPUpdate(BaseModel):
    """RFP update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=300)
    description: Optional[str] = None
    rfp_type: Optional[str] = Field(None, pattern="^(goods|services|construction|consulting|technology|other)$")
    submission_deadline: Optional[date] = None
    estimated_budget: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=3)
    requirements: Optional[Dict[str, Any]] = None
    contact_person: Optional[str] = Field(None, max_length=200)
    contact_email: Optional[str] = Field(None, max_length=255)
    status: Optional[str] = Field(None, pattern="^(draft|published|open|closed|awarded|cancelled)$")
    is_public: Optional[bool] = None


class RFPResponse(RFPBase, UUIDMixin, TimestampMixin):
    """RFP response schema"""
    id: int
    status: str
    is_active: bool
    is_public: bool
    ai_analysis: Dict[str, Any] = {}
    organization: Optional[OrganizationReference] = None
    creator: Optional[UserReference] = None
    days_until_deadline: int
    is_open: bool
    
    class Config:
        from_attributes = True


class RFPListResponse(BaseModel):
    """RFP list item response"""
    id: int
    uuid: str
    title: str
    rfp_number: str
    rfp_type: str
    status: str
    issue_date: date
    submission_deadline: date
    estimated_budget: Optional[float] = None
    currency: str
    is_public: bool
    days_until_deadline: int
    created_at: datetime
    
    @field_serializer('uuid')
    def serialize_uuid(self, uuid_val: Union[UUID, str]) -> str:
        """Convert UUID to string"""
        return str(uuid_val)
    
    class Config:
        from_attributes = True


class RFPStats(BaseModel):
    """RFP statistics"""
    total_rfps: int = 0
    draft_rfps: int = 0
    published_rfps: int = 0
    closed_rfps: int = 0
    average_budget: Optional[float] = None
    upcoming_deadlines: int = 0