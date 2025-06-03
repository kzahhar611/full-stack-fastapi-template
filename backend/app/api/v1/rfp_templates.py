"""
RFP Template Management API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from datetime import datetime

from ...core.database_enhanced import get_db
from ...api.dependencies_simple import get_current_user
from ...models.user_simple import User
from ...models.rfp_enhanced import RFPTemplate, RFPType
from ...schemas.rfp_enhanced import (
    RFPTemplateCreate, RFPTemplateUpdate, RFPTemplateResponse
)

router = APIRouter()


# =============================================================================
# TEMPLATE MANAGEMENT
# =============================================================================

@router.get("/", response_model=List[RFPTemplateResponse])
async def list_rfp_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    rfp_type: Optional[RFPType] = Query(None, description="Filter by RFP type"),
    include_system: bool = Query(True, description="Include system templates"),
    only_active: bool = Query(True, description="Only show active templates"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List RFP templates"""
    
    # Build query
    query = db.query(RFPTemplate)
    
    # Filter by organization and system templates
    if include_system:
        query = query.filter(
            or_(
                RFPTemplate.organization_id == current_user.organization_id,
                RFPTemplate.is_system_template == True
            )
        )
    else:
        query = query.filter(RFPTemplate.organization_id == current_user.organization_id)
    
    # Apply filters
    if category:
        query = query.filter(RFPTemplate.category.ilike(f"%{category}%"))
    
    if rfp_type:
        query = query.filter(RFPTemplate.rfp_type == rfp_type)
    
    if only_active:
        query = query.filter(RFPTemplate.is_active == True)
    
    # Order by usage count (popular first) and creation date
    templates = query.order_by(
        desc(RFPTemplate.usage_count),
        desc(RFPTemplate.created_at)
    ).all()
    
    return [RFPTemplateResponse.model_validate(template) for template in templates]


@router.get("/{template_id}", response_model=RFPTemplateResponse)
async def get_rfp_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get RFP template by ID"""
    
    template = db.query(RFPTemplate).filter(
        RFPTemplate.id == template_id,
        or_(
            RFPTemplate.organization_id == current_user.organization_id,
            RFPTemplate.is_system_template == True
        )
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return RFPTemplateResponse.model_validate(template)


@router.post("/", response_model=RFPTemplateResponse)
async def create_rfp_template(
    template_create: RFPTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new RFP template"""
    
    # Check if user can create templates (admin, manager, or super admin)
    if current_user.role.value not in ["super_admin", "admin", "manager"]:
        raise HTTPException(status_code=403, detail="Not authorized to create templates")
    
    # Check for duplicate template name in organization
    existing_template = db.query(RFPTemplate).filter(
        RFPTemplate.name == template_create.name,
        RFPTemplate.organization_id == current_user.organization_id
    ).first()
    
    if existing_template:
        raise HTTPException(
            status_code=400,
            detail=f"Template with name '{template_create.name}' already exists in your organization"
        )
    
    # Create template
    template_data = template_create.model_dump()
    new_template = RFPTemplate(
        **template_data,
        organization_id=current_user.organization_id,
        created_by_id=current_user.id,
        is_system_template=False
    )
    
    db.add(new_template)
    db.commit()
    db.refresh(new_template)
    
    return RFPTemplateResponse.model_validate(new_template)


@router.put("/{template_id}", response_model=RFPTemplateResponse)
async def update_rfp_template(
    template_id: int,
    template_update: RFPTemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update RFP template"""
    
    template = db.query(RFPTemplate).filter(
        RFPTemplate.id == template_id,
        RFPTemplate.organization_id == current_user.organization_id
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Check permissions (creator, admin, or super admin can edit)
    if (template.created_by_id != current_user.id and 
        current_user.role.value not in ["super_admin", "admin"]):
        raise HTTPException(status_code=403, detail="Not authorized to edit this template")
    
    # Cannot edit system templates
    if template.is_system_template:
        raise HTTPException(status_code=400, detail="Cannot edit system templates")
    
    # Update fields
    update_data = template_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    
    template.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(template)
    
    return RFPTemplateResponse.model_validate(template)


@router.delete("/{template_id}")
async def delete_rfp_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete RFP template"""
    
    template = db.query(RFPTemplate).filter(
        RFPTemplate.id == template_id,
        RFPTemplate.organization_id == current_user.organization_id
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Check permissions
    if (template.created_by_id != current_user.id and 
        current_user.role.value not in ["super_admin", "admin"]):
        raise HTTPException(status_code=403, detail="Not authorized to delete this template")
    
    # Cannot delete system templates
    if template.is_system_template:
        raise HTTPException(status_code=400, detail="Cannot delete system templates")
    
    # Check if template is being used
    from ...models.rfp_enhanced import RFPEnhanced
    rfps_using_template = db.query(RFPEnhanced).filter(
        RFPEnhanced.template_id == template_id
    ).count()
    
    if rfps_using_template > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete template. It is being used by {rfps_using_template} RFP(s)"
        )
    
    db.delete(template)
    db.commit()
    
    return {"message": "Template deleted successfully"}


@router.post("/{template_id}/duplicate", response_model=RFPTemplateResponse)
async def duplicate_rfp_template(
    template_id: int,
    new_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Duplicate an existing template"""
    
    # Get source template
    source_template = db.query(RFPTemplate).filter(
        RFPTemplate.id == template_id,
        or_(
            RFPTemplate.organization_id == current_user.organization_id,
            RFPTemplate.is_system_template == True
        )
    ).first()
    
    if not source_template:
        raise HTTPException(status_code=404, detail="Source template not found")
    
    # Check if user can create templates
    if current_user.role.value not in ["super_admin", "admin", "manager"]:
        raise HTTPException(status_code=403, detail="Not authorized to create templates")
    
    # Check for duplicate name
    existing_template = db.query(RFPTemplate).filter(
        RFPTemplate.name == new_name,
        RFPTemplate.organization_id == current_user.organization_id
    ).first()
    
    if existing_template:
        raise HTTPException(
            status_code=400,
            detail=f"Template with name '{new_name}' already exists in your organization"
        )
    
    # Create duplicate
    new_template = RFPTemplate(
        name=new_name,
        description=f"Copy of {source_template.name}",
        category=source_template.category,
        rfp_type=source_template.rfp_type,
        template_data=source_template.template_data.copy() if source_template.template_data else {},
        default_requirements=source_template.default_requirements.copy() if source_template.default_requirements else {},
        evaluation_criteria_template=source_template.evaluation_criteria_template.copy() if source_template.evaluation_criteria_template else {},
        description_template=source_template.description_template,
        requirements_template=source_template.requirements_template,
        is_active=True,
        is_system_template=False,
        organization_id=current_user.organization_id,
        created_by_id=current_user.id,
        usage_count=0
    )
    
    db.add(new_template)
    db.commit()
    db.refresh(new_template)
    
    return RFPTemplateResponse.model_validate(new_template)


# =============================================================================
# TEMPLATE CATEGORIES & STATISTICS
# =============================================================================

@router.get("/categories/list")
async def list_template_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of all template categories"""
    
    # Get categories from templates accessible to user
    categories = db.query(RFPTemplate.category).filter(
        or_(
            RFPTemplate.organization_id == current_user.organization_id,
            RFPTemplate.is_system_template == True
        ),
        RFPTemplate.is_active == True
    ).distinct().all()
    
    return [category[0] for category in categories if category[0]]


@router.get("/statistics/usage")
async def get_template_usage_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get template usage statistics"""
    
    # Most used templates
    popular_templates = db.query(RFPTemplate).filter(
        or_(
            RFPTemplate.organization_id == current_user.organization_id,
            RFPTemplate.is_system_template == True
        ),
        RFPTemplate.is_active == True
    ).order_by(desc(RFPTemplate.usage_count)).limit(10).all()
    
    # Template counts by category
    category_counts = {}
    templates_by_category = db.query(
        RFPTemplate.category,
        db.func.count(RFPTemplate.id).label('count')
    ).filter(
        or_(
            RFPTemplate.organization_id == current_user.organization_id,
            RFPTemplate.is_system_template == True
        ),
        RFPTemplate.is_active == True
    ).group_by(RFPTemplate.category).all()
    
    for category, count in templates_by_category:
        if category:
            category_counts[category] = count
    
    # Template counts by type
    type_counts = {}
    templates_by_type = db.query(
        RFPTemplate.rfp_type,
        db.func.count(RFPTemplate.id).label('count')
    ).filter(
        or_(
            RFPTemplate.organization_id == current_user.organization_id,
            RFPTemplate.is_system_template == True
        ),
        RFPTemplate.is_active == True
    ).group_by(RFPTemplate.rfp_type).all()
    
    for rfp_type, count in templates_by_type:
        type_counts[rfp_type.value] = count
    
    return {
        "popular_templates": [
            {
                "id": template.id,
                "name": template.name,
                "category": template.category,
                "usage_count": template.usage_count,
                "is_system_template": template.is_system_template
            }
            for template in popular_templates
        ],
        "templates_by_category": category_counts,
        "templates_by_type": type_counts
    }


# =============================================================================
# TEMPLATE EXPORT & IMPORT
# =============================================================================

@router.get("/{template_id}/export")
async def export_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export template as JSON"""
    
    template = db.query(RFPTemplate).filter(
        RFPTemplate.id == template_id,
        or_(
            RFPTemplate.organization_id == current_user.organization_id,
            RFPTemplate.is_system_template == True
        )
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Create export data
    export_data = {
        "template_info": {
            "name": template.name,
            "description": template.description,
            "category": template.category,
            "rfp_type": template.rfp_type.value,
            "version": "1.0",
            "exported_at": datetime.utcnow().isoformat(),
            "exported_by": current_user.email
        },
        "template_data": template.template_data,
        "default_requirements": template.default_requirements,
        "evaluation_criteria_template": template.evaluation_criteria_template,
        "description_template": template.description_template,
        "requirements_template": template.requirements_template
    }
    
    from fastapi.responses import JSONResponse
    import json
    
    return JSONResponse(
        content=export_data,
        headers={
            "Content-Disposition": f"attachment; filename={template.name.replace(' ', '_')}_template.json"
        }
    )