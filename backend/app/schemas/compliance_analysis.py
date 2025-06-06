"""
Pydantic schemas for Compliance Analysis API
Module 2: Proposal Compliance & Vendor Assessment

Data validation and serialization schemas for compliance analysis endpoints.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

from ..models.compliance_analysis import AnalysisStatus, RequirementType, PriorityLevel, ComplianceStatus


class ComplianceAnalysisCreate(BaseModel):
    """Schema for creating a new compliance analysis"""
    rfp_document_name: str = Field(..., min_length=1, max_length=255)
    company_context: str = Field("", max_length=1000, description="Company context for analysis")
    analysis_name: str = Field("", max_length=255, description="Name for this analysis")
    
    class Config:
        from_attributes = True


class ComplianceAnalysisResponse(BaseModel):
    """Schema for compliance analysis response"""
    id: str
    rfp_document_name: str
    analysis_status: AnalysisStatus
    total_requirements: int = 0
    total_proposals: int = 0
    processing_progress: float = 0.0
    analysis_results: Optional[Dict[str, Any]] = None
    processing_time_seconds: Optional[float] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    message: Optional[str] = None  # For additional context in responses
    
    class Config:
        from_attributes = True


class RFPRequirementResponse(BaseModel):
    """Schema for RFP requirement response"""
    id: str
    requirement_text: str
    requirement_summary: Optional[str] = None
    requirement_category: Optional[str] = None
    requirement_type: RequirementType
    priority_level: PriorityLevel
    section_reference: Optional[str] = None
    weight: float = 1.0
    keywords: Optional[List[str]] = None
    extraction_confidence: Optional[float] = None
    
    class Config:
        from_attributes = True


class VendorProposalResponse(BaseModel):
    """Schema for vendor proposal response"""
    id: str
    vendor_name: str
    vendor_company: Optional[str] = None
    document_name: str
    document_size_bytes: Optional[int] = None
    document_type: Optional[str] = None
    submission_date: Optional[datetime] = None
    word_count: Optional[int] = None
    extraction_confidence: Optional[float] = None
    
    class Config:
        from_attributes = True


class ComplianceMatrixResponse(BaseModel):
    """Schema for compliance matrix entry response"""
    id: str
    requirement_id: str
    proposal_id: str
    requirement_text: str
    requirement_type: Optional[RequirementType] = None
    vendor_name: str
    compliance_status: ComplianceStatus
    compliance_score: float = Field(..., ge=0, le=100, description="Compliance score 0-100%")
    confidence_level: Optional[float] = Field(None, ge=0, le=1, description="AI confidence 0-1")
    evidence_text: Optional[str] = None
    gap_description: Optional[str] = None
    recommendations: Optional[str] = None
    keywords_matched: Optional[List[str]] = None
    technical_relevance: Optional[float] = Field(None, ge=0, le=100)
    completeness_score: Optional[float] = Field(None, ge=0, le=100)
    clarity_score: Optional[float] = Field(None, ge=0, le=100)
    
    class Config:
        from_attributes = True


class ComplianceScoreResponse(BaseModel):
    """Schema for compliance score response"""
    id: str
    proposal_id: str
    overall_score: float = Field(..., ge=0, le=100)
    weighted_score: Optional[float] = Field(None, ge=0, le=100)
    rank_position: Optional[int] = Field(None, ge=1)
    technical_score: Optional[float] = Field(None, ge=0, le=100)
    functional_score: Optional[float] = Field(None, ge=0, le=100)
    commercial_score: Optional[float] = Field(None, ge=0, le=100)
    legal_score: Optional[float] = Field(None, ge=0, le=100)
    operational_score: Optional[float] = Field(None, ge=0, le=100)
    total_requirements: int = 0
    total_compliant: int = 0
    total_partial: int = 0
    total_non_compliant: int = 0
    total_not_addressed: int = 0
    last_calculated: datetime
    
    class Config:
        from_attributes = True


class VendorRankingResponse(BaseModel):
    """Schema for vendor ranking response"""
    proposal_id: str
    vendor_name: str
    overall_score: float = Field(..., ge=0, le=100, description="Overall compliance score")
    rank_position: int = Field(..., ge=1, description="Ranking position (1=best)")
    category_scores: Dict[str, Optional[float]] = Field(
        default_factory=dict,
        description="Scores by requirement category"
    )
    compliance_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="Count of requirements by compliance status"
    )
    strengths: List[str] = Field(default_factory=list, description="Vendor strengths")
    weaknesses: List[str] = Field(default_factory=list, description="Areas for improvement")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    
    @validator('category_scores')
    def validate_category_scores(cls, v):
        """Validate category scores are within range"""
        for key, score in v.items():
            if score is not None and (score < 0 or score > 100):
                raise ValueError(f"Category score {key} must be between 0 and 100")
        return v
    
    @validator('compliance_distribution')
    def validate_compliance_distribution(cls, v):
        """Validate compliance distribution counts"""
        for key, count in v.items():
            if count < 0:
                raise ValueError(f"Compliance count {key} cannot be negative")
        return v
    
    class Config:
        from_attributes = True


class ComplianceStatisticsResponse(BaseModel):
    """Schema for compliance statistics response"""
    total_analyses: int = 0
    completed_analyses: int = 0
    processing_analyses: int = 0
    failed_analyses: int = 0
    total_requirements_analyzed: int = 0
    total_proposals_analyzed: int = 0
    recent_analyses: List[Dict[str, Any]] = Field(default_factory=list)
    
    @validator('*', pre=True)
    def ensure_non_negative(cls, v):
        """Ensure all counts are non-negative"""
        if isinstance(v, int) and v < 0:
            return 0
        return v
    
    class Config:
        from_attributes = True


class ComplianceGapAnalysisResponse(BaseModel):
    """Schema for gap analysis response"""
    analysis_id: str
    total_gaps: int = 0
    critical_gaps: int = 0
    moderate_gaps: int = 0
    minor_gaps: int = 0
    gaps_by_category: Dict[str, int] = Field(default_factory=dict)
    gaps_by_vendor: Dict[str, int] = Field(default_factory=dict)
    common_gaps: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class ComplianceUploadRequest(BaseModel):
    """Schema for upload request validation"""
    analysis_name: Optional[str] = Field(None, max_length=255)
    company_context: Optional[str] = Field(None, max_length=1000)
    max_proposals: int = Field(10, ge=1, le=20, description="Maximum number of proposals")
    
    class Config:
        from_attributes = True


class ComplianceAnalysisProgress(BaseModel):
    """Schema for analysis progress updates"""
    analysis_id: str
    status: AnalysisStatus
    progress: float = Field(..., ge=0, le=100, description="Progress percentage")
    current_step: str
    estimated_time_remaining: Optional[int] = Field(None, description="Seconds remaining")
    message: Optional[str] = None
    
    class Config:
        from_attributes = True


class ComplianceExportRequest(BaseModel):
    """Schema for export request"""
    analysis_id: str
    export_format: str = Field(..., pattern="^(html|pdf|pptx|xlsx)$")
    include_sections: List[str] = Field(
        default_factory=lambda: ["summary", "matrix", "rankings", "gaps"],
        description="Sections to include in export"
    )
    
    class Config:
        from_attributes = True


class ComplianceFilterRequest(BaseModel):
    """Schema for filtering compliance results"""
    vendor_names: Optional[List[str]] = None
    requirement_types: Optional[List[RequirementType]] = None
    compliance_statuses: Optional[List[ComplianceStatus]] = None
    min_score: Optional[float] = Field(None, ge=0, le=100)
    max_score: Optional[float] = Field(None, ge=0, le=100)
    priority_levels: Optional[List[PriorityLevel]] = None
    
    @validator('max_score')
    def validate_score_range(cls, v, values):
        """Validate max_score is greater than min_score"""
        if v is not None and 'min_score' in values and values['min_score'] is not None:
            if v < values['min_score']:
                raise ValueError('max_score must be greater than or equal to min_score')
        return v
    
    class Config:
        from_attributes = True


class ComplianceBenchmarkResponse(BaseModel):
    """Schema for compliance benchmarking"""
    analysis_id: str
    vendor_name: str
    industry_average: float = Field(..., ge=0, le=100)
    vendor_score: float = Field(..., ge=0, le=100)
    percentile_rank: float = Field(..., ge=0, le=100)
    category_benchmarks: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    improvement_areas: List[str] = Field(default_factory=list)
    competitive_position: str
    
    class Config:
        from_attributes = True


# Utility schemas for common operations
class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    detail: Optional[str] = None
    analysis_id: Optional[str] = None
    
    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    detail: str
    analysis_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        from_attributes = True


class ValidationErrorResponse(BaseModel):
    """Validation error response"""
    error: str = "Validation Error"
    detail: str
    field_errors: Dict[str, List[str]] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True