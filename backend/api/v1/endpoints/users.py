"""
TenderWise AI - Users Endpoints
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_users():
    """Get all users"""
    # TODO: Implement get users logic
    return {"message": "Get users endpoint - Not implemented yet"}


@router.get("/me")
async def get_current_user():
    """Get current user profile"""
    # TODO: Implement get current user logic
    return {
        "email": "rfp@kzahhar.com",
        "full_name": "Admin User",
        "is_superuser": True,
        "is_active": True
    }


@router.put("/me")
async def update_current_user():
    """Update current user profile"""
    # TODO: Implement update user logic
    return {"message": "Update user endpoint - Not implemented yet"}