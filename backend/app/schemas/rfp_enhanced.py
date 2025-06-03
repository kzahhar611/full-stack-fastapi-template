"""
Enhanced RFP schemas for Release 5 with document management and templates
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field, validator
from enum import Enum

from .common import UUIDMixin, TimestampMixin


class RFPStatusEnum(str, Enum):
    """RFP status enumeration"""
    DRAFT = "draft"
    PUBLISHED = "published"
    OPEN = "open"
    CLOSED = "closed"
    AWARDED = "awarded"
    CANCELLED = "cancelled"


class RFPTypeEnum(str, Enum):
    """RFP type enumeration"""
    GOODS = "goods"
    SERVICES = "services"
    CONSTRUCTION = "construction"
    CONSULTING = "consulting"
    TECHNOLOGY = "technology"
    OTHER = "other"


class DocumentTypeEnum(str, Enum):
    """Document type enumeration"""
    SPECIFICATION = "specification"
    ATTACHMENT = "attachment"
    TEMPLATE = "template"
    PROPOSAL = "proposal"
    EVALUATION = "evaluation"
    CONTRACT = "contract"
    OTHER = "other"


# Document Schemas
class RFPDocumentBase(BaseModel):
    """Base RFP document schema"""
    filename: str = Field(..., max_length=255)
    original_filename: str = Field(..., max_length=255)
    file_size: int = Field(..., gt=0)
    mime_type: str = Field(..., max_length=100)
    document_type: DocumentTypeEnum = DocumentTypeEnum.ATTACHMENT
    description: Optional[str] = None
    is_public: bool = False
    is_required: bool = False


class RFPDocumentCreate(RFPDocumentBase):
    """Create RFP document schema"""
    file_path: str = Field(..., max_length=500)


class RFPDocumentUpdate(BaseModel):
    """Update RFP document schema"""
    description: Optional[str] = None
    is_public: Optional[bool] = None
    is_required: Optional[bool] = None
    document_type: Optional[DocumentTypeEnum] = None


class RFPDocumentResponse(RFPDocumentBase, UUIDMixin):
    """RFP document response schema"""
    id: int
    upload_date: datetime
    uploaded_by_id: int
    rfp_id: int
    
    # File access info (no actual file_path for security)
    download_url: Optional[str] = None
    
    class Config:
        from_attributes = True


# Template Schemas
class RFPTemplateBase(BaseModel):
    """Base RFP template schema"""
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    category: str = Field(..., max_length=100)
    rfp_type: RFPTypeEnum
    template_data: Dict[str, Any] = Field(default_factory=dict)
    default_requirements: Dict[str, Any] = Field(default_factory=dict)
    evaluation_criteria_template: Dict[str, Any] = Field(default_factory=dict)
    description_template: Optional[str] = None
    requirements_template: Optional[str] = None
    is_active: bool = True


class RFPTemplateCreate(RFPTemplateBase):
    """Create RFP template schema"""
    pass


class RFPTemplateUpdate(BaseModel):
    """Update RFP template schema"""
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    rfp_type: Optional[RFPTypeEnum] = None
    template_data: Optional[Dict[str, Any]] = None
    default_requirements: Optional[Dict[str, Any]] = None
    evaluation_criteria_template: Optional[Dict[str, Any]] = None
    description_template: Optional[str] = None
    requirements_template: Optional[str] = None
    is_active: Optional[bool] = None


class RFPTemplateResponse(RFPTemplateBase, UUIDMixin, TimestampMixin):
    """RFP template response schema"""
    id: int
    is_system_template: bool
    usage_count: int
    created_at: datetime
    updated_at: datetime
    created_by_id: int
    organization_id: Optional[int]
    
    class Config:
        from_attributes = True


# Enhanced RFP Schemas
class RFPEnhancedBase(BaseModel):
    """Base enhanced RFP schema"""
    title: str = Field(..., max_length=300)
    description: Optional[str] = None
    description_html: Optional[str] = None
    rfp_number: str = Field(..., max_length=100)
    rfp_type: RFPTypeEnum
    category: Optional[str] = Field(None, max_length=100)
    
    # Dates
    issue_date: date
    submission_deadline: datetime
    publication_date: Optional[datetime] = None
    clarification_deadline: Optional[datetime] = None
    
    # Financial
    estimated_budget: Optional[float] = Field(None, ge=0)
    budget_range_min: Optional[float] = Field(None, ge=0)
    budget_range_max: Optional[float] = Field(None, ge=0)
    currency: str = Field(default="USD", max_length=3)
    
    # Content
    requirements: Dict[str, Any] = Field(default_factory=dict)
    requirements_html: Optional[str] = None
    evaluation_criteria: Dict[str, Any] = Field(default_factory=dict)
    
    # Contact
    contact_person: Optional[str] = Field(None, max_length=200)
    contact_email: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=50)
    
    # Settings
    is_public: bool = False
    internal_notes: Optional[str] = None
    
    @validator('budget_range_max')
    def validate_budget_range(cls, v, values):
        """Ensure max budget is greater than min budget"""
        if v is not None and 'budget_range_min' in values and values['budget_range_min'] is not None:
            if v < values['budget_range_min']:
                raise ValueError('Maximum budget must be greater than minimum budget')
        return v
    
    @validator('submission_deadline')
    def validate_submission_deadline(cls, v, values):
        """Ensure submission deadline is in the future"""
        if v and v <= datetime.utcnow():
            raise ValueError('Submission deadline must be in the future')
        return v


class RFPEnhancedCreate(RFPEnhancedBase):
    """Create enhanced RFP schema"""
    template_id: Optional[int] = None


class RFPEnhancedUpdate(BaseModel):
    """Update enhanced RFP schema"""
    title: Optional[str] = Field(None, max_length=300)
    description: Optional[str] = None
    description_html: Optional[str] = None
    rfp_type: Optional[RFPTypeEnum] = None
    category: Optional[str] = Field(None, max_length=100)
    
    # Dates
    submission_deadline: Optional[datetime] = None
    publication_date: Optional[datetime] = None
    clarification_deadline: Optional[datetime] = None
    
    # Financial
    estimated_budget: Optional[float] = Field(None, ge=0)
    budget_range_min: Optional[float] = Field(None, ge=0)
    budget_range_max: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=3)
    
    # Content
    requirements: Optional[Dict[str, Any]] = None
    requirements_html: Optional[str] = None
    evaluation_criteria: Optional[Dict[str, Any]] = None
    
    # Contact
    contact_person: Optional[str] = Field(None, max_length=200)
    contact_email: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=50)
    
    # Settings
    is_public: Optional[bool] = None
    internal_notes: Optional[str] = None
    status: Optional[RFPStatusEnum] = None


class RFPEnhancedResponse(RFPEnhancedBase, UUIDMixin, TimestampMixin):
    """Enhanced RFP response schema"""
    id: int
    status: RFPStatusEnum
    is_active: bool
    is_template_based: bool
    template_id: Optional[int]
    
    # Statistics
    view_count: int
    download_count: int
    document_count: int
    public_document_count: int
    
    # Computed fields
    days_until_deadline: int
    hours_until_deadline: int
    is_open: bool
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    organization_id: int
    created_by_id: int
    
    # Documents (optional, can be loaded separately)
    documents: Optional[List[RFPDocumentResponse]] = None
    
    class Config:
        from_attributes = True


# Status Update Schema
class RFPStatusUpdate(BaseModel):
    """RFP status update schema"""
    status: RFPStatusEnum
    notes: Optional[str] = None


# Search and Filter Schemas
class RFPSearchParams(BaseModel):
    """RFP search parameters"""
    query: Optional[str] = None  # Full-text search
    status: Optional[List[RFPStatusEnum]] = None
    rfp_type: Optional[List[RFPTypeEnum]] = None
    category: Optional[List[str]] = None
    budget_min: Optional[float] = Field(None, ge=0)
    budget_max: Optional[float] = Field(None, ge=0)
    deadline_from: Optional[date] = None
    deadline_to: Optional[date] = None
    is_public: Optional[bool] = None
    created_by: Optional[List[int]] = None
    
    # Pagination
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1, le=100)
    
    # Sorting
    sort_by: Optional[str] = Field(default="created_at", pattern="^(created_at|updated_at|submission_deadline|title|estimated_budget)$")
    sort_order: Optional[str] = Field(default="desc", pattern="^(asc|desc)$")


class RFPExportRequest(BaseModel):
    """RFP export request schema"""
    format: str = Field(default="pdf", pattern="^(pdf|docx|html)$")
    include_documents: bool = False
    include_internal_notes: bool = False


# Statistics Schema
class RFPStatistics(BaseModel):
    """RFP statistics response"""
    total_rfps: int
    rfps_by_status: Dict[str, int]
    rfps_by_type: Dict[str, int]
    total_budget: float
    average_budget: float
    upcoming_deadlines: int  # Count of RFPs with deadlines in next 7 days
    recent_activity_count: int  # Count of RFPs created/updated in last 30 days