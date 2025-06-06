"""
Compliance Analysis Models for TenderWise AI Platform
Module 2: Proposal Compliance & Vendor Assessment

Database models for compliance matrix, vendor scoring, and gap analysis.
"""

from sqlalchemy import Column, String, Text, Integer, Float, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from typing import Optional, List, Dict, Any
import uuid

from ..core.database import Base


class AnalysisStatus(PyEnum):
    """Analysis processing status"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class RequirementType(PyEnum):
    """Requirement categorization types"""
    TECHNICAL = "TECHNICAL"
    FUNCTIONAL = "FUNCTIONAL"
    COMMERCIAL = "COMMERCIAL"
    LEGAL = "LEGAL"
    OPERATIONAL = "OPERATIONAL"


class PriorityLevel(PyEnum):
    """Requirement priority levels"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ComplianceStatus(PyEnum):
    """Compliance assessment status"""
    COMPLIANT = "COMPLIANT"           # 80-100%: Fully addresses requirement
    PARTIAL = "PARTIAL"               # 40-79%: Partially addresses requirement
    NON_COMPLIANT = "NON_COMPLIANT"   # 1-39%: Inadequately addresses requirement
    NOT_ADDRESSED = "NOT_ADDRESSED"   # 0%: No mention or addressing


class ComplianceAnalysis(Base):
    """
    Main compliance analysis record
    Tracks overall analysis of RFP requirements vs vendor proposals
    """
    __tablename__ = "compliance_analyses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=True)
    
    # RFP Document Information
    rfp_document_name = Column(String(255), nullable=False)
    rfp_content = Column(Text, nullable=False)
    rfp_metadata = Column(JSON, nullable=True)
    
    # Analysis Status and Progress
    analysis_status = Column(Enum(AnalysisStatus), default=AnalysisStatus.PENDING, nullable=False)
    processing_progress = Column(Float, default=0.0)  # 0-100 percentage
    
    # Analysis Summary
    total_requirements = Column(Integer, default=0)
    total_proposals = Column(Integer, default=0)
    analysis_results = Column(JSON, nullable=True)  # Summary results and insights
    
    # Processing Metadata
    processing_time_seconds = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships (commented out to avoid model conflicts)
    # user = relationship("User", back_populates="compliance_analyses")
    # organization = relationship("Organization", back_populates="compliance_analyses")
    requirements = relationship("RFPRequirement", back_populates="compliance_analysis", cascade="all, delete-orphan")
    proposals = relationship("VendorProposal", back_populates="compliance_analysis", cascade="all, delete-orphan")
    compliance_matrix = relationship("ComplianceMatrix", back_populates="compliance_analysis", cascade="all, delete-orphan")
    compliance_scores = relationship("ComplianceScore", back_populates="compliance_analysis", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ComplianceAnalysis(id={self.id}, rfp_document={self.rfp_document_name}, status={self.analysis_status})>"


class RFPRequirement(Base):
    """
    Individual requirements extracted from RFP document
    Each requirement represents a specific need that vendors must address
    """
    __tablename__ = "rfp_requirements"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    compliance_analysis_id = Column(String, ForeignKey("compliance_analyses.id"), nullable=False)
    
    # Requirement Content
    requirement_text = Column(Text, nullable=False)
    requirement_summary = Column(String(500), nullable=True)
    requirement_category = Column(String(100), nullable=True)
    
    # Requirement Classification
    requirement_type = Column(Enum(RequirementType), default=RequirementType.FUNCTIONAL, nullable=False)
    priority_level = Column(Enum(PriorityLevel), default=PriorityLevel.MEDIUM, nullable=False)
    
    # Requirement Metadata
    section_reference = Column(String(255), nullable=True)  # RFP section where found
    page_number = Column(Integer, nullable=True)
    weight = Column(Float, default=1.0)  # Importance weight (0-1)
    
    # Processing Information
    extraction_confidence = Column(Float, nullable=True)  # AI extraction confidence
    keywords = Column(JSON, nullable=True)  # Key terms for matching
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    compliance_analysis = relationship("ComplianceAnalysis", back_populates="requirements")
    compliance_matrix = relationship("ComplianceMatrix", back_populates="requirement")

    def __repr__(self):
        return f"<RFPRequirement(id={self.id}, type={self.requirement_type}, priority={self.priority_level})>"


class VendorProposal(Base):
    """
    Vendor proposal submissions for compliance analysis
    Contains proposal content and vendor information
    """
    __tablename__ = "vendor_proposals"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    compliance_analysis_id = Column(String, ForeignKey("compliance_analyses.id"), nullable=False)
    
    # Vendor Information
    vendor_name = Column(String(255), nullable=False)
    vendor_company = Column(String(255), nullable=True)
    vendor_email = Column(String(255), nullable=True)
    
    # Document Information
    document_name = Column(String(255), nullable=False)
    document_size_bytes = Column(Integer, nullable=True)
    document_type = Column(String(50), nullable=True)  # PDF, DOCX, etc.
    
    # Proposal Content
    proposal_content = Column(Text, nullable=False)
    content_sections = Column(JSON, nullable=True)  # Extracted sections
    
    # Submission Information
    submission_date = Column(DateTime(timezone=True), nullable=True)
    proposal_metadata = Column(JSON, nullable=True)  # Additional proposal metadata
    
    # Processing Information
    extraction_confidence = Column(Float, nullable=True)
    word_count = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    compliance_analysis = relationship("ComplianceAnalysis", back_populates="proposals")
    compliance_matrix = relationship("ComplianceMatrix", back_populates="proposal")
    compliance_scores = relationship("ComplianceScore", back_populates="proposal")

    def __repr__(self):
        return f"<VendorProposal(id={self.id}, vendor={self.vendor_name}, document={self.document_name})>"


class ComplianceMatrix(Base):
    """
    Compliance matrix mapping requirements to vendor proposals
    Each record represents how well a vendor addresses a specific requirement
    """
    __tablename__ = "compliance_matrix"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    compliance_analysis_id = Column(String, ForeignKey("compliance_analyses.id"), nullable=False)
    requirement_id = Column(String, ForeignKey("rfp_requirements.id"), nullable=False)
    proposal_id = Column(String, ForeignKey("vendor_proposals.id"), nullable=False)
    
    # Compliance Assessment
    compliance_status = Column(Enum(ComplianceStatus), nullable=False)
    compliance_score = Column(Float, nullable=False)  # 0-100 percentage
    confidence_level = Column(Float, nullable=True)   # AI confidence in assessment
    
    # Evidence and Analysis
    evidence_text = Column(Text, nullable=True)       # Text from proposal addressing requirement
    gap_description = Column(Text, nullable=True)     # Description of gaps or shortcomings
    recommendations = Column(Text, nullable=True)     # Recommendations for improvement
    
    # Detailed Scoring
    technical_relevance = Column(Float, nullable=True)    # How technically relevant (0-100)
    completeness_score = Column(Float, nullable=True)     # How complete the response (0-100)
    clarity_score = Column(Float, nullable=True)          # How clear the response (0-100)
    
    # Analysis Metadata
    analysis_method = Column(String(100), nullable=True)  # Method used for analysis
    keywords_matched = Column(JSON, nullable=True)        # Keywords that matched
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    compliance_analysis = relationship("ComplianceAnalysis", back_populates="compliance_matrix")
    requirement = relationship("RFPRequirement", back_populates="compliance_matrix")
    proposal = relationship("VendorProposal", back_populates="compliance_matrix")

    def __repr__(self):
        return f"<ComplianceMatrix(id={self.id}, status={self.compliance_status}, score={self.compliance_score})>"


class ComplianceScore(Base):
    """
    Overall compliance scores and rankings for each vendor proposal
    Aggregated scoring across all requirements
    """
    __tablename__ = "compliance_scores"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    compliance_analysis_id = Column(String, ForeignKey("compliance_analyses.id"), nullable=False)
    proposal_id = Column(String, ForeignKey("vendor_proposals.id"), nullable=False)
    
    # Overall Scoring
    overall_score = Column(Float, nullable=False)      # 0-100 overall compliance score
    weighted_score = Column(Float, nullable=True)      # Score adjusted by requirement weights
    rank_position = Column(Integer, nullable=True)     # Ranking among all vendors (1=best)
    
    # Category Scores
    technical_score = Column(Float, nullable=True)     # Technical requirement compliance
    functional_score = Column(Float, nullable=True)    # Functional requirement compliance
    commercial_score = Column(Float, nullable=True)    # Commercial requirement compliance
    legal_score = Column(Float, nullable=True)         # Legal requirement compliance
    operational_score = Column(Float, nullable=True)   # Operational requirement compliance
    
    # Compliance Distribution
    total_requirements = Column(Integer, default=0)
    total_compliant = Column(Integer, default=0)       # COMPLIANT status count
    total_partial = Column(Integer, default=0)         # PARTIAL status count
    total_non_compliant = Column(Integer, default=0)   # NON_COMPLIANT status count
    total_not_addressed = Column(Integer, default=0)   # NOT_ADDRESSED status count
    
    # Analysis Insights
    strength_areas = Column(JSON, nullable=True)       # Areas where vendor excels
    weakness_areas = Column(JSON, nullable=True)       # Areas needing improvement
    risk_factors = Column(JSON, nullable=True)         # Identified risks
    recommendations = Column(JSON, nullable=True)      # Overall recommendations
    
    # Scoring Metadata
    calculation_method = Column(String(100), nullable=True)
    last_calculated = Column(DateTime(timezone=True), server_default=func.now())
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    compliance_analysis = relationship("ComplianceAnalysis", back_populates="compliance_scores")
    proposal = relationship("VendorProposal", back_populates="compliance_scores")

    def __repr__(self):
        return f"<ComplianceScore(id={self.id}, overall_score={self.overall_score}, rank={self.rank_position})>"


# Add relationships to existing models
def add_compliance_relationships():
    """
    Function to add compliance analysis relationships to existing User and Organization models
    This should be called after importing existing models
    """
    from .user import User
    from .organization import Organization
    
    # Add relationship to User model
    if not hasattr(User, 'compliance_analyses'):
        User.compliance_analyses = relationship("ComplianceAnalysis", back_populates="user")
    
    # Add relationship to Organization model  
    if not hasattr(Organization, 'compliance_analyses'):
        Organization.compliance_analyses = relationship("ComplianceAnalysis", back_populates="organization")