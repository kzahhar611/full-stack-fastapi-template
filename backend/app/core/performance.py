"""
TenderWise AI - Performance Monitoring and Optimization
Real-time performance tracking and optimization features
"""
import time
import psutil
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """
    Real-time performance monitoring system
    Tracks API response times, system resources, and performance metrics
    """
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.request_history = deque(maxlen=max_history)
        self.endpoint_stats = defaultdict(lambda: {
            "count": 0,
            "total_time": 0,
            "min_time": float('inf'),
            "max_time": 0,
            "recent_times": deque(maxlen=100)
        })
        self.error_counts = defaultdict(int)
        self.start_time = datetime.utcnow()
        
    def record_request(self, 
                      endpoint: str, 
                      method: str, 
                      response_time: float, 
                      status_code: int,
                      request_size: int = 0,
                      response_size: int = 0):
        """Record a request for performance analysis"""
        
        # Record in history
        self.request_history.append({
            "timestamp": datetime.utcnow(),
            "endpoint": endpoint,
            "method": method,
            "response_time": response_time,
            "status_code": status_code,
            "request_size": request_size,
            "response_size": response_size
        })
        
        # Update endpoint stats
        key = f"{method} {endpoint}"
        stats = self.endpoint_stats[key]
        stats["count"] += 1
        stats["total_time"] += response_time
        stats["min_time"] = min(stats["min_time"], response_time)
        stats["max_time"] = max(stats["max_time"], response_time)
        stats["recent_times"].append(response_time)
        
        # Track errors
        if status_code >= 400:
            self.error_counts[status_code] += 1
    
    def get_system_metrics(self) -> Dict:
        """Get current system performance metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available / 1024 / 1024,
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / 1024 / 1024 / 1024,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {"error": str(e)}
    
    def get_api_metrics(self, time_window_minutes: int = 15) -> Dict:
        """Get API performance metrics for specified time window"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)
        recent_requests = [r for r in self.request_history if r["timestamp"] > cutoff_time]
        
        if not recent_requests:
            return {
                "time_window_minutes": time_window_minutes,
                "total_requests": 0,
                "avg_response_time": 0,
                "error_rate": 0,
                "requests_per_minute": 0
            }
        
        total_requests = len(recent_requests)
        total_response_time = sum(r["response_time"] for r in recent_requests)
        avg_response_time = total_response_time / total_requests
        
        error_requests = sum(1 for r in recent_requests if r["status_code"] >= 400)
        error_rate = (error_requests / total_requests) * 100
        
        requests_per_minute = total_requests / time_window_minutes
        
        # Get response time percentiles
        response_times = sorted([r["response_time"] for r in recent_requests])
        p50 = response_times[int(len(response_times) * 0.5)] if response_times else 0
        p95 = response_times[int(len(response_times) * 0.95)] if response_times else 0
        p99 = response_times[int(len(response_times) * 0.99)] if response_times else 0
        
        return {
            "time_window_minutes": time_window_minutes,
            "total_requests": total_requests,
            "avg_response_time": round(avg_response_time, 3),
            "min_response_time": round(min(r["response_time"] for r in recent_requests), 3),
            "max_response_time": round(max(r["response_time"] for r in recent_requests), 3),
            "p50_response_time": round(p50, 3),
            "p95_response_time": round(p95, 3),
            "p99_response_time": round(p99, 3),
            "error_rate": round(error_rate, 2),
            "requests_per_minute": round(requests_per_minute, 2),
            "error_breakdown": dict(self.error_counts)
        }
    
    def get_endpoint_stats(self, limit: int = 20) -> List[Dict]:
        """Get performance stats for top endpoints"""
        endpoint_list = []
        
        for endpoint, stats in self.endpoint_stats.items():
            if stats["count"] > 0:
                avg_time = stats["total_time"] / stats["count"]
                recent_avg = sum(stats["recent_times"]) / len(stats["recent_times"]) if stats["recent_times"] else 0
                
                endpoint_list.append({
                    "endpoint": endpoint,
                    "request_count": stats["count"],
                    "avg_response_time": round(avg_time, 3),
                    "recent_avg_response_time": round(recent_avg, 3),
                    "min_response_time": round(stats["min_time"], 3),
                    "max_response_time": round(stats["max_time"], 3)
                })
        
        # Sort by request count and return top endpoints
        endpoint_list.sort(key=lambda x: x["request_count"], reverse=True)
        return endpoint_list[:limit]
    
    def get_health_status(self) -> Dict:
        """Get overall system health status"""
        system_metrics = self.get_system_metrics()
        api_metrics = self.get_api_metrics(5)  # Last 5 minutes
        
        # Determine health status
        health_score = 100
        issues = []
        
        # Check system resources
        if system_metrics.get("cpu_percent", 0) > 80:
            health_score -= 20
            issues.append("High CPU usage")
        
        if system_metrics.get("memory_percent", 0) > 85:
            health_score -= 20
            issues.append("High memory usage")
        
        if system_metrics.get("disk_percent", 0) > 90:
            health_score -= 15
            issues.append("Low disk space")
        
        # Check API performance
        if api_metrics.get("avg_response_time", 0) > 2.0:
            health_score -= 15
            issues.append("Slow API response times")
        
        if api_metrics.get("error_rate", 0) > 5:
            health_score -= 20
            issues.append("High error rate")
        
        # Determine status
        if health_score >= 90:
            status = "healthy"
        elif health_score >= 70:
            status = "warning"
        else:
            status = "critical"
        
        return {
            "status": status,
            "health_score": max(0, health_score),
            "issues": issues,
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "system_metrics": system_metrics,
            "api_metrics": api_metrics
        }


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


class PerformanceMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track API performance automatically
    """
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Get request size
        request_size = 0
        if hasattr(request, "body"):
            try:
                body = await request.body()
                request_size = len(body) if body else 0
            except:
                pass
        
        # Process request
        response = await call_next(request)
        
        # Calculate metrics
        process_time = time.time() - start_time
        endpoint = request.url.path
        method = request.method
        status_code = response.status_code
        
        # Get response size
        response_size = 0
        if hasattr(response, "body"):
            try:
                response_size = len(response.body) if response.body else 0
            except:
                pass
        
        # Record performance data
        performance_monitor.record_request(
            endpoint=endpoint,
            method=method,
            response_time=process_time,
            status_code=status_code,
            request_size=request_size,
            response_size=response_size
        )
        
        # Add performance headers
        response.headers["X-Process-Time"] = str(round(process_time, 4))
        response.headers["X-Timestamp"] = str(int(time.time()))
        
        return response


# Performance optimization utilities
class ResponseOptimizer:
    """Utilities for optimizing API responses"""
    
    @staticmethod
    def compress_response(data: dict, remove_nulls: bool = True) -> dict:
        """Compress response by removing null values and optimizing structure"""
        if not isinstance(data, dict):
            return data
        
        compressed = {}
        for key, value in data.items():
            if remove_nulls and value is None:
                continue
            
            if isinstance(value, dict):
                compressed[key] = ResponseOptimizer.compress_response(value, remove_nulls)
            elif isinstance(value, list):
                compressed[key] = [
                    ResponseOptimizer.compress_response(item, remove_nulls) 
                    if isinstance(item, dict) else item 
                    for item in value
                ]
            else:
                compressed[key] = value
        
        return compressed
    
    @staticmethod
    def paginate_response(data: List, page: int = 1, size: int = 20) -> dict:
        """Paginate large responses for better performance"""
        total = len(data)
        start = (page - 1) * size
        end = start + size
        
        return {
            "data": data[start:end],
            "pagination": {
                "page": page,
                "size": size,
                "total": total,
                "pages": (total + size - 1) // size,
                "has_next": end < total,
                "has_prev": page > 1
            }
        }


# Database query optimization helpers
class QueryOptimizer:
    """Utilities for optimizing database queries"""
    
    @staticmethod
    def get_optimized_query_options(include_relationships: bool = False) -> dict:
        """Get optimized query options for SQLAlchemy"""
        options = {
            "execution_options": {
                "compiled_cache": {},
                "autocommit": False
            }
        }
        
        if include_relationships:
            options["joinedload"] = True
        
        return options
    
    @staticmethod
    def batch_queries(queries: List, batch_size: int = 100):
        """Execute queries in batches for better performance"""
        for i in range(0, len(queries), batch_size):
            yield queries[i:i + batch_size]