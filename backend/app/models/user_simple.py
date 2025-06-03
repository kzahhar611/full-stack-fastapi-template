"""
User model with organization support (SQLAlchemy 2.0)
"""
from typing import Optional, List
from sqlalchemy import Boolean, String, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from .types import get_json_type
import uuid
import enum

from .base import Base


class UserRole(enum.Enum):
    """User roles in the system"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    VIEWER = "viewer"


class UserStatus(enum.Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class User(Base):
    """User model with organization support"""
    
    __tablename__ = "users"
    
    # Basic Information
    uuid: Mapped[str] = mapped_column(UUID(as_uuid=False), default=lambda: str(uuid.uuid4()), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)
    
    # Profile Information
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)  # en, ar
    
    # System Fields
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    status: Mapped[UserStatus] = mapped_column(SQLEnum(UserStatus), default=UserStatus.PENDING, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Organization relationship
    organization_id: Mapped[Optional[int]] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    organization: Mapped[Optional["Organization"]] = relationship("Organization", back_populates="users")
    
    # Authentication
    last_login: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    password_reset_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email_verification_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Preferences (JSON field for flexible user preferences)
    preferences: Mapped[dict] = mapped_column(get_json_type(), default={}, nullable=False)
    
    # Relationships
    created_rfps: Mapped[List["RFP"]] = relationship("RFP", back_populates="creator", foreign_keys="RFP.created_by_id")
    
    def __repr__(self):
        return f"<User(email='{self.email}', role='{self.role}')>"
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def is_admin(self) -> bool:
        """Check if user has admin privileges"""
        return self.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]