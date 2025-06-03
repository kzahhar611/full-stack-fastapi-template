"""
TenderWise AI - Authentication Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint"""
    # TODO: Implement authentication logic
    if form_data.username == "rfp@kzahhar.com" and form_data.password == "password123":
        return {
            "access_token": "dummy_token",
            "token_type": "bearer",
            "user": {
                "email": form_data.username,
                "full_name": "Admin User",
                "is_superuser": True
            }
        }
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/register")
async def register():
    """Register endpoint"""
    # TODO: Implement registration logic
    return {"message": "Registration endpoint - Not implemented yet"}


@router.post("/refresh")
async def refresh_token():
    """Refresh token endpoint"""
    # TODO: Implement token refresh logic
    return {"message": "Token refresh endpoint - Not implemented yet"}