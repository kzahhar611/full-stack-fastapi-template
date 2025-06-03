"""
TenderWise AI - Simplified Main FastAPI application for Release 1
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from contextlib import asynccontextmanager
import time
import logging
import json
from uuid import UUID
from datetime import datetime

from .core.config import settings
from .core.database_simple import init_db
from .api.v1.api_simple import api_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Custom JSON encoder for UUIDs and other types
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    """
    # Startup
    logger.info("Starting TenderWise AI application...")
    
    # Initialize database with tables and admin user
    init_db()
    logger.info("Database initialized with admin user")
    
    yield
    
    # Shutdown
    logger.info("Shutting down TenderWise AI application...")


# Create FastAPI application
app = FastAPI(
    title="TenderWise AI",
    description="AI-powered platform for RFP analysis, proposal generation, and procurement automation",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom middleware for request timing
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation error",
            "errors": [
                {
                    "type": "validation_error",
                    "message": str(error["msg"]),
                    "field": ".".join(str(x) for x in error["loc"])
                }
                for error in exc.errors()
            ]
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal server error" if not settings.DEBUG else str(exc)
        }
    )


# Include API routers
app.include_router(api_router, prefix="/api/v1")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "environment": "development"
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to TenderWise AI",
        "version": "1.0.0",
        "docs": "/docs",
        "api": "/api/v1"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )