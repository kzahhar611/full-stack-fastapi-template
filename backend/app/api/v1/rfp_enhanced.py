"""
Enhanced RFP API endpoints with document management and templates
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, desc, asc
from datetime import datetime, timedelta
import json
import uuid

from ...core.database_enhanced import get_db
from ...api.dependencies_simple import get_current_user
from ...models.user_simple import User
from ...models.rfp_enhanced import RFPEnhanced, RFPDocument, RFPTemplate, RFPStatus, RFPType, DocumentType
from ...schemas.rfp_enhanced import (
    RFPEnhancedCreate, RFPEnhancedUpdate, RFPEnhancedResponse,
    RFPDocumentResponse, RFPDocumentUpdate,
    RFPTemplateCreate, RFPTemplateUpdate, RFPTemplateResponse,
    RFPSearchParams, RFPStatusUpdate, RFPExportRequest, RFPStatistics
)
from ...services.file_storage import file_storage_service

router = APIRouter()


# =============================================================================
# RFP ENHANCED ENDPOINTS
# =============================================================================

@router.get("/", response_model=List[RFPEnhancedResponse])
async def list_enhanced_rfps(
    search_params: RFPSearchParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List enhanced RFPs with advanced search and filtering"""
    
    # Build base query with organization filter
    query = db.query(RFPEnhanced).filter(
        RFPEnhanced.organization_id == current_user.organization_id
    )
    
    # Apply filters
    if search_params.query:
        # Full-text search across title, description, and requirements
        search_term = f"%{search_params.query}%"
        query = query.filter(
            or_(
                RFPEnhanced.title.ilike(search_term),
                RFPEnhanced.description.ilike(search_term),
                RFPEnhanced.description_html.ilike(search_term),
                RFPEnhanced.rfp_number.ilike(search_term),
                RFPEnhanced.category.ilike(search_term)
            )
        )
    
    if search_params.status:
        query = query.filter(RFPEnhanced.status.in_(search_params.status))
    
    if search_params.rfp_type:
        query = query.filter(RFPEnhanced.rfp_type.in_(search_params.rfp_type))
    
    if search_params.category:
        query = query.filter(RFPEnhanced.category.in_(search_params.category))
    
    if search_params.budget_min is not None:
        query = query.filter(
            or_(
                RFPEnhanced.estimated_budget >= search_params.budget_min,
                RFPEnhanced.budget_range_min >= search_params.budget_min
            )
        )
    
    if search_params.budget_max is not None:
        query = query.filter(
            or_(
                RFPEnhanced.estimated_budget <= search_params.budget_max,
                RFPEnhanced.budget_range_max <= search_params.budget_max
            )
        )
    
    if search_params.deadline_from:
        query = query.filter(RFPEnhanced.submission_deadline >= search_params.deadline_from)
    
    if search_params.deadline_to:
        query = query.filter(RFPEnhanced.submission_deadline <= search_params.deadline_to)
    
    if search_params.is_public is not None:
        query = query.filter(RFPEnhanced.is_public == search_params.is_public)
    
    if search_params.created_by:
        query = query.filter(RFPEnhanced.created_by_id.in_(search_params.created_by))
    
    # Apply sorting
    if search_params.sort_by == "title":
        order_column = RFPEnhanced.title
    elif search_params.sort_by == "updated_at":
        order_column = RFPEnhanced.updated_at
    elif search_params.sort_by == "submission_deadline":
        order_column = RFPEnhanced.submission_deadline
    elif search_params.sort_by == "estimated_budget":
        order_column = RFPEnhanced.estimated_budget
    else:  # default to created_at
        order_column = RFPEnhanced.created_at
    
    if search_params.sort_order == "asc":
        query = query.order_by(asc(order_column))
    else:
        query = query.order_by(desc(order_column))
    
    # Apply pagination
    total = query.count()
    rfps = query.offset(search_params.skip).limit(search_params.limit).all()
    
    # Convert to response model with computed fields
    response_rfps = []
    for rfp in rfps:
        rfp_dict = {
            **rfp.__dict__,
            "days_until_deadline": rfp.days_until_deadline,
            "hours_until_deadline": rfp.hours_until_deadline,
            "is_open": rfp.is_open,
            "document_count": rfp.document_count,
            "public_document_count": rfp.public_document_count
        }
        response_rfps.append(RFPEnhancedResponse(**rfp_dict))
    
    return response_rfps


@router.post("/", response_model=RFPEnhancedResponse)
async def create_enhanced_rfp(
    rfp_create: RFPEnhancedCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new enhanced RFP"""
    
    # Generate unique RFP number if not provided
    if not rfp_create.rfp_number:
        # Generate based on organization and timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M")
        org_prefix = current_user.organization.slug[:3].upper()
        rfp_create.rfp_number = f"{org_prefix}-RFP-{timestamp}"
    
    # Check if RFP number is unique
    existing_rfp = db.query(RFPEnhanced).filter(
        RFPEnhanced.rfp_number == rfp_create.rfp_number,
        RFPEnhanced.organization_id == current_user.organization_id
    ).first()
    
    if existing_rfp:
        raise HTTPException(
            status_code=400,
            detail=f"RFP number '{rfp_create.rfp_number}' already exists in your organization"
        )
    
    # Create RFP
    rfp_data = rfp_create.model_dump(exclude={"template_id"})
    
    # Handle template-based creation
    if rfp_create.template_id:
        template = db.query(RFPTemplate).filter(
            RFPTemplate.id == rfp_create.template_id,
            or_(
                RFPTemplate.organization_id == current_user.organization_id,
                RFPTemplate.is_system_template == True
            )
        ).first()
        
        if template:
            # Apply template data
            if template.description_template and not rfp_data.get("description_html"):
                rfp_data["description_html"] = template.description_template
            
            if template.requirements_template and not rfp_data.get("requirements_html"):
                rfp_data["requirements_html"] = template.requirements_template
            
            if template.default_requirements:
                # Merge template requirements with provided requirements
                template_reqs = template.default_requirements
                provided_reqs = rfp_data.get("requirements", {})
                rfp_data["requirements"] = {**template_reqs, **provided_reqs}
            
            if template.evaluation_criteria_template and not rfp_data.get("evaluation_criteria"):
                rfp_data["evaluation_criteria"] = template.evaluation_criteria_template
            
            rfp_data["is_template_based"] = True
            rfp_data["template_id"] = template.id
            
            # Update template usage count
            template.usage_count += 1
    
    new_rfp = RFPEnhanced(
        **rfp_data,
        organization_id=current_user.organization_id,
        created_by_id=current_user.id
    )
    
    db.add(new_rfp)
    db.commit()
    db.refresh(new_rfp)
    
    # Add computed fields for response
    rfp_dict = {
        **new_rfp.__dict__,
        "days_until_deadline": new_rfp.days_until_deadline,
        "hours_until_deadline": new_rfp.hours_until_deadline,
        "is_open": new_rfp.is_open,
        "document_count": new_rfp.document_count,
        "public_document_count": new_rfp.public_document_count
    }
    
    return RFPEnhancedResponse(**rfp_dict)


@router.get("/{rfp_id}", response_model=RFPEnhancedResponse)
async def get_enhanced_rfp(
    rfp_id: int,
    include_documents: bool = Query(False, description="Include document list in response"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get enhanced RFP by ID"""
    
    rfp = db.query(RFPEnhanced).filter(
        RFPEnhanced.id == rfp_id,
        RFPEnhanced.organization_id == current_user.organization_id
    ).first()
    
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    
    # Increment view count
    rfp.view_count += 1
    db.commit()
    
    # Prepare response data
    rfp_dict = {
        **rfp.__dict__,
        "days_until_deadline": rfp.days_until_deadline,
        "hours_until_deadline": rfp.hours_until_deadline,
        "is_open": rfp.is_open,
        "document_count": rfp.document_count,
        "public_document_count": rfp.public_document_count
    }
    
    # Include documents if requested
    if include_documents:
        documents = db.query(RFPDocument).filter(RFPDocument.rfp_id == rfp_id).all()
        rfp_dict["documents"] = [
            RFPDocumentResponse(
                **{
                    **doc.__dict__,
                    "download_url": f"/api/v1/rfps-enhanced/{rfp_id}/documents/{doc.id}/download"
                }
            ) for doc in documents
        ]
    
    return RFPEnhancedResponse(**rfp_dict)


@router.put("/{rfp_id}", response_model=RFPEnhancedResponse)
async def update_enhanced_rfp(
    rfp_id: int,
    rfp_update: RFPEnhancedUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update enhanced RFP"""
    
    rfp = db.query(RFPEnhanced).filter(
        RFPEnhanced.id == rfp_id,
        RFPEnhanced.organization_id == current_user.organization_id
    ).first()
    
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    
    # Check permissions (only creator or admin can edit)
    if (rfp.created_by_id != current_user.id and 
        current_user.role.value not in ["super_admin", "admin"]):
        raise HTTPException(status_code=403, detail="Not authorized to edit this RFP")
    
    # Check if RFP can be edited (not closed or awarded)
    if rfp.status in [RFPStatus.CLOSED, RFPStatus.AWARDED]:
        raise HTTPException(status_code=400, detail="Cannot edit closed or awarded RFP")
    
    # Update fields
    update_data = rfp_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rfp, field, value)
    
    rfp.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(rfp)
    
    # Add computed fields for response
    rfp_dict = {
        **rfp.__dict__,
        "days_until_deadline": rfp.days_until_deadline,
        "hours_until_deadline": rfp.hours_until_deadline,
        "is_open": rfp.is_open,
        "document_count": rfp.document_count,
        "public_document_count": rfp.public_document_count
    }
    
    return RFPEnhancedResponse(**rfp_dict)


@router.delete("/{rfp_id}")
async def delete_enhanced_rfp(
    rfp_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete enhanced RFP"""
    
    rfp = db.query(RFPEnhanced).filter(
        RFPEnhanced.id == rfp_id,
        RFPEnhanced.organization_id == current_user.organization_id
    ).first()
    
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    
    # Check permissions
    if (rfp.created_by_id != current_user.id and 
        current_user.role.value not in ["super_admin", "admin"]):
        raise HTTPException(status_code=403, detail="Not authorized to delete this RFP")
    
    # Check if RFP can be deleted (only drafts)
    if rfp.status != RFPStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Can only delete draft RFPs")
    
    # Delete associated documents from storage
    documents = db.query(RFPDocument).filter(RFPDocument.rfp_id == rfp_id).all()
    for document in documents:
        await file_storage_service.delete_file(document.file_path)
    
    # Delete RFP (cascade will handle documents)
    db.delete(rfp)
    db.commit()
    
    return {"message": "RFP deleted successfully"}


# =============================================================================
# RFP STATUS MANAGEMENT
# =============================================================================

@router.put("/{rfp_id}/status", response_model=RFPEnhancedResponse)
async def update_rfp_status(
    rfp_id: int,
    status_update: RFPStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update RFP status with workflow validation"""
    
    rfp = db.query(RFPEnhanced).filter(
        RFPEnhanced.id == rfp_id,
        RFPEnhanced.organization_id == current_user.organization_id
    ).first()
    
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    
    # Check permissions
    if (rfp.created_by_id != current_user.id and 
        current_user.role.value not in ["super_admin", "admin", "manager"]):
        raise HTTPException(status_code=403, detail="Not authorized to update RFP status")
    
    # Validate status transition
    valid_transitions = {
        RFPStatus.DRAFT: [RFPStatus.PUBLISHED, RFPStatus.CANCELLED],
        RFPStatus.PUBLISHED: [RFPStatus.OPEN, RFPStatus.CANCELLED],
        RFPStatus.OPEN: [RFPStatus.CLOSED, RFPStatus.CANCELLED],
        RFPStatus.CLOSED: [RFPStatus.AWARDED, RFPStatus.CANCELLED],
        RFPStatus.AWARDED: [],  # Final state
        RFPStatus.CANCELLED: []  # Final state
    }
    
    if status_update.status not in valid_transitions.get(rfp.status, []):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status transition from {rfp.status.value} to {status_update.status.value}"
        )
    
    # Update status
    rfp.status = status_update.status
    rfp.updated_at = datetime.utcnow()
    
    # Set publication date when publishing
    if status_update.status == RFPStatus.PUBLISHED and not rfp.publication_date:
        rfp.publication_date = datetime.utcnow()
    
    # Update workflow data with status change log
    if not rfp.workflow_data:
        rfp.workflow_data = {}
    
    status_history = rfp.workflow_data.get("status_history", [])
    status_history.append({
        "status": status_update.status.value,
        "changed_by": current_user.id,
        "changed_at": datetime.utcnow().isoformat(),
        "notes": status_update.notes
    })
    rfp.workflow_data["status_history"] = status_history
    
    db.commit()
    db.refresh(rfp)
    
    # Add computed fields for response
    rfp_dict = {
        **rfp.__dict__,
        "days_until_deadline": rfp.days_until_deadline,
        "hours_until_deadline": rfp.hours_until_deadline,
        "is_open": rfp.is_open,
        "document_count": rfp.document_count,
        "public_document_count": rfp.public_document_count
    }
    
    return RFPEnhancedResponse(**rfp_dict)


@router.post("/{rfp_id}/publish", response_model=RFPEnhancedResponse)
async def publish_rfp(
    rfp_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Publish RFP (shortcut for status update to PUBLISHED)"""
    
    status_update = RFPStatusUpdate(
        status=RFPStatus.PUBLISHED,
        notes="RFP published via publish endpoint"
    )
    
    return await update_rfp_status(rfp_id, status_update, current_user, db)


# =============================================================================
# RFP STATISTICS
# =============================================================================

@router.get("/statistics/overview", response_model=RFPStatistics)
async def get_rfp_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get RFP statistics for the organization"""
    
    # Base query for organization
    base_query = db.query(RFPEnhanced).filter(
        RFPEnhanced.organization_id == current_user.organization_id
    )
    
    # Total RFPs
    total_rfps = base_query.count()
    
    # RFPs by status
    status_counts = {}
    for status in RFPStatus:
        count = base_query.filter(RFPEnhanced.status == status).count()
        status_counts[status.value] = count
    
    # RFPs by type
    type_counts = {}
    for rfp_type in RFPType:
        count = base_query.filter(RFPEnhanced.rfp_type == rfp_type).count()
        type_counts[rfp_type.value] = count
    
    # Budget statistics
    budget_query = base_query.filter(RFPEnhanced.estimated_budget.isnot(None))
    total_budget = budget_query.with_entities(func.sum(RFPEnhanced.estimated_budget)).scalar() or 0
    avg_budget = budget_query.with_entities(func.avg(RFPEnhanced.estimated_budget)).scalar() or 0
    
    # Upcoming deadlines (next 7 days)
    next_week = datetime.utcnow() + timedelta(days=7)
    upcoming_deadlines = base_query.filter(
        RFPEnhanced.submission_deadline <= next_week,
        RFPEnhanced.submission_deadline >= datetime.utcnow(),
        RFPEnhanced.status.in_([RFPStatus.PUBLISHED, RFPStatus.OPEN])
    ).count()
    
    # Recent activity (last 30 days)
    last_month = datetime.utcnow() - timedelta(days=30)
    recent_activity = base_query.filter(
        or_(
            RFPEnhanced.created_at >= last_month,
            RFPEnhanced.updated_at >= last_month
        )
    ).count()
    
    return RFPStatistics(
        total_rfps=total_rfps,
        rfps_by_status=status_counts,
        rfps_by_type=type_counts,
        total_budget=float(total_budget),
        average_budget=float(avg_budget),
        upcoming_deadlines=upcoming_deadlines,
        recent_activity_count=recent_activity
    )