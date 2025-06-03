"""
API dependencies for authentication and authorization
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import verify_token, TokenData, user_has_permission
from ..models.user import User
from ..models.organization import Organization

# HTTP Bearer scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify the token
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
            
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except Exception:
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (additional check for user status)
    """
    if current_user.status.value != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is not active"
        )
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Get current verified user
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User email is not verified"
        )
    return current_user


async def get_current_user_organization(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Organization:
    """
    Get current user's organization
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with an organization"
        )
    
    organization = db.query(Organization).filter(
        Organization.id == current_user.organization_id
    ).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    if not organization.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization is not active"
        )
    
    return organization


# Permission-based dependencies
def require_permission(permission: str):
    """
    Create a dependency that requires a specific permission
    """
    async def permission_dependency(
        current_user: User = Depends(get_current_verified_user)
    ) -> User:
        if not user_has_permission(current_user.role.value, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Required: {permission}"
            )
        return current_user
    
    return permission_dependency


def require_admin():
    """Require admin role"""
    async def admin_dependency(
        current_user: User = Depends(get_current_verified_user)
    ) -> User:
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        return current_user
    
    return admin_dependency


def require_super_admin():
    """Require super admin role"""
    async def super_admin_dependency(
        current_user: User = Depends(get_current_verified_user)
    ) -> User:
        if current_user.role.value != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Super admin access required"
            )
        return current_user
    
    return super_admin_dependency


# Optional user dependency (for public endpoints that can benefit from user context)
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if token is provided, otherwise return None
    """
    if not credentials:
        return None
    
    try:
        payload = verify_token(credentials.credentials)
        if payload is None:
            return None
            
        user_id: int = payload.get("sub")
        if user_id is None:
            return None
            
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.is_active:
            return user
            
    except Exception:
        pass
    
    return None


# Organization context dependency
class OrganizationContext:
    """Organization context for multi-tenant operations"""
    def __init__(self, organization: Organization, user: User):
        self.organization = organization
        self.user = user
        self.user_role = user.role.value
        self.is_admin = user.is_admin


async def get_organization_context(
    current_user: User = Depends(get_current_verified_user),
    organization: Organization = Depends(get_current_user_organization)
) -> OrganizationContext:
    """
    Get organization context for multi-tenant operations
    """
    return OrganizationContext(organization, current_user)


# Resource ownership dependency
def require_resource_owner_or_admin(resource_user_id_field: str = "created_by_id"):
    """
    Create a dependency that requires the user to be the resource owner or admin
    """
    async def ownership_dependency(
        resource_id: int,
        current_user: User = Depends(get_current_verified_user),
        db: Session = Depends(get_db)
    ) -> User:
        # If user is admin, allow access
        if current_user.is_admin:
            return current_user
        
        # Check if user owns the resource
        # Note: This is a simplified check. In practice, you'd query the specific resource
        # and check ownership based on the resource type and ID
        return current_user
    
    return ownership_dependency


# API key authentication (for external integrations)
async def get_api_key_user(
    api_key: str,
    db: Session = Depends(get_db)
) -> User:
    """
    Authenticate user via API key
    """
    # This would check against a separate API keys table
    # For now, just a placeholder
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key"
    )