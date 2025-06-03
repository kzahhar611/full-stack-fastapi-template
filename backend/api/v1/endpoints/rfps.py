"""
TenderWise AI - RFPs Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session

from core.database import get_db
from auth.dependencies import get_current_active_user
from models.user import User
from models.rfp import RFPStatus
from schemas.rfp import (
    RFPResponse, 
    RFPListResponse, 
    RFPCreate, 
    RFPUpdate, 
    RFPStatusUpdate,
    RFPAnalysisRequest,
    RFPAnalysisResponse,
    RFPDocumentResponse
)
from services.rfp_service import RFPService
from services.file_service import FileService

router = APIRouter()


@router.get("/", response_model=List[RFPListResponse])
async def get_rfps(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[RFPStatus] = Query(None),
    search: Optional[str] = Query(None),
    my_rfps: bool = Query(False),
    order_by: str = Query("created_at"),
    order_direction: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get RFPs with filtering and pagination"""
    created_by = current_user.id if my_rfps else None
    
    # Non-superusers can only see their own RFPs or published ones
    if not current_user.is_superuser and not my_rfps:
        # This will be handled in the service layer
        pass
    
    rfps = RFPService.get_rfps(
        db=db,
        skip=skip,
        limit=limit,
        status=status,
        created_by=created_by,
        search=search,
        order_by=order_by,
        order_direction=order_direction
    )
    
    # Filter RFPs based on user permissions
    accessible_rfps = []
    for rfp in rfps:
        if RFPService.can_user_view_rfp(rfp, current_user):
            accessible_rfps.append(rfp)
    
    return [RFPListResponse.from_orm(rfp) for rfp in accessible_rfps]


@router.post("/", response_model=RFPResponse)
async def create_rfp(
    rfp_data: RFPCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new RFP"""
    rfp = RFPService.create_rfp(
        db=db,
        rfp_data=rfp_data,
        created_by=current_user.id
    )
    
    return RFPResponse.from_orm(rfp)


@router.get("/{rfp_id}", response_model=RFPResponse)
async def get_rfp(
    rfp_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get RFP by ID"""
    rfp = RFPService.get_rfp_by_id(db, rfp_id)
    if not rfp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFP not found"
        )
    
    # Check permissions
    if not RFPService.can_user_view_rfp(rfp, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this RFP"
        )
    
    return RFPResponse.from_orm(rfp)


@router.put("/{rfp_id}", response_model=RFPResponse)
async def update_rfp(
    rfp_id: int,
    rfp_update: RFPUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update RFP"""
    rfp = RFPService.get_rfp_by_id(db, rfp_id)
    if not rfp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFP not found"
        )
    
    # Check permissions
    if not RFPService.can_user_edit_rfp(rfp, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to edit this RFP"
        )
    
    updated_rfp = RFPService.update_rfp(
        db=db,
        rfp_id=rfp_id,
        rfp_update=rfp_update,
        updated_by=current_user.id
    )
    
    return RFPResponse.from_orm(updated_rfp)


@router.put("/{rfp_id}/status", response_model=RFPResponse)
async def update_rfp_status(
    rfp_id: int,
    status_update: RFPStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update RFP status"""
    rfp = RFPService.get_rfp_by_id(db, rfp_id)
    if not rfp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFP not found"
        )
    
    # Check permissions
    if not RFPService.can_user_edit_rfp(rfp, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to edit this RFP"
        )
    
    updated_rfp = RFPService.update_rfp_status(
        db=db,
        rfp_id=rfp_id,
        new_status=status_update.status,
        updated_by=current_user.id
    )
    
    return RFPResponse.from_orm(updated_rfp)


@router.delete("/{rfp_id}")
async def delete_rfp(
    rfp_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete RFP (soft delete)"""
    rfp = RFPService.get_rfp_by_id(db, rfp_id)
    if not rfp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFP not found"
        )
    
    # Check permissions
    if not RFPService.can_user_edit_rfp(rfp, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this RFP"
        )
    
    success = RFPService.delete_rfp(db, rfp_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete RFP. Only draft RFPs can be deleted."
        )
    
    return {"message": "RFP deleted successfully"}


@router.post("/{rfp_id}/analyze", response_model=RFPAnalysisResponse)
async def analyze_rfp(
    rfp_id: int,
    analysis_request: RFPAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Analyze RFP with AI (placeholder)"""
    rfp = RFPService.get_rfp_by_id(db, rfp_id)
    if not rfp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFP not found"
        )
    
    # Check permissions
    if not RFPService.can_user_view_rfp(rfp, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to analyze this RFP"
        )
    
    # TODO: Implement actual AI analysis
    # For now, return mock analysis
    mock_analysis = RFPAnalysisResponse(
        complexity_score=7.5,
        risk_assessment={
            "technical_risk": "Medium",
            "financial_risk": "Low",
            "timeline_risk": "High",
            "market_risk": "Medium"
        },
        go_no_go_recommendation="GO",
        analysis_summary=f"Analysis for RFP {rfp.rfp_number}: This RFP presents a moderate complexity project with manageable risks. The technical requirements are well-defined, and the budget appears realistic. However, the timeline is aggressive and may require careful resource planning.",
        key_insights={
            "estimated_effort": "6-8 months",
            "required_team_size": "8-12 people",
            "key_technologies": ["Python", "FastAPI", "React", "AI/ML"],
            "critical_success_factors": [
                "Strong project management",
                "Early stakeholder engagement",
                "Agile development approach"
            ]
        },
        confidence_score=0.85,
        processing_time=2.3
    )
    
    return mock_analysis


@router.get("/{rfp_id}/documents", response_model=List[RFPDocumentResponse])
async def get_rfp_documents(
    rfp_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get documents for an RFP"""
    rfp = RFPService.get_rfp_by_id(db, rfp_id)
    if not rfp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFP not found"
        )
    
    # Check permissions
    if not RFPService.can_user_view_rfp(rfp, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this RFP"
        )
    
    documents = FileService.get_rfp_documents(db, rfp_id)
    
    return [RFPDocumentResponse.from_orm(doc) for doc in documents]


@router.post("/{rfp_id}/documents", response_model=RFPDocumentResponse)
async def upload_rfp_document(
    rfp_id: int,
    file: UploadFile = File(...),
    document_type: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload document for an RFP"""
    rfp = RFPService.get_rfp_by_id(db, rfp_id)
    if not rfp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFP not found"
        )
    
    # Check permissions (must be able to edit RFP to upload documents)
    if not RFPService.can_user_edit_rfp(rfp, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to upload documents for this RFP"
        )
    
    document = await FileService.upload_rfp_document(
        db=db,
        rfp_id=rfp_id,
        file=file,
        uploaded_by=current_user.id,
        document_type=document_type
    )
    
    return RFPDocumentResponse.from_orm(document)


@router.delete("/{rfp_id}/documents/{document_id}")
async def delete_rfp_document(
    rfp_id: int,
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete document from an RFP"""
    rfp = RFPService.get_rfp_by_id(db, rfp_id)
    if not rfp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFP not found"
        )
    
    # Check permissions
    if not RFPService.can_user_edit_rfp(rfp, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete documents for this RFP"
        )
    
    # Check if document belongs to this RFP
    document = FileService.get_document_by_id(db, document_id)
    if not document or document.rfp_id != rfp_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    success = FileService.delete_rfp_document(db, document_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document"
        )
    
    return {"message": "Document deleted successfully"}