"""
TenderWise AI - Production FastAPI Application
Optimized for high performance and production deployment
"""
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import time
import logging
import os
from typing import Optional
import uvicorn

# Core imports
from .core.config import settings
from .core.database_enhanced import init_enhanced_db
from .core.cache import cache_service
from .core.performance import PerformanceMiddleware, performance_monitor
from .api.v1.api import api_router
from .services.ai.ai_config import ai_config

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/app.log') if os.path.exists('logs') else logging.StreamHandler()
    ]
)
logger = logging.getLogger("tenderwise_production")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown tasks"""
    
    # Startup tasks
    logger.info("🚀 Starting TenderWise AI Production Server...")
    
    try:
        # Initialize database
        logger.info("📊 Initializing database...")
        init_enhanced_db()
        
        # Initialize AI services
        logger.info("🧠 Initializing AI services...")
        ai_status = ai_config.initialize_ai_services()
        logger.info(f"AI Services: {ai_status}")
        
        # Warm up cache
        logger.info("⚡ Warming up cache service...")
        cache_health = cache_service.is_healthy()
        logger.info(f"Cache Status: {'✅ Healthy' if cache_health else '⚠️ Degraded'}")
        
        # Application ready
        logger.info("✅ TenderWise AI Production Server Ready!")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown tasks
    logger.info("🛑 Shutting down TenderWise AI...")
    
    try:
        # Clear cache if needed
        await cache_service.clear()
        logger.info("Cache cleared")
        
        # Final cleanup
        logger.info("✅ Shutdown complete")
        
    except Exception as e:
        logger.error(f"Shutdown error: {e}")


# Create FastAPI application with production settings
app = FastAPI(
    title="TenderWise AI - Production API",
    description="Enterprise RFP & Tendering Platform with AI-powered workflow automation",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan
)

# Security middleware - Add trusted hosts in production
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.tenderwise.ai"]
    )

# Performance middleware - Add GZip compression
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,
    compresslevel=6
)

# Performance monitoring middleware
app.add_middleware(PerformanceMiddleware)

# CORS middleware with production settings
cors_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://app.tenderwise.ai",
    "https://tenderwise.ai"
]

if settings.DEBUG:
    cors_origins.extend([
        "http://localhost:*",
        "http://127.0.0.1:*"
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time", "X-Cache-Status"]
)


# Custom exception handlers for production
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed logging"""
    logger.warning(f"Validation error on {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Validation error",
            "details": exc.errors()
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with proper logging"""
    if exc.status_code >= 500:
        logger.error(f"Server error on {request.url}: {exc.detail}")
    else:
        logger.warning(f"Client error on {request.url}: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors"""
    logger.error(f"Unexpected error on {request.url}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )


# Health check endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """Production health check with comprehensive status"""
    health_status = performance_monitor.get_health_status()
    cache_status = cache_service.is_healthy()
    
    return {
        "status": "healthy" if health_status["status"] in ["healthy", "warning"] else "unhealthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "environment": "production" if not settings.DEBUG else "development",
        "services": {
            "database": "healthy",
            "cache": "healthy" if cache_status else "degraded",
            "ai": "healthy" if ai_config.get_status()["initialized"] else "degraded"
        },
        "performance": {
            "health_score": health_status["health_score"],
            "uptime_seconds": health_status["uptime_seconds"],
            "issues": health_status["issues"]
        }
    }


@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check():
    """Detailed health check for monitoring systems"""
    return {
        "system": performance_monitor.get_system_metrics(),
        "api": performance_monitor.get_api_metrics(15),
        "cache": cache_service.get_stats(),
        "endpoints": performance_monitor.get_endpoint_stats(10),
        "ai_services": ai_config.get_status()
    }


@app.get("/metrics", tags=["Monitoring"])
async def get_metrics():
    """Prometheus-style metrics endpoint"""
    api_metrics = performance_monitor.get_api_metrics(60)
    cache_stats = cache_service.get_stats()
    
    metrics = [
        f"# HELP tenderwise_requests_total Total number of HTTP requests",
        f"# TYPE tenderwise_requests_total counter",
        f"tenderwise_requests_total {api_metrics['total_requests']}",
        "",
        f"# HELP tenderwise_response_time_seconds Response time in seconds",
        f"# TYPE tenderwise_response_time_seconds histogram",
        f"tenderwise_response_time_seconds_sum {api_metrics['total_requests'] * api_metrics['avg_response_time']}",
        f"tenderwise_response_time_seconds_count {api_metrics['total_requests']}",
        "",
        f"# HELP tenderwise_cache_hits_total Total cache hits",
        f"# TYPE tenderwise_cache_hits_total counter",
        f"tenderwise_cache_hits_total {cache_stats['hits']}",
        "",
        f"# HELP tenderwise_cache_hit_rate Cache hit rate percentage",
        f"# TYPE tenderwise_cache_hit_rate gauge",
        f"tenderwise_cache_hit_rate {cache_stats['hit_rate_percent']}",
    ]
    
    return Response(
        content="\n".join(metrics),
        media_type="text/plain"
    )


# Include API routers
app.include_router(api_router, prefix="/api/v1")


# Production server configuration
def create_production_app():
    """Create production-configured application"""
    return app


if __name__ == "__main__":
    # Production server settings
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    workers = int(os.getenv("WORKERS", 1))
    
    if settings.DEBUG:
        # Development mode
        uvicorn.run(
            "app.main_production:app",
            host=host,
            port=port,
            reload=True,
            log_level="info"
        )
    else:
        # Production mode with gunicorn-compatible setup
        logger.info(f"Starting production server on {host}:{port}")
        uvicorn.run(
            app,
            host=host,
            port=port,
            workers=workers,
            log_level="warning",
            access_log=False  # Use custom logging
        )