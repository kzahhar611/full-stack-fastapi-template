"""
Enhanced RFP models for Release 5 with document management and templates
"""
from typing import Optional, List
from datetime import datetime, date
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text, Enum as SQLEnum, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from .types import get_json_type
import uuid
import enum

from .base import Base


class RFPStatus(enum.Enum):
    """RFP status"""
    DRAFT = "draft"
    PUBLISHED = "published"
    OPEN = "open"
    CLOSED = "closed"
    AWARDED = "awarded"
    CANCELLED = "cancelled"


class RFPType(enum.Enum):
    """RFP types"""
    GOODS = "goods"
    SERVICES = "services"
    CONSTRUCTION = "construction"
    CONSULTING = "consulting"
    TECHNOLOGY = "technology"
    OTHER = "other"


class DocumentType(enum.Enum):
    """Document types for RFPs"""
    SPECIFICATION = "specification"
    ATTACHMENT = "attachment"
    TEMPLATE = "template"
    PROPOSAL = "proposal"
    EVALUATION = "evaluation"
    CONTRACT = "contract"
    OTHER = "other"


class RFPDocument(Base):
    """RFP Document model for file management"""
    
    __tablename__ = "rfp_documents"
    
    # Basic Information
    uuid: Mapped[str] = mapped_column(UUID(as_uuid=False), default=lambda: str(uuid.uuid4()), unique=True, nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Classification
    document_type: Mapped[DocumentType] = mapped_column(SQLEnum(DocumentType), default=DocumentType.ATTACHMENT, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Security & Access
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Timestamps
    upload_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    rfp_id: Mapped[int] = mapped_column(ForeignKey("rfps_enhanced.id"), nullable=False)
    rfp: Mapped["RFPEnhanced"] = relationship("RFPEnhanced", back_populates="documents")
    
    uploaded_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    uploaded_by: Mapped["User"] = relationship("User")
    
    def __repr__(self):
        return f"<RFPDocument(filename='{self.filename}', type='{self.document_type.value}')>"


class RFPTemplate(Base):
    """RFP Template model for standardized RFP creation"""
    
    __tablename__ = "rfp_templates"
    
    # Basic Information
    uuid: Mapped[str] = mapped_column(UUID(as_uuid=False), default=lambda: str(uuid.uuid4()), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Classification
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # Services, Goods, Construction, etc.
    rfp_type: Mapped[RFPType] = mapped_column(SQLEnum(RFPType), nullable=False)
    
    # Template Data
    template_data: Mapped[dict] = mapped_column(get_json_type(), default={}, nullable=False)  # Form structure and defaults
    default_requirements: Mapped[dict] = mapped_column(get_json_type(), default={}, nullable=False)
    evaluation_criteria_template: Mapped[dict] = mapped_column(get_json_type(), default={}, nullable=False)
    
    # Content Templates
    description_template: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    requirements_template: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # System Fields
    is_system_template: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    usage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    organization_id: Mapped[Optional[int]] = mapped_column(ForeignKey("organizations.id"), nullable=True)  # None for system templates
    organization: Mapped[Optional["Organization"]] = relationship("Organization")
    
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_by: Mapped["User"] = relationship("User")
    
    # RFPs created from this template
    rfps: Mapped[List["RFPEnhanced"]] = relationship("RFPEnhanced", back_populates="template")
    
    def __repr__(self):
        return f"<RFPTemplate(name='{self.name}', category='{self.category}')>"


class RFPEnhanced(Base):
    """Enhanced RFP model with rich content and document management"""
    
    __tablename__ = "rfps_enhanced"
    
    # Basic Information
    uuid: Mapped[str] = mapped_column(UUID(as_uuid=False), default=lambda: str(uuid.uuid4()), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Plain text fallback
    description_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Rich HTML content
    rfp_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    
    # Classification
    rfp_type: Mapped[RFPType] = mapped_column(SQLEnum(RFPType), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Dates & Deadlines
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    submission_deadline: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    publication_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    clarification_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Financial Information
    estimated_budget: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    budget_range_min: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    budget_range_max: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    
    # Requirements & Evaluation
    requirements: Mapped[dict] = mapped_column(get_json_type(), default={}, nullable=False)
    requirements_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Rich HTML requirements
    evaluation_criteria: Mapped[dict] = mapped_column(get_json_type(), default={}, nullable=False)  # Scoring criteria
    
    # Contact Information
    contact_person: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # System Fields
    status: Mapped[RFPStatus] = mapped_column(SQLEnum(RFPStatus), default=RFPStatus.DRAFT, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Template & Workflow
    is_template_based: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    template_id: Mapped[Optional[int]] = mapped_column(ForeignKey("rfp_templates.id"), nullable=True)
    template: Mapped[Optional["RFPTemplate"]] = relationship("RFPTemplate", back_populates="rfps")
    
    # Internal Fields
    internal_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    workflow_data: Mapped[dict] = mapped_column(get_json_type(), default={}, nullable=False)
    
    # AI Analysis Results
    ai_analysis: Mapped[dict] = mapped_column(get_json_type(), default={}, nullable=False)
    
    # Statistics
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    download_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    organization: Mapped["Organization"] = relationship("Organization")
    
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by_id])
    
    # Document relationships
    documents: Mapped[List["RFPDocument"]] = relationship("RFPDocument", back_populates="rfp", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<RFPEnhanced(title='{self.title}', rfp_number='{self.rfp_number}')>"
    
    @property
    def is_open(self) -> bool:
        """Check if RFP is open for submissions"""
        return self.status in [RFPStatus.PUBLISHED, RFPStatus.OPEN]
    
    @property
    def days_until_deadline(self) -> int:
        """Calculate days until submission deadline"""
        if self.submission_deadline:
            delta = self.submission_deadline.date() - date.today()
            return delta.days
        return 0
    
    @property
    def hours_until_deadline(self) -> int:
        """Calculate hours until submission deadline"""
        if self.submission_deadline:
            delta = self.submission_deadline - datetime.utcnow()
            return int(delta.total_seconds() / 3600)
        return 0
    
    @property
    def document_count(self) -> int:
        """Get count of documents"""
        return len(self.documents) if self.documents else 0
    
    @property
    def public_document_count(self) -> int:
        """Get count of public documents"""
        return len([doc for doc in self.documents if doc.is_public]) if self.documents else 0