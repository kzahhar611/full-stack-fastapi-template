"""
Main API v1 router
"""
from fastapi import APIRouter

from .auth import router as auth_router

api_router = APIRouter()

# Include authentication routes
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])

# TODO: Add other routers
# api_router.include_router(users_router, prefix="/users", tags=["users"])
# api_router.include_router(organizations_router, prefix="/organizations", tags=["organizations"])
# api_router.include_router(rfps_router, prefix="/rfps", tags=["rfps"])
# api_router.include_router(proposals_router, prefix="/proposals", tags=["proposals"])
# api_router.include_router(workflows_router, prefix="/workflows", tags=["workflows"])
# api_router.include_router(agents_router, prefix="/agents", tags=["agents"])