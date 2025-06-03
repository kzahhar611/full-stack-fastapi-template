"""
TenderWise AI - RFP Models
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, JSON, ForeignKey, Enum, Numeric
from sqlalchemy.orm import relationship
from core.database import Base
import enum


class RFPStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    UNDER_REVIEW = "under_review"
    CLOSED = "closed"
    AWARDED = "awarded"
    CANCELLED = "cancelled"


class RFPType(str, enum.Enum):
    REQUEST_FOR_PROPOSAL = "rfp"
    REQUEST_FOR_QUOTATION = "rfq"
    INVITATION_TO_BID = "itb"
    REQUEST_FOR_INFORMATION = "rfi"


class RFP(Base):
    """RFP (Request for Proposal) model"""
    
    __tablename__ = "rfps"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    rfp_number = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # RFP Details
    rfp_type = Column(Enum(RFPType), default=RFPType.REQUEST_FOR_PROPOSAL)
    status = Column(Enum(RFPStatus), default=RFPStatus.DRAFT, index=True)
    
    # Financial Information
    estimated_budget = Column(Numeric(15, 2), nullable=True)
    currency = Column(String(3), default="USD")
    
    # Timeline
    issue_date = Column(DateTime, nullable=True)
    submission_deadline = Column(DateTime, nullable=True)
    evaluation_period = Column(Integer, nullable=True)  # Days
    award_date = Column(DateTime, nullable=True)
    project_start_date = Column(DateTime, nullable=True)
    project_end_date = Column(DateTime, nullable=True)
    
    # Requirements and Criteria
    technical_requirements = Column(JSON, nullable=True)
    evaluation_criteria = Column(JSON, nullable=True)
    compliance_requirements = Column(JSON, nullable=True)
    
    # AI Analysis Results
    complexity_score = Column(Numeric(3, 2), nullable=True)  # 0.00 - 10.00
    risk_assessment = Column(JSON, nullable=True)
    go_no_go_recommendation = Column(String(50), nullable=True)
    ai_analysis_summary = Column(Text, nullable=True)
    key_insights = Column(JSON, nullable=True)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization = Column(String(255), nullable=True)
    contact_person = Column(String(255), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    # creator = relationship("User", back_populates="rfps")
    documents = relationship("RFPDocument", back_populates="rfp", cascade="all, delete-orphan")
    # proposals = relationship("Proposal", back_populates="rfp")

    def __repr__(self):
        return f"<RFP(id={self.id}, title='{self.title}', status='{self.status}')>"


class RFPDocument(Base):
    """RFP Document attachments"""
    
    __tablename__ = "rfp_documents"

    id = Column(Integer, primary_key=True, index=True)
    rfp_id = Column(Integer, ForeignKey("rfps.id"), nullable=False)
    
    # Document Information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String(100), nullable=False)
    
    # Document Processing
    extracted_text = Column(Text, nullable=True)
    document_type = Column(String(50), nullable=True)  # specifications, drawings, etc.
    processing_status = Column(String(50), default="pending")
    
    # Metadata
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    rfp = relationship("RFP", back_populates="documents")
    # uploader = relationship("User")

    def __repr__(self):
        return f"<RFPDocument(id={self.id}, filename='{self.filename}', rfp_id={self.rfp_id})>"