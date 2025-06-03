"""
Main API v1 router with Release 5 enhanced features
"""
from fastapi import APIRouter

# Original routers from previous releases
from .auth_simple import router as auth_router
from .organizations import router as organizations_router
from .rfps import router as rfps_router

# Release 5: Enhanced RFP routers
from .rfp_enhanced import router as rfp_enhanced_router
from .rfp_documents import router as rfp_documents_router
from .rfp_templates import router as rfp_templates_router

# Release 7: AI Services
from .ai_services import router as ai_services_router

# Release 8: Analytics (temporarily disabled due to table conflicts)
# from .analytics_simple import router as analytics_router

api_router = APIRouter()

# Include original authentication and basic routes (backward compatibility)
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(organizations_router, prefix="/organizations", tags=["organizations"])
api_router.include_router(rfps_router, prefix="/rfps", tags=["rfps"])  # Original RFP endpoints

# Release 5: Enhanced RFP endpoints
api_router.include_router(rfp_enhanced_router, prefix="/rfps-enhanced", tags=["rfps-enhanced"])
api_router.include_router(rfp_documents_router, prefix="/rfps-enhanced", tags=["rfp-documents"])
api_router.include_router(rfp_templates_router, prefix="/rfp-templates", tags=["rfp-templates"])

# Release 7: AI Services endpoints
api_router.include_router(ai_services_router, prefix="/ai", tags=["ai-services"])

# Release 8: Analytics endpoints (temporarily disabled)
# api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])

# TODO: Add other routers for future releases
# api_router.include_router(users_router, prefix="/users", tags=["users"])
# api_router.include_router(proposals_router, prefix="/proposals", tags=["proposals"])
# api_router.include_router(workflows_router, prefix="/workflows", tags=["workflows"])
# api_router.include_router(agents_router, prefix="/agents", tags=["agents"])