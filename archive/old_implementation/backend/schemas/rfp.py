"""
TenderWise AI - RFP Schemas
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field
from enum import Enum

from models.rfp import RFPStatus, RFPType

class RFPBase(BaseModel):
    """Base RFP schema"""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    rfp_type: RFPType = RFPType.REQUEST_FOR_PROPOSAL
    estimated_budget: Optional[Decimal] = None
    currency: str = "USD"
    submission_deadline: Optional[datetime] = None
    evaluation_period: Optional[int] = None  # Days
    project_start_date: Optional[datetime] = None
    project_end_date: Optional[datetime] = None
    technical_requirements: Optional[Dict[str, Any]] = None
    evaluation_criteria: Optional[Dict[str, Any]] = None
    compliance_requirements: Optional[Dict[str, Any]] = None
    organization: Optional[str] = None
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None

class RFPCreate(RFPBase):
    """RFP creation schema"""
    pass

class RFPUpdate(BaseModel):
    """RFP update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    rfp_type: Optional[RFPType] = None
    estimated_budget: Optional[Decimal] = None
    currency: Optional[str] = None
    submission_deadline: Optional[datetime] = None
    evaluation_period: Optional[int] = None
    project_start_date: Optional[datetime] = None
    project_end_date: Optional[datetime] = None
    technical_requirements: Optional[Dict[str, Any]] = None
    evaluation_criteria: Optional[Dict[str, Any]] = None
    compliance_requirements: Optional[Dict[str, Any]] = None
    organization: Optional[str] = None
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None

class RFPResponse(RFPBase):
    """RFP response schema"""
    id: int
    rfp_number: str
    status: RFPStatus
    issue_date: Optional[datetime] = None
    award_date: Optional[datetime] = None
    complexity_score: Optional[Decimal] = None
    risk_assessment: Optional[Dict[str, Any]] = None
    go_no_go_recommendation: Optional[str] = None
    ai_analysis_summary: Optional[str] = None
    key_insights: Optional[Dict[str, Any]] = None
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RFPListResponse(BaseModel):
    """RFP list response schema"""
    id: int
    title: str
    rfp_number: str
    status: RFPStatus
    rfp_type: RFPType
    estimated_budget: Optional[Decimal] = None
    currency: str
    submission_deadline: Optional[datetime] = None
    organization: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class RFPStatusUpdate(BaseModel):
    """RFP status update schema"""
    status: RFPStatus

class RFPAnalysisRequest(BaseModel):
    """RFP analysis request schema"""
    analyze_complexity: bool = True
    analyze_risks: bool = True
    generate_recommendations: bool = True
    custom_criteria: Optional[Dict[str, Any]] = None

class RFPAnalysisResponse(BaseModel):
    """RFP analysis response schema"""
    complexity_score: Optional[Decimal] = None
    risk_assessment: Optional[Dict[str, Any]] = None
    go_no_go_recommendation: Optional[str] = None
    analysis_summary: str
    key_insights: Dict[str, Any]
    confidence_score: Optional[Decimal] = None
    processing_time: float  # seconds

# Document schemas
class RFPDocumentUpload(BaseModel):
    """RFP document upload schema"""
    document_type: Optional[str] = None

class RFPDocumentResponse(BaseModel):
    """RFP document response schema"""
    id: int
    filename: str
    original_filename: str
    file_size: int
    content_type: str
    document_type: Optional[str] = None
    processing_status: str
    created_at: datetime

    class Config:
        from_attributes = True