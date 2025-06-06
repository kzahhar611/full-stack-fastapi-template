"""
Organization model for multi-tenant architecture (SQLAlchemy 2.0)
"""
from typing import Optional, List
from sqlalchemy import Boolean, String, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import JSON
from .types import get_json_type
import uuid
import enum

from .base import Base


class OrganizationType(enum.Enum):
    """Organization types"""
    GOVERNMENT = "government"
    PRIVATE = "private"
    NON_PROFIT = "non_profit"
    EDUCATION = "education"
    HEALTHCARE = "healthcare"
    TECHNOLOGY = "technology"
    CONSULTING = "consulting"
    OTHER = "other"


class OrganizationStatus(enum.Enum):
    """Organization status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    TRIAL = "trial"


class SubscriptionTier(enum.Enum):
    """Subscription tiers"""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class Organization(Base):
    """Organization model for multi-tenant architecture"""
    
    __tablename__ = "organizations"
    
    # Basic Information
    uuid: Mapped[str] = mapped_column(UUID(as_uuid=False), default=lambda: str(uuid.uuid4()), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Contact Information
    website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Address
    address_line1: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    address_line2: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Organization Details
    organization_type: Mapped[OrganizationType] = mapped_column(SQLEnum(OrganizationType), nullable=False)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    size: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Small, Medium, Large, Enterprise
    
    # System Fields
    status: Mapped[OrganizationStatus] = mapped_column(SQLEnum(OrganizationStatus), default=OrganizationStatus.TRIAL, nullable=False)
    subscription_tier: Mapped[SubscriptionTier] = mapped_column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Branding
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    primary_color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)  # Hex color
    secondary_color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    
    # Configuration (JSON field for flexible organization settings)
    settings: Mapped[dict] = mapped_column(get_json_type(), default={}, nullable=False)
    
    # Relationships
    users: Mapped[List["User"]] = relationship("User", back_populates="organization")
    rfps: Mapped[List["RFP"]] = relationship("RFP", back_populates="organization")
    
    # Module 1 relationships
    rfp_analyses: Mapped[List["RFPAnalysis"]] = relationship("RFPAnalysis", back_populates="organization")
    analysis_templates: Mapped[List["AnalysisTemplate"]] = relationship("AnalysisTemplate", back_populates="organization")
    
    def __repr__(self):
        return f"<Organization(name='{self.name}', slug='{self.slug}')>"

    
    @property
    def is_premium(self) -> bool:
        """Check if organization has premium features"""
        return self.subscription_tier in [SubscriptionTier.PROFESSIONAL, SubscriptionTier.ENTERPRISE]
    
    def get_setting(self, key: str, default=None):
        """Get a specific setting value"""
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value):
        """Set a specific setting value"""
        if self.settings is None:
            self.settings = {}
        self.settings[key] = value