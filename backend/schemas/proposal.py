"""
TenderWise AI - Proposal Schemas
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from models.proposal import ProposalStatus


class ProposalDocumentResponse(BaseModel):
    """Proposal document response schema"""
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


class ProposalBase(BaseModel):
    """Base proposal schema"""
    title: str = Field(..., min_length=1, max_length=500)
    executive_summary: Optional[str] = None
    technical_approach: Optional[str] = None
    total_cost: Optional[float] = Field(None, ge=0)
    currency: str = Field(default="USD", max_length=3)
    cost_breakdown: Optional[Dict[str, Any]] = None
    proposed_timeline: Optional[Dict[str, Any]] = None
    delivery_date: Optional[datetime] = None
    compliance_matrix: Optional[Dict[str, Any]] = None


class ProposalCreate(ProposalBase):
    """Proposal creation schema"""
    rfp_id: int = Field(..., gt=0)


class ProposalUpdate(ProposalBase):
    """Proposal update schema - all fields optional"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)


class ProposalStatusUpdate(BaseModel):
    """Proposal status update schema"""
    status: ProposalStatus


class ProposalListResponse(BaseModel):
    """Proposal list item response schema"""
    id: int
    rfp_id: int
    title: str
    proposal_number: str
    status: ProposalStatus
    total_cost: Optional[float] = None
    currency: str
    delivery_date: Optional[datetime] = None
    compliance_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime] = None
    
    # Related data
    rfp_title: Optional[str] = None
    rfp_number: Optional[str] = None
    rfp_organization: Optional[str] = None

    class Config:
        from_attributes = True


class ProposalResponse(ProposalBase):
    """Complete proposal response schema"""
    id: int
    rfp_id: int
    proposal_number: str
    status: ProposalStatus
    compliance_score: Optional[float] = None
    evaluation_results: Optional[Dict[str, Any]] = None
    
    # AI Analysis
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    risk_factors: Optional[List[str]] = None
    recommendation: Optional[str] = None
    
    # Metadata
    created_by: int
    submitted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # Related data
    rfp_title: Optional[str] = None
    rfp_number: Optional[str] = None
    rfp_organization: Optional[str] = None
    documents: List[ProposalDocumentResponse] = []

    class Config:
        from_attributes = True


class ProposalEvaluationRequest(BaseModel):
    """Proposal evaluation request schema"""
    evaluate_technical: bool = True
    evaluate_financial: bool = True
    evaluate_compliance: bool = True
    custom_criteria: Optional[Dict[str, float]] = None


class ProposalEvaluationResponse(BaseModel):
    """Proposal evaluation response schema"""
    proposal_id: int
    overall_score: float
    technical_score: Optional[float] = None
    financial_score: Optional[float] = None
    compliance_score: Optional[float] = None
    strengths: List[str] = []
    weaknesses: List[str] = []
    risk_factors: List[str] = []
    recommendation: str
    evaluation_summary: str
    created_at: datetime


class ProposalFilters(BaseModel):
    """Proposal filtering parameters"""
    search: Optional[str] = None
    status: Optional[ProposalStatus] = None
    rfp_id: Optional[int] = None
    my_proposals: bool = False
    min_cost: Optional[float] = None
    max_cost: Optional[float] = None
    order_by: str = "created_at"
    order_direction: str = "desc"