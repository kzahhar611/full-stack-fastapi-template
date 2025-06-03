"""
API v1 router for Release 2
"""
from fastapi import APIRouter

from .auth_simple import router as auth_router
from .organizations import router as organizations_router
from .rfps import router as rfps_router

api_router = APIRouter()

# Include all routes
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(organizations_router, prefix="/organizations", tags=["organizations"])
api_router.include_router(rfps_router, prefix="/rfps", tags=["rfps"])