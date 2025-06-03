"""
TenderWise AI - API v1 Router
"""

from fastapi import APIRouter

from api.v1.endpoints import auth, users, rfps, proposals, projects

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(rfps.router, prefix="/rfps", tags=["RFPs"])
api_router.include_router(proposals.router, prefix="/proposals", tags=["Proposals"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])