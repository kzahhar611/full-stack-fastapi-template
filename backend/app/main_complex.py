"""
TenderWise AI - Main FastAPI Application
Enterprise-grade AI platform for RFP and tendering automation
"""

import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .api.v1.api import api_router
from app.core.config import get_settings
from app.core.logging import setup_logging, logger
from app.core.middleware import (
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
    TimingMiddleware
)
from app.core.database import engine, init_db
from app.core.exceptions import TenderWiseException, ValidationException


# Application lifespan events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events"""
    logger.info("🚀 Starting TenderWise AI application...")
    
    # Startup
    try:
        # Initialize database
        await init_db()
        logger.info("✅ Database initialized successfully")
        
        # Initialize AI providers
        from app.services.ai.provider_manager import AIProviderManager
        provider_manager = AIProviderManager()
        await provider_manager.initialize()
        logger.info("✅ AI providers initialized successfully")
        
        # Initialize workflow engine
        from app.workflows.engine.workflow_engine import WorkflowEngine
        workflow_engine = WorkflowEngine()
        await workflow_engine.initialize()
        logger.info("✅ Workflow engine initialized successfully")
        
        logger.info("🎉 TenderWise AI application started successfully!")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        raise
    finally:
        # Shutdown
        logger.info("🛑 Shutting down TenderWise AI application...")
        
        # Cleanup resources
        if hasattr(engine, 'dispose'):
            await engine.dispose()
            logger.info("✅ Database connections closed")
        
        logger.info("👋 TenderWise AI application stopped")


# Get application settings
settings = get_settings()

# Setup logging
setup_logging()

# Create FastAPI application
app = FastAPI(
    title="TenderWise AI",
    description="Enterprise AI Platform for RFP & Tendering Automation",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
    # Custom OpenAPI settings
    openapi_tags=[
        {
            "name": "auth",
            "description": "Authentication and authorization operations"
        },
        {
            "name": "organizations", 
            "description": "Multi-tenant organization management"
        },
        {
            "name": "users",
            "description": "User management and profiles"
        },
        {
            "name": "ai-agents",
            "description": "AI agent creation and management"
        },
        {
            "name": "workflows",
            "description": "Visual workflow designer and execution"
        },
        {
            "name": "rfps",
            "description": "RFP creation and management"
        },
        {
            "name": "proposals",
            "description": "Proposal generation and analysis"
        },
        {
            "name": "documents",
            "description": "Document processing and templates"
        },
        {
            "name": "analytics",
            "description": "Analytics and reporting"
        },
        {
            "name": "admin",
            "description": "Administrative operations"
        },
        {
            "name": "health",
            "description": "Health checks and system status"
        }
    ]
)

# =============================================================================
# MIDDLEWARE CONFIGURATION
# =============================================================================

# Security Headers Middleware (should be first)
app.add_middleware(SecurityHeadersMiddleware)

# CORS Middleware
if settings.ENABLE_CORS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Trusted Host Middleware
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )

# Compression Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Rate Limiting Middleware
if settings.ENABLE_RATE_LIMITING:
    app.add_middleware(RateLimitMiddleware)

# Request Logging Middleware
app.add_middleware(RequestLoggingMiddleware)

# Timing Middleware (should be last)
app.add_middleware(TimingMiddleware)

# =============================================================================
# EXCEPTION HANDLERS
# =============================================================================

@app.exception_handler(TenderWiseException)
async def tenderwise_exception_handler(request: Request, exc: TenderWiseException):
    """Handle custom TenderWise exceptions"""
    logger.error(f"TenderWise error: {exc.detail}", extra={"error_code": exc.error_code})
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "error_code": exc.error_code,
            "message": exc.detail,
            "timestamp": time.time()
        }
    )

@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    """Handle validation exceptions"""
    logger.warning(f"Validation error: {exc.detail}")
    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "error_code": "VALIDATION_ERROR",
            "message": exc.detail,
            "errors": exc.errors,
            "timestamp": time.time()
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP error {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "error_code": f"HTTP_{exc.status_code}",
            "message": exc.detail,
            "timestamp": time.time()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred" if not settings.DEBUG else str(exc),
            "timestamp": time.time()
        }
    )

# =============================================================================
# ROUTES
# =============================================================================

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }

# Root endpoint
@app.get("/", tags=["health"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "TenderWise AI",
        "description": "Enterprise AI Platform for RFP & Tendering Automation",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs" if settings.DEBUG else None,
        "api_url": f"{settings.API_V1_STR}",
        "timestamp": time.time()
    }

# Metrics endpoint (for Prometheus)
if settings.ENABLE_METRICS:
    @app.get("/metrics", tags=["health"])
    async def metrics():
        """Prometheus metrics endpoint"""
        from app.core.metrics import generate_metrics
        return Response(
            content=generate_metrics(),
            media_type="text/plain"
        )

# =============================================================================
# STARTUP MESSAGE
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting TenderWise AI in development mode...")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        reload_dirs=["app"] if settings.DEBUG else None,
        log_level="info" if settings.DEBUG else "warning",
        access_log=settings.DEBUG
    )