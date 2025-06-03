"""
RFP (Request for Proposal) models (SQLAlchemy 2.0)
"""
from typing import Optional, List
from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text, Enum as SQLEnum, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import enum
from datetime import date

from .base import Base


class RFPStatus(enum.Enum):
    """RFP status"""
    DRAFT = "draft"
    PUBLISHED = "published"
    OPEN = "open"
    CLOSED = "closed"
    EVALUATION = "evaluation"
    AWARDED = "awarded"
    CANCELLED = "cancelled"


class RFPType(enum.Enum):
    """RFP types"""
    GOODS = "goods"
    SERVICES = "services"
    CONSTRUCTION = "construction"
    CONSULTING = "consulting"
    TECHNOLOGY = "technology"
    MAINTENANCE = "maintenance"
    OTHER = "other"


class RFPCategory(enum.Enum):
    """RFP categories"""
    IT_SOFTWARE = "it_software"
    IT_HARDWARE = "it_hardware"
    CONSULTING = "consulting"
    CONSTRUCTION = "construction"
    PROFESSIONAL_SERVICES = "professional_services"
    SUPPLIES = "supplies"
    EQUIPMENT = "equipment"
    MAINTENANCE = "maintenance"
    TRAINING = "training"
    OTHER = "other"


class RFP(Base):
    """RFP (Request for Proposal) model"""
    
    __tablename__ = "rfps"
    
    # Basic Information
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    title = Column(String(300), nullable=False, index=True)
    description = Column(Text, nullable=True)
    rfp_number = Column(String(100), unique=True, nullable=False, index=True)
    
    # Classification
    rfp_type = Column(Enum(RFPType), nullable=False)
    category = Column(Enum(RFPCategory), nullable=False)
    industry = Column(String(100), nullable=True)
    
    # Dates
    issue_date = Column(Date, nullable=False)
    submission_deadline = Column(Date, nullable=False)
    opening_date = Column(Date, nullable=True)
    award_date = Column(Date, nullable=True)
    
    # Financial
    estimated_budget = Column(Numeric(15, 2), nullable=True)
    currency = Column(String(3), default="USD", nullable=False)  # ISO currency code
    
    # Requirements
    minimum_requirements = Column(JSONB, default=[], nullable=False)
    evaluation_criteria = Column(JSONB, default=[], nullable=False)
    technical_requirements = Column(Text, nullable=True)
    commercial_requirements = Column(Text, nullable=True)
    
    # Contact Information
    contact_person = Column(String(200), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    
    # System Fields
    status = Column(Enum(RFPStatus), default=RFPStatus.DRAFT, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)
    
    # AI Analysis Results
    ai_analysis = Column(JSONB, default={}, nullable=False)
    complexity_score = Column(Numeric(3, 2), nullable=True)  # 0.00 to 1.00
    
    # Relationships
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="rfps")
    
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    creator = relationship("User", back_populates="created_rfps", foreign_keys=[created_by_id])
    
    documents = relationship("RFPDocument", back_populates="rfp", cascade="all, delete-orphan")
    proposals = relationship("Proposal", back_populates="rfp")
    
    def __repr__(self):
        return f"<RFP(title='{self.title}', rfp_number='{self.rfp_number}')>"
    
    @property
    def is_open(self) -> bool:
        """Check if RFP is open for submissions"""
        return self.status in [RFPStatus.PUBLISHED, RFPStatus.OPEN]
    
    @property
    def days_until_deadline(self) -> int:
        """Calculate days until submission deadline"""
        from datetime import date
        if self.submission_deadline:
            delta = self.submission_deadline - date.today()
            return delta.days
        return 0
    
    @property
    def proposal_count(self) -> int:
        """Get number of proposals submitted"""
        return len(self.proposals)


class RFPDocument(Base):
    """RFP related documents"""
    
    __tablename__ = "rfp_documents"
    
    # Basic Information
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    mime_type = Column(String(100), nullable=False)
    
    # Document Information
    document_type = Column(String(50), nullable=False)  # rfp_document, amendment, clarification
    title = Column(String(300), nullable=True)
    description = Column(Text, nullable=True)
    version = Column(String(20), default="1.0", nullable=False)
    
    # Processing
    is_processed = Column(Boolean, default=False, nullable=False)
    extracted_text = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)
    metadata = Column(JSONB, default={}, nullable=False)
    
    # Relationships
    rfp_id = Column(Integer, ForeignKey("rfps.id"), nullable=False)
    rfp = relationship("RFP", back_populates="documents")
    
    def __repr__(self):
        return f"<RFPDocument(filename='{self.filename}', type='{self.document_type}')>"