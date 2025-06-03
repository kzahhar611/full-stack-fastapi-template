"""
RFP management endpoints
"""
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import date, timedelta

from ...core.database_simple import get_db
from ...models import Organization, User
from ...models.rfp_simple import RFP, RFPType, RFPStatus
from ...schemas.rfp import (
    RFPCreate, 
    RFPUpdate, 
    RFPResponse,
    RFPListResponse,
    RFPStats
)
from ...schemas.common import StatusResponse
from ...api.dependencies_simple import get_current_active_user

router = APIRouter()


@router.post("/", response_model=RFPResponse)
async def create_rfp(
    rfp_data: RFPCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create a new RFP
    """
    # Use user's organization if not specified
    organization_id = rfp_data.organization_id or current_user.organization_id
    
    if not organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with an organization to create RFPs"
        )
    
    # Verify organization exists and user has access
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Check permissions: Admin or user belongs to this organization
    if not current_user.is_admin and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create RFP in this organization"
        )
    
    # Check if RFP number is unique within organization
    existing_rfp = db.query(RFP).filter(
        and_(
            RFP.rfp_number == rfp_data.rfp_number,
            RFP.organization_id == organization_id
        )
    ).first()
    
    if existing_rfp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="RFP number already exists in this organization"
        )
    
    # Convert string rfp_type to enum
    try:
        rfp_type_enum = RFPType(rfp_data.rfp_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid RFP type: {rfp_data.rfp_type}. Valid types: {[e.value for e in RFPType]}"
        )
    
    # Create RFP
    rfp = RFP(
        title=rfp_data.title,
        description=rfp_data.description,
        rfp_number=rfp_data.rfp_number,
        rfp_type=rfp_type_enum,
        issue_date=rfp_data.issue_date,
        submission_deadline=rfp_data.submission_deadline,
        estimated_budget=rfp_data.estimated_budget,
        currency=rfp_data.currency,
        requirements=rfp_data.requirements,
        contact_person=rfp_data.contact_person,
        contact_email=rfp_data.contact_email,
        organization_id=organization_id,
        created_by_id=current_user.id,
        created_by=str(current_user.id)
    )
    
    db.add(rfp)
    db.commit()
    db.refresh(rfp)
    
    return rfp


@router.get("/", response_model=List[RFPListResponse])
async def list_rfps(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    rfp_type: Optional[str] = Query(None),
    public_only: bool = Query(False),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    List RFPs with filtering
    """
    query = db.query(RFP)
    
    # Apply organization filter for non-admin users
    if not current_user.is_admin:
        if public_only:
            query = query.filter(RFP.is_public == True)
        else:
            # Show organization RFPs and public RFPs
            query = query.filter(
                or_(
                    RFP.organization_id == current_user.organization_id,
                    RFP.is_public == True
                )
            )
    
    # Apply filters
    if status_filter:
        query = query.filter(RFP.status == status_filter)
    
    if rfp_type:
        query = query.filter(RFP.rfp_type == rfp_type)
    
    # Only show active RFPs
    query = query.filter(RFP.is_active == True)
    
    # Order by creation date (newest first)
    query = query.order_by(RFP.created_at.desc())
    
    rfps = query.offset(skip).limit(limit).all()
    return rfps


@router.get("/{rfp_id}", response_model=RFPResponse)
async def get_rfp(
    rfp_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get RFP by ID
    """
    rfp = db.query(RFP).filter(RFP.id == rfp_id).first()
    
    if not rfp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFP not found"
        )
    
    # Check permissions: Admin, belongs to organization, or is public
    if not current_user.is_admin:
        if not rfp.is_public and rfp.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to access this RFP"
            )
    
    return rfp


@router.put("/{rfp_id}", response_model=RFPResponse)
async def update_rfp(
    rfp_id: int,
    rfp_update: RFPUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update RFP
    """
    rfp = db.query(RFP).filter(RFP.id == rfp_id).first()
    
    if not rfp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFP not found"
        )
    
    # Check permissions: Admin, creator, or organization member with manager+ role
    can_edit = (
        current_user.is_admin or
        rfp.created_by_id == current_user.id or
        (rfp.organization_id == current_user.organization_id and 
         current_user.role.value in ['manager', 'admin', 'super_admin'])
    )
    
    if not can_edit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this RFP"
        )
    
    # Update fields
    update_data = rfp_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rfp, field, value)
    
    rfp.updated_by = str(current_user.id)
    
    db.commit()
    db.refresh(rfp)
    
    return rfp


@router.delete("/{rfp_id}", response_model=StatusResponse)
async def delete_rfp(
    rfp_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete RFP (soft delete)
    """
    rfp = db.query(RFP).filter(RFP.id == rfp_id).first()
    
    if not rfp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFP not found"
        )
    
    # Check permissions: Admin, creator, or organization admin
    can_delete = (
        current_user.is_admin or
        rfp.created_by_id == current_user.id or
        (rfp.organization_id == current_user.organization_id and 
         current_user.role.value in ['admin', 'super_admin'])
    )
    
    if not can_delete:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this RFP"
        )
    
    # Soft delete
    rfp.is_active = False
    rfp.updated_by = str(current_user.id)
    
    db.commit()
    
    return StatusResponse(
        success=True,
        message="RFP deleted successfully"
    )


@router.post("/{rfp_id}/publish", response_model=StatusResponse)
async def publish_rfp(
    rfp_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Publish RFP (make it available for proposals)
    """
    rfp = db.query(RFP).filter(RFP.id == rfp_id).first()
    
    if not rfp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFP not found"
        )
    
    # Check permissions
    can_publish = (
        current_user.is_admin or
        rfp.created_by_id == current_user.id or
        (rfp.organization_id == current_user.organization_id and 
         current_user.role.value in ['manager', 'admin', 'super_admin'])
    )
    
    if not can_publish:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to publish this RFP"
        )
    
    if rfp.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft RFPs can be published"
        )
    
    # Validate RFP is complete
    if not rfp.title or not rfp.rfp_number or not rfp.submission_deadline:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="RFP is incomplete. Please fill all required fields."
        )
    
    # Check deadline is in the future
    if rfp.submission_deadline <= date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Submission deadline must be in the future"
        )
    
    rfp.status = "published"
    rfp.updated_by = str(current_user.id)
    
    db.commit()
    
    return StatusResponse(
        success=True,
        message="RFP published successfully"
    )


@router.get("/stats/summary", response_model=RFPStats)
async def get_rfp_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get RFP statistics for the user's organization
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with an organization"
        )
    
    # Base query for user's organization
    base_query = db.query(RFP).filter(
        and_(
            RFP.organization_id == current_user.organization_id,
            RFP.is_active == True
        )
    )
    
    total_rfps = base_query.count()
    draft_rfps = base_query.filter(RFP.status == "draft").count()
    published_rfps = base_query.filter(RFP.status == "published").count()
    closed_rfps = base_query.filter(RFP.status == "closed").count()
    
    # Calculate average budget
    rfps_with_budget = base_query.filter(RFP.estimated_budget.isnot(None)).all()
    average_budget = None
    if rfps_with_budget:
        total_budget = sum(rfp.estimated_budget for rfp in rfps_with_budget)
        average_budget = total_budget / len(rfps_with_budget)
    
    # Upcoming deadlines (next 30 days)
    upcoming_deadline_date = date.today() + timedelta(days=30)
    upcoming_deadlines = base_query.filter(
        and_(
            RFP.submission_deadline <= upcoming_deadline_date,
            RFP.submission_deadline >= date.today(),
            RFP.status.in_(["published", "open"])
        )
    ).count()
    
    return RFPStats(
        total_rfps=total_rfps,
        draft_rfps=draft_rfps,
        published_rfps=published_rfps,
        closed_rfps=closed_rfps,
        average_budget=average_budget,
        upcoming_deadlines=upcoming_deadlines
    )