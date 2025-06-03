"""
Organization management endpoints
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...core.database_simple import get_db
from ...models import Organization, User
from ...schemas.organization import (
    OrganizationCreate, 
    OrganizationUpdate, 
    OrganizationResponse,
    OrganizationListResponse
)
from ...schemas.common import StatusResponse, PaginatedResponse
from ...api.dependencies_simple import get_current_user, get_current_active_user

router = APIRouter()


@router.post("/", response_model=OrganizationResponse)
async def create_organization(
    organization_data: OrganizationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create a new organization (Admin only)
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create organizations"
        )
    
    # Check if slug is unique
    existing_org = db.query(Organization).filter(
        Organization.slug == organization_data.slug
    ).first()
    
    if existing_org:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization slug already exists"
        )
    
    # Create organization
    organization = Organization(
        name=organization_data.name,
        slug=organization_data.slug,
        description=organization_data.description,
        website=organization_data.website,
        email=organization_data.email,
        phone=organization_data.phone,
        address_line1=organization_data.address_line1,
        address_line2=organization_data.address_line2,
        city=organization_data.city,
        state=organization_data.state,
        country=organization_data.country,
        postal_code=organization_data.postal_code,
        organization_type=organization_data.organization_type,
        industry=organization_data.industry,
        size=organization_data.size,
        created_by=str(current_user.id)
    )
    
    db.add(organization)
    db.commit()
    db.refresh(organization)
    
    return organization


@router.get("/", response_model=List[OrganizationListResponse])
async def list_organizations(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    List all organizations (Admin only)
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can list all organizations"
        )
    
    organizations = db.query(Organization).offset(skip).limit(limit).all()
    return organizations


@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
    organization_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get organization by ID
    """
    organization = db.query(Organization).filter(
        Organization.id == organization_id
    ).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Check permissions: Admin or user belongs to this organization
    if not current_user.is_admin and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this organization"
        )
    
    return organization


@router.put("/{organization_id}", response_model=OrganizationResponse)
async def update_organization(
    organization_id: int,
    organization_update: OrganizationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update organization
    """
    organization = db.query(Organization).filter(
        Organization.id == organization_id
    ).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Check permissions: Admin or user belongs to this organization
    if not current_user.is_admin and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this organization"
        )
    
    # Update fields
    update_data = organization_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(organization, field, value)
    
    organization.updated_by = str(current_user.id)
    
    db.commit()
    db.refresh(organization)
    
    return organization


@router.delete("/{organization_id}", response_model=StatusResponse)
async def delete_organization(
    organization_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete organization (Super Admin only)
    """
    if current_user.role.value != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can delete organizations"
        )
    
    organization = db.query(Organization).filter(
        Organization.id == organization_id
    ).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Check if organization has users
    user_count = db.query(User).filter(User.organization_id == organization_id).count()
    if user_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete organization with {user_count} users. Move or delete users first."
        )
    
    db.delete(organization)
    db.commit()
    
    return StatusResponse(
        success=True,
        message="Organization deleted successfully"
    )


@router.get("/{organization_id}/users", response_model=List[dict])
async def get_organization_users(
    organization_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get users in organization
    """
    organization = db.query(Organization).filter(
        Organization.id == organization_id
    ).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Check permissions
    if not current_user.is_admin and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this organization's users"
        )
    
    users = db.query(User).filter(User.organization_id == organization_id).all()
    
    return [
        {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "role": user.role.value,
            "status": user.status.value,
            "is_active": user.is_active,
            "created_at": user.created_at
        }
        for user in users
    ]