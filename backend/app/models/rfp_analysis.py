"""
RFP Analysis models for Module 1 - Strategic Decision Support
"""
from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, Text, Enum, Numeric, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from datetime import datetime

from .base import Base


class AnalysisStatus(enum.Enum):
    """Analysis status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class DecisionType(enum.Enum):
    """Go/No-Go decision types"""
    GO = "go"
    NO_GO = "no_go"
    CONDITIONAL = "conditional"
    NEEDS_REVIEW = "needs_review"


class RiskLevel(enum.Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RFPAnalysis(Base):
    """RFP Analysis results for strategic decision support"""
    
    __tablename__ = "rfp_analyses"
    
    # Basic Information
    uuid = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False, index=True)
    analysis_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Analysis Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    status = Column(Enum(AnalysisStatus), default=AnalysisStatus.PENDING, nullable=False)
    
    # Analysis Configuration
    company_context = Column(JSON, default={}, nullable=False)
    analysis_parameters = Column(JSON, default={}, nullable=False)
    
    # Go/No-Go Decision
    decision = Column(Enum(DecisionType), nullable=True)
    confidence_score = Column(Numeric(5, 4), nullable=True)  # 0.0000 to 1.0000
    primary_justification = Column(Text, nullable=True)
    detailed_reasoning = Column(JSON, default=[], nullable=False)
    risk_factors = Column(JSON, default=[], nullable=False)
    success_factors = Column(JSON, default=[], nullable=False)
    conditions = Column(JSON, default=[], nullable=False)
    estimated_win_probability = Column(Numeric(5, 4), nullable=True)
    
    # Risk Assessment
    overall_risk_level = Column(Enum(RiskLevel), nullable=True)
    risk_score = Column(Numeric(4, 2), nullable=True)  # 0.00 to 10.00
    technical_risks = Column(JSON, default=[], nullable=False)
    commercial_risks = Column(JSON, default=[], nullable=False)
    operational_risks = Column(JSON, default=[], nullable=False)
    legal_risks = Column(JSON, default=[], nullable=False)
    mitigation_strategies = Column(JSON, default=[], nullable=False)
    
    # Project Insights
    project_complexity = Column(String(20), nullable=True)  # low, medium, high, very_high
    estimated_duration_months = Column(Integer, nullable=True)
    estimated_cost_range = Column(JSON, default={}, nullable=False)
    technology_stack = Column(JSON, default=[], nullable=False)
    required_team_size = Column(Integer, nullable=True)
    key_success_factors = Column(JSON, default=[], nullable=False)
    competitive_advantages = Column(JSON, default=[], nullable=False)
    potential_challenges = Column(JSON, default=[], nullable=False)
    
    # KPI Dashboard Data
    kpi_dashboard = Column(JSON, default={}, nullable=False)
    strategic_score = Column(Numeric(5, 4), nullable=True)
    complexity_score = Column(Numeric(5, 4), nullable=True)
    
    # Raw Analysis Data
    raw_analysis = Column(JSON, default={}, nullable=False)
    strategic_analysis = Column(JSON, default={}, nullable=False)
    
    # Error Handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    
    # Processing Time
    analysis_duration_seconds = Column(Integer, nullable=True)
    
    # Relationships
    rfp_id = Column(Integer, ForeignKey("rfps.id"), nullable=False)
    rfp = relationship("RFP", back_populates="analyses")
    
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="rfp_analyses")
    
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    creator = relationship("User", back_populates="rfp_analyses")
    
    # Analysis history and comments
    decision_history = relationship("DecisionHistory", back_populates="analysis", cascade="all, delete-orphan")
    
    def to_dict(self) -> dict:
        """Convert analysis to dictionary"""
        return {
            "id": self.id,
            "uuid": str(self.uuid),
            "analysis_id": self.analysis_id,
            "rfp_id": self.rfp_id,
            "status": self.status.value if self.status else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            
            # Decision
            "decision": {
                "type": self.decision.value if self.decision else None,
                "confidence_score": float(self.confidence_score) if self.confidence_score else None,
                "primary_justification": self.primary_justification,
                "detailed_reasoning": self.detailed_reasoning,
                "risk_factors": self.risk_factors,
                "success_factors": self.success_factors,
                "conditions": self.conditions,
                "estimated_win_probability": float(self.estimated_win_probability) if self.estimated_win_probability else None
            },
            
            # Risk Assessment
            "risk_assessment": {
                "overall_risk_level": self.overall_risk_level.value if self.overall_risk_level else None,
                "risk_score": float(self.risk_score) if self.risk_score else None,
                "technical_risks": self.technical_risks,
                "commercial_risks": self.commercial_risks,
                "operational_risks": self.operational_risks,
                "legal_risks": self.legal_risks,
                "mitigation_strategies": self.mitigation_strategies
            },
            
            # Project Insights
            "project_insights": {
                "complexity": self.project_complexity,
                "estimated_duration_months": self.estimated_duration_months,
                "estimated_cost_range": self.estimated_cost_range,
                "technology_stack": self.technology_stack,
                "required_team_size": self.required_team_size,
                "key_success_factors": self.key_success_factors,
                "competitive_advantages": self.competitive_advantages,
                "potential_challenges": self.potential_challenges
            },
            
            # KPIs
            "kpi_dashboard": self.kpi_dashboard,
            "strategic_score": float(self.strategic_score) if self.strategic_score else None,
            "complexity_score": float(self.complexity_score) if self.complexity_score else None,
            
            # Metadata
            "analysis_duration_seconds": self.analysis_duration_seconds,
            "company_context": self.company_context,
            "error_message": self.error_message
        }


class DecisionHistory(Base):
    """History of decision changes and reviews"""
    
    __tablename__ = "decision_history"
    
    # Basic Information
    uuid = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False, index=True)
    
    # Decision Information
    previous_decision = Column(Enum(DecisionType), nullable=True)
    new_decision = Column(Enum(DecisionType), nullable=False)
    reason_for_change = Column(Text, nullable=False)
    reviewer_notes = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    analysis_id = Column(Integer, ForeignKey("rfp_analyses.id"), nullable=False)
    analysis = relationship("RFPAnalysis", back_populates="decision_history")
    
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reviewer = relationship("User", back_populates="decision_reviews")
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "uuid": str(self.uuid),
            "previous_decision": self.previous_decision.value if self.previous_decision else None,
            "new_decision": self.new_decision.value,
            "reason_for_change": self.reason_for_change,
            "reviewer_notes": self.reviewer_notes,
            "created_at": self.created_at.isoformat(),
            "reviewer_id": self.reviewer_id
        }


class AnalysisTemplate(Base):
    """Templates for analysis configuration"""
    
    __tablename__ = "analysis_templates"
    
    # Basic Information
    uuid = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Template Configuration
    industry = Column(String(100), nullable=True)
    company_size = Column(String(50), nullable=True)
    analysis_criteria = Column(JSON, default={}, nullable=False)
    risk_weights = Column(JSON, default={}, nullable=False)
    decision_thresholds = Column(JSON, default={}, nullable=False)
    
    # System Fields
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    usage_count = Column(Integer, default=0, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="analysis_templates")
    
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    creator = relationship("User", back_populates="analysis_templates")
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "uuid": str(self.uuid),
            "name": self.name,
            "description": self.description,
            "industry": self.industry,
            "company_size": self.company_size,
            "analysis_criteria": self.analysis_criteria,
            "risk_weights": self.risk_weights,
            "decision_thresholds": self.decision_thresholds,
            "is_active": self.is_active,
            "is_default": self.is_default,
            "usage_count": self.usage_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }