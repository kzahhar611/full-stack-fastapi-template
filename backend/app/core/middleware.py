"""
TenderWise AI - Middleware Components
Custom middleware for the FastAPI application
"""

import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger("tenderwise.middleware")

class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware to add timing information to responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log requests"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url}")
        
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"Response: {response.status_code} - "
            f"{request.method} {request.url} - "
            f"Time: {process_time:.4f}s"
        )
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Basic rate limiting middleware"""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Basic implementation - could be enhanced with Redis
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old entries
        cutoff_time = current_time - self.period
        self.clients = {
            ip: times for ip, times in self.clients.items()
            if any(t > cutoff_time for t in times)
        }
        
        # Check rate limit
        if client_ip in self.clients:
            recent_calls = [t for t in self.clients[client_ip] if t > cutoff_time]
            if len(recent_calls) >= self.calls:
                logger.warning(f"Rate limit exceeded for {client_ip}")
                return Response(
                    content="Rate limit exceeded",
                    status_code=429,
                    headers={"Retry-After": str(self.period)}
                )
            self.clients[client_ip] = recent_calls + [current_time]
        else:
            self.clients[client_ip] = [current_time]
        
        return await call_next(request)