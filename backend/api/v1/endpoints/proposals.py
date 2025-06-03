"""
TenderWise AI - Proposals Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session

from core.database import get_db
from auth.dependencies import get_current_active_user
from models.user import User
from models.proposal import ProposalStatus
from models.rfp import RFP
from schemas.proposal import (
    ProposalResponse,
    ProposalListResponse,
    ProposalCreate,
    ProposalUpdate,
    ProposalStatusUpdate,
    ProposalEvaluationRequest,
    ProposalEvaluationResponse,
    ProposalDocumentResponse,
    ProposalFilters
)
from services.proposal_service import ProposalService
from services.file_service import FileService

router = APIRouter()


@router.get("/", response_model=List[ProposalListResponse])
async def get_proposals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[ProposalStatus] = Query(None),
    search: Optional[str] = Query(None),
    rfp_id: Optional[int] = Query(None),
    my_proposals: bool = Query(False),
    min_cost: Optional[float] = Query(None),
    max_cost: Optional[float] = Query(None),
    order_by: str = Query("created_at"),
    order_direction: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get proposals with filtering and pagination"""
    filters = ProposalFilters(
        search=search,
        status=status,
        rfp_id=rfp_id,
        my_proposals=my_proposals,
        min_cost=min_cost,
        max_cost=max_cost,
        order_by=order_by,
        order_direction=order_direction
    )
    
    proposals = ProposalService.get_proposals(
        db=db,
        filters=filters,
        current_user=current_user,
        skip=skip,
        limit=limit
    )
    
    # Convert to response format with RFP data
    response_proposals = []
    for proposal in proposals:
        # Get RFP data
        rfp = db.query(RFP).filter(RFP.id == proposal.rfp_id).first()
        
        proposal_dict = {
            "id": proposal.id,
            "rfp_id": proposal.rfp_id,
            "title": proposal.title,
            "proposal_number": proposal.proposal_number,
            "status": proposal.status,
            "total_cost": proposal.total_cost,
            "currency": proposal.currency,
            "delivery_date": proposal.delivery_date,
            "compliance_score": proposal.compliance_score,
            "created_at": proposal.created_at,
            "updated_at": proposal.updated_at,
            "submitted_at": proposal.submitted_at,
            "rfp_title": rfp.title if rfp else None,
            "rfp_number": rfp.rfp_number if rfp else None,
            "rfp_organization": rfp.organization if rfp else None,
        }
        response_proposals.append(ProposalListResponse(**proposal_dict))
    
    return response_proposals


@router.post("/", response_model=ProposalResponse)
async def create_proposal(
    proposal_data: ProposalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new proposal"""
    proposal = ProposalService.create_proposal(
        db=db,
        proposal_data=proposal_data,
        current_user=current_user
    )
    
    return ProposalResponse.from_orm(proposal)


@router.get("/{proposal_id}", response_model=ProposalResponse)
async def get_proposal(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get proposal by ID"""
    proposal = ProposalService.get_proposal_by_id(db, proposal_id)
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found"
        )
    
    # Check permissions
    if not current_user.is_superuser and proposal.created_by != current_user.id:
        # Allow viewing submitted proposals
        if proposal.status != ProposalStatus.SUBMITTED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this proposal"
            )
    
    # Get RFP data
    rfp = db.query(RFP).filter(RFP.id == proposal.rfp_id).first()
    
    # Build response with RFP data
    proposal_dict = proposal.__dict__.copy()
    proposal_dict.update({
        "rfp_title": rfp.title if rfp else None,
        "rfp_number": rfp.rfp_number if rfp else None,
        "rfp_organization": rfp.organization if rfp else None,
    })
    
    return ProposalResponse(**proposal_dict)


@router.put("/{proposal_id}", response_model=ProposalResponse)
async def update_proposal(
    proposal_id: int,
    proposal_data: ProposalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update proposal"""
    proposal = ProposalService.update_proposal(
        db=db,
        proposal_id=proposal_id,
        proposal_data=proposal_data,
        current_user=current_user
    )
    
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found"
        )
    
    return ProposalResponse.from_orm(proposal)


@router.put("/{proposal_id}/status", response_model=ProposalResponse)
async def update_proposal_status(
    proposal_id: int,
    status_update: ProposalStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update proposal status"""
    proposal = ProposalService.update_proposal_status(
        db=db,
        proposal_id=proposal_id,
        status=status_update.status,
        current_user=current_user
    )
    
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found"
        )
    
    return ProposalResponse.from_orm(proposal)


@router.delete("/{proposal_id}")
async def delete_proposal(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete proposal"""
    success = ProposalService.delete_proposal(
        db=db,
        proposal_id=proposal_id,
        current_user=current_user
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found"
        )
    
    return {"message": "Proposal deleted successfully"}


@router.get("/{proposal_id}/documents", response_model=List[ProposalDocumentResponse])
async def get_proposal_documents(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get documents for a proposal"""
    proposal = ProposalService.get_proposal_by_id(db, proposal_id)
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found"
        )
    
    # Check permissions
    if not current_user.is_superuser and proposal.created_by != current_user.id:
        if proposal.status != ProposalStatus.SUBMITTED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view documents for this proposal"
            )
    
    documents = FileService.get_proposal_documents(db, proposal_id)
    
    return [ProposalDocumentResponse.from_orm(doc) for doc in documents]


@router.post("/{proposal_id}/documents", response_model=ProposalDocumentResponse)
async def upload_proposal_document(
    proposal_id: int,
    file: UploadFile = File(...),
    document_type: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload document for a proposal"""
    proposal = ProposalService.get_proposal_by_id(db, proposal_id)
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found"
        )
    
    # Check permissions
    if not ProposalService.can_user_edit_proposal(proposal, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to upload documents for this proposal"
        )
    
    document = await FileService.upload_proposal_document(
        db=db,
        proposal_id=proposal_id,
        file=file,
        uploaded_by=current_user.id,
        document_type=document_type
    )
    
    return ProposalDocumentResponse.from_orm(document)


@router.delete("/{proposal_id}/documents/{document_id}")
async def delete_proposal_document(
    proposal_id: int,
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a proposal document"""
    proposal = ProposalService.get_proposal_by_id(db, proposal_id)
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found"
        )
    
    # Check permissions
    if not ProposalService.can_user_edit_proposal(proposal, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete documents for this proposal"
        )
    
    success = FileService.delete_proposal_document(db, proposal_id, document_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return {"message": "Document deleted successfully"}


@router.post("/{proposal_id}/evaluate", response_model=ProposalEvaluationResponse)
async def evaluate_proposal(
    proposal_id: int,
    evaluation_request: ProposalEvaluationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Evaluate proposal with AI"""
    proposal = ProposalService.get_proposal_by_id(db, proposal_id)
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found"
        )
    
    # Only superusers can evaluate proposals
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to evaluate proposals"
        )
    
    # TODO: Implement actual AI evaluation
    # For now, return mock evaluation
    from datetime import datetime
    
    evaluation = ProposalEvaluationResponse(
        proposal_id=proposal_id,
        overall_score=85.5,
        technical_score=88.0 if evaluation_request.evaluate_technical else None,
        financial_score=82.0 if evaluation_request.evaluate_financial else None,
        compliance_score=87.0 if evaluation_request.evaluate_compliance else None,
        strengths=[
            "Strong technical approach",
            "Competitive pricing",
            "Proven track record"
        ],
        weaknesses=[
            "Timeline might be aggressive",
            "Some compliance requirements need clarification"
        ],
        risk_factors=[
            "Delivery timeline risk",
            "Resource allocation concerns"
        ],
        recommendation="ACCEPT",
        evaluation_summary="This proposal demonstrates strong technical capabilities with competitive pricing. While there are some timeline concerns, the overall quality and approach make it a strong candidate for selection.",
        created_at=datetime.utcnow()
    )
    
    return evaluation