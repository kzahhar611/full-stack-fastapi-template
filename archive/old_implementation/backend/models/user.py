"""
TenderWise AI - User Model
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, JSON
from sqlalchemy.orm import relationship
from core.database import Base


class User(Base):
    """User model for authentication and authorization"""
    
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    
    # User status and permissions
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    # Profile information
    phone = Column(String(50), nullable=True)
    organization = Column(String(255), nullable=True)
    position = Column(String(255), nullable=True)
    department = Column(String(255), nullable=True)
    
    # Preferences
    language = Column(String(10), default="en")
    timezone = Column(String(50), default="UTC")
    preferences = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    # projects = relationship("Project", back_populates="owner")
    # tasks = relationship("Task", back_populates="assignee")
    # rfps = relationship("RFP", back_populates="creator")
    # proposals = relationship("Proposal", back_populates="creator")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', full_name='{self.full_name}')>"