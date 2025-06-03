"""
TenderWise AI - Proposal Models
"""

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, JSON, ForeignKey, Enum, Numeric
from sqlalchemy.orm import relationship
from core.database import Base
import enum


class ProposalStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    UNDER_REVIEW = "under_review"
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class Proposal(Base):
    """Proposal model for responses to RFPs"""
    
    __tablename__ = "proposals"

    id = Column(Integer, primary_key=True, index=True)
    rfp_id = Column(Integer, ForeignKey("rfps.id"), nullable=False)
    title = Column(String(500), nullable=False)
    proposal_number = Column(String(100), unique=True, nullable=False, index=True)
    
    # Proposal Details
    status = Column(Enum(ProposalStatus), default=ProposalStatus.DRAFT, index=True)
    executive_summary = Column(Text, nullable=True)
    technical_approach = Column(Text, nullable=True)
    
    # Financial Information
    total_cost = Column(Numeric(15, 2), nullable=True)
    currency = Column(String(3), default="USD")
    cost_breakdown = Column(JSON, nullable=True)
    
    # Timeline
    proposed_timeline = Column(JSON, nullable=True)
    delivery_date = Column(DateTime, nullable=True)
    
    # Compliance and Evaluation
    compliance_matrix = Column(JSON, nullable=True)
    compliance_score = Column(Numeric(5, 2), nullable=True)  # Percentage
    evaluation_results = Column(JSON, nullable=True)
    
    # AI Analysis
    strengths = Column(JSON, nullable=True)
    weaknesses = Column(JSON, nullable=True)
    risk_factors = Column(JSON, nullable=True)
    recommendation = Column(String(50), nullable=True)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    submitted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    # rfp = relationship("RFP", back_populates="proposals")
    # creator = relationship("User", back_populates="proposals")
    documents = relationship("ProposalDocument", back_populates="proposal", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Proposal(id={self.id}, title='{self.title}', status='{self.status}')>"


class ProposalDocument(Base):
    """Proposal Document attachments"""
    
    __tablename__ = "proposal_documents"

    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, ForeignKey("proposals.id"), nullable=False)
    
    # Document Information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String(100), nullable=False)
    
    # Document Processing
    extracted_text = Column(Text, nullable=True)
    document_type = Column(String(50), nullable=True)
    processing_status = Column(String(50), default="pending")
    
    # Metadata
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    proposal = relationship("Proposal", back_populates="documents")
    # uploader = relationship("User")

    def __repr__(self):
        return f"<ProposalDocument(id={self.id}, filename='{self.filename}', proposal_id={self.proposal_id})>"