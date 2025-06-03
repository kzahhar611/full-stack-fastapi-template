"""
User model for authentication and user management
"""
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
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
    """User model for authentication and profile management"""
    
    __tablename__ = "users"
    
    # Basic Information
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    
    # Profile Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    display_name = Column(String(200), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    phone = Column(String(20), nullable=True)
    timezone = Column(String(50), default="UTC", nullable=False)
    language = Column(String(10), default="en", nullable=False)  # en, ar
    
    # System Fields
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Organization relationship
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    organization = relationship("Organization", back_populates="users")
    
    # Authentication
    last_login = Column(String(50), nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    email_verification_token = Column(String(255), nullable=True)
    
    # Preferences (JSON field for flexible user preferences)
    preferences = Column(JSONB, default={}, nullable=False)
    
    # Relationships
    created_rfps = relationship("RFP", back_populates="creator", foreign_keys="RFP.created_by_id")
    created_proposals = relationship("Proposal", back_populates="creator", foreign_keys="Proposal.created_by_id")
    workflows = relationship("Workflow", back_populates="creator")
    
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
    
    def to_dict(self) -> dict:
        """Convert to dictionary (excluding sensitive fields)"""
        data = super().to_dict()
        # Remove sensitive fields
        data.pop('hashed_password', None)
        data.pop('password_reset_token', None)
        data.pop('email_verification_token', None)
        return data