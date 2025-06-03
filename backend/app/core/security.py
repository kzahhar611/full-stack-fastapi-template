"""
Security utilities for authentication and authorization
"""
from datetime import datetime, timedelta
from typing import Optional, Union
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer scheme for JWT tokens
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def create_password_reset_token(email: str) -> str:
    """Create password reset token"""
    data = {"sub": email, "type": "password_reset"}
    expire = datetime.utcnow() + timedelta(hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS)
    data.update({"exp": expire})
    
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_password_reset_token(token: str) -> Optional[str]:
    """Verify password reset token and return email"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "password_reset":
            return None
        return payload.get("sub")
    except JWTError:
        return None


def create_email_verification_token(email: str) -> str:
    """Create email verification token"""
    data = {"sub": email, "type": "email_verification"}
    expire = datetime.utcnow() + timedelta(days=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_DAYS)
    data.update({"exp": expire})
    
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_email_verification_token(token: str) -> Optional[str]:
    """Verify email verification token and return email"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "email_verification":
            return None
        return payload.get("sub")
    except JWTError:
        return None


class TokenData:
    """Token data class"""
    def __init__(self, user_id: Optional[int] = None, email: Optional[str] = None):
        self.user_id = user_id
        self.email = email


def generate_api_key() -> str:
    """Generate API key for external integrations"""
    import secrets
    return f"twa_{secrets.token_urlsafe(32)}"


def verify_api_key(api_key: str) -> bool:
    """Verify API key format"""
    return api_key.startswith("twa_") and len(api_key) == 48


# Permission decorators and utilities
class Permission:
    """Permission constants"""
    CREATE_RFP = "create_rfp"
    READ_RFP = "read_rfp"
    UPDATE_RFP = "update_rfp"
    DELETE_RFP = "delete_rfp"
    
    CREATE_PROPOSAL = "create_proposal"
    READ_PROPOSAL = "read_proposal"
    UPDATE_PROPOSAL = "update_proposal"
    DELETE_PROPOSAL = "delete_proposal"
    
    CREATE_WORKFLOW = "create_workflow"
    READ_WORKFLOW = "read_workflow"
    UPDATE_WORKFLOW = "update_workflow"
    DELETE_WORKFLOW = "delete_workflow"
    EXECUTE_WORKFLOW = "execute_workflow"
    
    MANAGE_USERS = "manage_users"
    MANAGE_ORGANIZATION = "manage_organization"
    VIEW_ANALYTICS = "view_analytics"
    
    ADMIN_ACCESS = "admin_access"
    SUPER_ADMIN_ACCESS = "super_admin_access"


# Role-based permissions mapping
ROLE_PERMISSIONS = {
    "viewer": [
        Permission.READ_RFP,
        Permission.READ_PROPOSAL,
        Permission.READ_WORKFLOW,
    ],
    "user": [
        Permission.CREATE_RFP,
        Permission.READ_RFP,
        Permission.UPDATE_RFP,
        Permission.CREATE_PROPOSAL,
        Permission.READ_PROPOSAL,
        Permission.UPDATE_PROPOSAL,
        Permission.CREATE_WORKFLOW,
        Permission.READ_WORKFLOW,
        Permission.UPDATE_WORKFLOW,
        Permission.EXECUTE_WORKFLOW,
    ],
    "manager": [
        Permission.CREATE_RFP,
        Permission.READ_RFP,
        Permission.UPDATE_RFP,
        Permission.DELETE_RFP,
        Permission.CREATE_PROPOSAL,
        Permission.READ_PROPOSAL,
        Permission.UPDATE_PROPOSAL,
        Permission.DELETE_PROPOSAL,
        Permission.CREATE_WORKFLOW,
        Permission.READ_WORKFLOW,
        Permission.UPDATE_WORKFLOW,
        Permission.DELETE_WORKFLOW,
        Permission.EXECUTE_WORKFLOW,
        Permission.VIEW_ANALYTICS,
    ],
    "admin": [
        # All manager permissions plus:
        Permission.MANAGE_USERS,
        Permission.MANAGE_ORGANIZATION,
        Permission.ADMIN_ACCESS,
    ],
    "super_admin": [
        # All permissions
        Permission.SUPER_ADMIN_ACCESS,
    ]
}

# Flatten admin and super_admin permissions
ROLE_PERMISSIONS["admin"].extend(ROLE_PERMISSIONS["manager"])
ROLE_PERMISSIONS["super_admin"].extend(ROLE_PERMISSIONS["admin"])


def user_has_permission(user_role: str, permission: str) -> bool:
    """Check if user role has specific permission"""
    if user_role == "super_admin":
        return True  # Super admin has all permissions
    
    return permission in ROLE_PERMISSIONS.get(user_role, [])