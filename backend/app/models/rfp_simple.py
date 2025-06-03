"""
Simplified RFP model for Release 2 (SQLAlchemy 2.0)
"""
from typing import Optional, List
from sqlalchemy import Boolean, Date, ForeignKey, String, Text, Enum as SQLEnum, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from .types import get_json_type
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


class RFP(Base):
    """Simplified RFP (Request for Proposal) model"""
    
    __tablename__ = "rfps"
    
    # Basic Information
    uuid: Mapped[str] = mapped_column(UUID(as_uuid=False), default=lambda: str(uuid.uuid4()), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rfp_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    
    # Classification
    rfp_type: Mapped[RFPType] = mapped_column(SQLEnum(RFPType), nullable=False)
    
    # Dates
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    submission_deadline: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Financial
    estimated_budget: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    
    # Requirements
    requirements: Mapped[dict] = mapped_column(get_json_type(), default={}, nullable=False)
    
    # Contact Information
    contact_person: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # System Fields
    status: Mapped[RFPStatus] = mapped_column(SQLEnum(RFPStatus), default=RFPStatus.DRAFT, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # AI Analysis Results
    ai_analysis: Mapped[dict] = mapped_column(get_json_type(), default={}, nullable=False)
    
    # Relationships
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    organization: Mapped["Organization"] = relationship("Organization", back_populates="rfps")
    
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    creator: Mapped["User"] = relationship("User", back_populates="created_rfps", foreign_keys=[created_by_id])
    
    def __repr__(self):
        return f"<RFP(title='{self.title}', rfp_number='{self.rfp_number}')>"
    
    @property
    def is_open(self) -> bool:
        """Check if RFP is open for submissions"""
        return self.status in [RFPStatus.PUBLISHED, RFPStatus.OPEN]
    
    @property
    def days_until_deadline(self) -> int:
        """Calculate days until submission deadline"""
        if self.submission_deadline:
            delta = self.submission_deadline - date.today()
            return delta.days
        return 0