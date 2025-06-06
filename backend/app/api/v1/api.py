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

# Release 8: Analytics
from .analytics_simple import router as analytics_router

# Release 9: Advanced Analytics
from .analytics_advanced import router as analytics_advanced_router
from .integrations import router as integrations_router
from .collaboration import router as collaboration_router
from .ai_advanced import router as ai_advanced_router

# Release 13: Module 1 - RFP Analysis
from .rfp_analysis import router as rfp_analysis_router

# Release 13: Document Generation Service
from .documents import router as documents_router

# Release 13: Module 2 - Compliance Analysis
from .compliance_analysis import router as compliance_analysis_router

# Release 15: Module 3 - Proposal Generation (Phase 3.1 Foundation)
from .proposal_generation_simple import router as proposal_generation_router

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

# Release 8: Analytics endpoints
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])

# Release 9: Advanced Analytics endpoints
api_router.include_router(analytics_advanced_router, prefix="", tags=["advanced-analytics"])

# Release 9: Third-party Integrations endpoints
api_router.include_router(integrations_router, prefix="/integrations", tags=["integrations"])

# Release 13: Module 1 - RFP Analysis endpoints
api_router.include_router(rfp_analysis_router, prefix="/rfp-analysis", tags=["rfp-analysis"])

# Release 13: Document Generation endpoints
api_router.include_router(documents_router, prefix="/documents", tags=["documents"])

# Release 13: Module 2 - Compliance Analysis endpoints
api_router.include_router(compliance_analysis_router, prefix="/compliance-analysis", tags=["compliance-analysis"])

# Release 15: Module 3 - Proposal Generation endpoints
api_router.include_router(proposal_generation_router, prefix="/proposal-generation", tags=["proposal-generation"])

# Release 9: Advanced Collaboration endpoints
api_router.include_router(collaboration_router, prefix="/collaboration", tags=["collaboration"])

# Release 9: Advanced AI endpoints
api_router.include_router(ai_advanced_router, prefix="/ai-advanced", tags=["ai-advanced"])

# TODO: Add other routers for future releases
# api_router.include_router(users_router, prefix="/users", tags=["users"])
# api_router.include_router(proposals_router, prefix="/proposals", tags=["proposals"])
# api_router.include_router(workflows_router, prefix="/workflows", tags=["workflows"])
# api_router.include_router(agents_router, prefix="/agents", tags=["agents"])