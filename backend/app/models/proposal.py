"""
Proposal models for RFP responses
"""
from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, Text, Enum, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import enum
from datetime import date

from .base import Base


class ProposalStatus(enum.Enum):
    """Proposal status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    SHORTLISTED = "shortlisted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class ProposalType(enum.Enum):
    """Proposal types"""
    TECHNICAL = "technical"
    COMMERCIAL = "commercial"
    COMBINED = "combined"


class ComplianceStatus(enum.Enum):
    """Compliance status"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NEEDS_CLARIFICATION = "needs_clarification"


class Proposal(Base):
    """Proposal model for RFP responses"""
    
    __tablename__ = "proposals"
    
    # Basic Information
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    title = Column(String(300), nullable=False)
    proposal_number = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Classification
    proposal_type = Column(Enum(ProposalType), default=ProposalType.COMBINED, nullable=False)
    
    # Vendor Information
    vendor_name = Column(String(200), nullable=False)
    vendor_contact_person = Column(String(200), nullable=True)
    vendor_email = Column(String(255), nullable=True)
    vendor_phone = Column(String(20), nullable=True)
    vendor_address = Column(Text, nullable=True)
    
    # Dates
    submission_date = Column(Date, nullable=False)
    validity_date = Column(Date, nullable=True)  # Proposal validity period
    
    # Financial Information
    total_cost = Column(Numeric(15, 2), nullable=True)
    currency = Column(String(3), default="USD", nullable=False)
    cost_breakdown = Column(JSONB, default={}, nullable=False)
    
    # Technical Information
    technical_approach = Column(Text, nullable=True)
    implementation_timeline = Column(JSONB, default={}, nullable=False)
    team_composition = Column(JSONB, default=[], nullable=False)
    
    # Compliance & Evaluation
    compliance_matrix = Column(JSONB, default={}, nullable=False)
    overall_compliance = Column(Enum(ComplianceStatus), nullable=True)
    evaluation_score = Column(Numeric(5, 2), nullable=True)  # 0.00 to 100.00
    
    # AI Analysis
    ai_analysis = Column(JSONB, default={}, nullable=False)
    risk_assessment = Column(JSONB, default={}, nullable=False)
    strengths = Column(JSONB, default=[], nullable=False)
    weaknesses = Column(JSONB, default=[], nullable=False)
    
    # System Fields
    status = Column(Enum(ProposalStatus), default=ProposalStatus.DRAFT, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Evaluation
    evaluator_notes = Column(Text, nullable=True)
    evaluation_date = Column(Date, nullable=True)
    
    # Relationships
    rfp_id = Column(Integer, ForeignKey("rfps.id"), nullable=False)
    rfp = relationship("RFP", back_populates="proposals")
    
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="proposals")
    
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    creator = relationship("User", back_populates="created_proposals", foreign_keys=[created_by_id])
    
    documents = relationship("ProposalDocument", back_populates="proposal", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Proposal(title='{self.title}', proposal_number='{self.proposal_number}')>"
    
    @property
    def is_submitted(self) -> bool:
        """Check if proposal is submitted"""
        return self.status != ProposalStatus.DRAFT
    
    @property
    def compliance_percentage(self) -> float:
        """Calculate compliance percentage"""
        if not self.compliance_matrix:
            return 0.0
        
        total_requirements = len(self.compliance_matrix)
        if total_requirements == 0:
            return 0.0
        
        compliant_count = sum(
            1 for status in self.compliance_matrix.values() 
            if status == ComplianceStatus.COMPLIANT.value
        )
        
        return (compliant_count / total_requirements) * 100
    
    @property
    def document_count(self) -> int:
        """Get number of documents in the proposal"""
        return len(self.documents)


class ProposalDocument(Base):
    """Proposal related documents"""
    
    __tablename__ = "proposal_documents"
    
    # Basic Information
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    mime_type = Column(String(100), nullable=False)
    
    # Document Information
    document_type = Column(String(50), nullable=False)  # technical, commercial, supporting
    title = Column(String(300), nullable=True)
    description = Column(Text, nullable=True)
    section = Column(String(100), nullable=True)  # Which section this document belongs to
    
    # Processing
    is_processed = Column(Boolean, default=False, nullable=False)
    extracted_text = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)
    key_points = Column(JSONB, default=[], nullable=False)
    metadata = Column(JSONB, default={}, nullable=False)
    
    # Relationships
    proposal_id = Column(Integer, ForeignKey("proposals.id"), nullable=False)
    proposal = relationship("Proposal", back_populates="documents")
    
    def __repr__(self):
        return f"<ProposalDocument(filename='{self.filename}', type='{self.document_type}')>"