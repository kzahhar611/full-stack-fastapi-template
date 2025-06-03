"""
TenderWise AI - Project Model
"""

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from core.database import Base
import enum


class ProjectStatus(str, enum.Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Project(Base):
    """Project model for managing RFP/Proposal projects"""
    
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Project Details
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PLANNING, index=True)
    project_type = Column(String(50), nullable=True)  # rfp_response, rfp_creation, etc.
    
    # Timeline
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    
    # Relationships
    rfp_id = Column(Integer, ForeignKey("rfps.id"), nullable=True)
    proposal_id = Column(Integer, ForeignKey("proposals.id"), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    # owner = relationship("User", back_populates="projects")
    # rfp = relationship("RFP")
    # proposal = relationship("Proposal")

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', status='{self.status}')>"