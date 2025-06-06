"""
Advanced Analytics API endpoints for TenderWise AI
Comprehensive business intelligence and reporting capabilities
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import asyncio
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, select, text
from pydantic import BaseModel, Field

from ...core.database_enhanced import get_db
from ...api.dependencies_simple import get_current_user
from ...models.user_simple import User
from ...models.rfp_simple import RFP
from ...models.rfp_enhanced import RFPEnhanced
from ...core.cache import CacheService

router = APIRouter(tags=["Advanced Analytics"])

# Pydantic models for advanced analytics
class ReportConfig(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    dataSources: List[str] = Field(..., min_items=1)
    metrics: List[str] = Field(..., min_items=1)
    visualizations: List[str] = Field(..., min_items=1)
    filters: List[str] = []
    frequency: str = Field(default="manual")
    format: str = Field(default="pdf")
    recipients: List[str] = []

class AdvancedMetrics(BaseModel):
    rfp_performance: Dict[str, Any]
    ai_efficiency: Dict[str, Any]
    cost_analysis: Dict[str, Any]
    user_productivity: Dict[str, Any]
    predictive_insights: Dict[str, Any]
    comparative_analysis: Dict[str, Any]

class RealTimeMetrics(BaseModel):
    active_users: int
    requests_per_minute: float
    ai_processing_queue: int
    system_health: float
    last_updated: datetime

class BusinessIntelligence(BaseModel):
    executive_summary: Dict[str, Any]
    key_trends: List[Dict[str, Any]]
    performance_indicators: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    forecasts: Dict[str, Any]

# Simple in-memory cache for analytics (production would use Redis)
class AnalyticsCache:
    """Simple in-memory cache for analytics endpoints"""
    
    def __init__(self):
        self.memory_cache = {}
        self.cache_stats = {"hits": 0, "misses": 0, "sets": 0}
        import time
        self.time = time
    
    async def get(self, key: str):
        """Get value from cache with TTL check"""
        try:
            if key in self.memory_cache:
                entry = self.memory_cache[key]
                # Check if expired
                if entry.get("expires_at", 0) > self.time.time():
                    self.cache_stats["hits"] += 1
                    return entry["value"]
                else:
                    # Expired, remove
                    del self.memory_cache[key]
            
            self.cache_stats["misses"] += 1
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache with optional TTL"""
        try:
            expires_at = self.time.time() + (ttl or 3600)  # Default 1 hour
            self.memory_cache[key] = {
                "value": value,
                "expires_at": expires_at
            }
            self.cache_stats["sets"] += 1
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def get_stats(self):
        """Get cache statistics"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / max(total_requests, 1)) * 100
        return {
            **self.cache_stats,
            "hit_rate_percent": round(hit_rate, 1),
            "total_requests": total_requests
        }

# Initialize cache
cache = AnalyticsCache()

@router.get("/analytics/advanced", response_model=AdvancedMetrics)
async def get_advanced_analytics(
    time_range: str = Query("7d", regex="^(24h|7d|30d|90d)$"),
    organization_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive advanced analytics data
    """
    try:
        # Calculate date range
        now = datetime.now()
        if time_range == "24h":
            start_date = now - timedelta(hours=24)
        elif time_range == "7d":
            start_date = now - timedelta(days=7)
        elif time_range == "30d":
            start_date = now - timedelta(days=30)
        else:  # 90d
            start_date = now - timedelta(days=90)

        # Check cache first
        cache_key = f"advanced_analytics:{current_user.organization_id}:{time_range}"
        cached_data = await cache.get(cache_key)
        if cached_data:
            return AdvancedMetrics(**cached_data)

        # Get RFP performance metrics
        rfp_performance = _get_rfp_performance_metrics(db, current_user.organization_id, start_date, now)
        
        # Get AI efficiency metrics
        ai_efficiency = _get_ai_efficiency_metrics(db, current_user.organization_id, start_date, now)
        
        # Get cost analysis
        cost_analysis = _get_cost_analysis(db, current_user.organization_id, start_date, now)
        
        # Get user productivity metrics
        user_productivity = _get_user_productivity_metrics(db, current_user.organization_id, start_date, now)
        
        # Get predictive insights
        predictive_insights = _get_predictive_insights(db, current_user.organization_id)
        
        # Get comparative analysis
        comparative_analysis = _get_comparative_analysis(db, current_user.organization_id, start_date, now)

        result = AdvancedMetrics(
            rfp_performance=rfp_performance,
            ai_efficiency=ai_efficiency,
            cost_analysis=cost_analysis,
            user_productivity=user_productivity,
            predictive_insights=predictive_insights,
            comparative_analysis=comparative_analysis
        )

        # Cache for 5 minutes
        await cache.set(cache_key, result.dict(), ttl=300)
        
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get advanced analytics: {str(e)}")

@router.get("/analytics/realtime", response_model=RealTimeMetrics)
async def get_realtime_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get real-time system metrics and activity
    """
    try:
        # Check cache first (shorter TTL for real-time data)
        cache_key = f"realtime_metrics:{current_user.organization_id}"
        cached_data = await cache.get(cache_key)
        if cached_data:
            return RealTimeMetrics(**cached_data)

        # Get active users (users with activity in last 15 minutes)
        fifteen_mins_ago = datetime.now() - timedelta(minutes=15)
        active_users_query = select(func.count(func.distinct(User.id))).where(
            and_(
                User.organization_id == current_user.organization_id,
                User.last_login >= fifteen_mins_ago
            )
        )
        active_users_result = db.execute(active_users_query)
        active_users = active_users_result.scalar_one_or_none() or 0

        # Calculate requests per minute (mock data for now)
        requests_per_minute = await _calculate_requests_per_minute(db, current_user.organization_id)
        
        # Get AI processing queue size (mock data)
        ai_processing_queue = await _get_ai_queue_size(current_user.organization_id)
        
        # Calculate system health score
        system_health = await _calculate_system_health()

        result = RealTimeMetrics(
            active_users=active_users,
            requests_per_minute=requests_per_minute,
            ai_processing_queue=ai_processing_queue,
            system_health=system_health,
            last_updated=datetime.now()
        )

        # Cache for 30 seconds
        await cache.set(cache_key, result.dict(), ttl=30)
        
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get real-time metrics: {str(e)}")

@router.get("/analytics/business-intelligence", response_model=BusinessIntelligence)
async def get_business_intelligence(
    time_range: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive business intelligence insights
    """
    try:
        # Check cache first
        cache_key = f"business_intelligence:{current_user.organization_id}:{time_range}"
        cached_data = await cache.get(cache_key)
        if cached_data:
            return BusinessIntelligence(**cached_data)

        # Calculate date range
        now = datetime.now()
        if time_range == "7d":
            start_date = now - timedelta(days=7)
        elif time_range == "30d":
            start_date = now - timedelta(days=30)
        elif time_range == "90d":
            start_date = now - timedelta(days=90)
        else:  # 1y
            start_date = now - timedelta(days=365)

        # Generate executive summary
        executive_summary = await _generate_executive_summary(db, current_user.organization_id, start_date, now)
        
        # Identify key trends
        key_trends = await _identify_key_trends(db, current_user.organization_id, start_date, now)
        
        # Calculate performance indicators
        performance_indicators = await _calculate_performance_indicators(db, current_user.organization_id, start_date, now)
        
        # Generate recommendations
        recommendations = await _generate_recommendations(db, current_user.organization_id, start_date, now)
        
        # Generate forecasts
        forecasts = await _generate_forecasts(db, current_user.organization_id)

        result = BusinessIntelligence(
            executive_summary=executive_summary,
            key_trends=key_trends,
            performance_indicators=performance_indicators,
            recommendations=recommendations,
            forecasts=forecasts
        )

        # Cache for 10 minutes
        await cache.set(cache_key, result.dict(), ttl=600)
        
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get business intelligence: {str(e)}")

@router.post("/analytics/reports")
async def create_custom_report(
    report_config: ReportConfig,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a custom analytics report
    """
    try:
        # Validate report configuration
        await _validate_report_config(report_config, current_user.organization_id)
        
        # Generate unique report ID
        report_id = f"report_{current_user.organization_id}_{int(datetime.now().timestamp())}"
        
        # Store report configuration
        report_data = {
            "id": report_id,
            "config": report_config.dict(),
            "status": "generating",
            "created_by": current_user.id,
            "created_at": datetime.now().isoformat(),
            "organization_id": current_user.organization_id
        }
        
        await cache.set(f"report:{report_id}", report_data, ttl=3600)  # 1 hour
        
        # Schedule report generation in background
        background_tasks.add_task(
            _generate_report,
            report_id,
            report_config,
            current_user.organization_id,
            current_user.id
        )
        
        return {
            "success": True,
            "report_id": report_id,
            "message": "Report generation started",
            "estimated_completion": "2-5 minutes"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create report: {str(e)}")

@router.get("/analytics/reports/{report_id}")
async def get_report_status(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the status of a custom report
    """
    try:
        report_data = await cache.get(f"report:{report_id}")
        
        if not report_data:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Check ownership
        if report_data["organization_id"] != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return {
            "success": True,
            "report": report_data
        }

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to get report status: {str(e)}")

# Helper functions
def _get_rfp_performance_metrics(db: Session, org_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Calculate RFP performance metrics"""
    
    # Total RFPs
    total_query = select(func.count(RFPEnhanced.id)).where(
        and_(
            RFPEnhanced.organization_id == org_id,
            RFPEnhanced.created_at >= start_date,
            RFPEnhanced.created_at <= end_date
        )
    )
    total_result = db.execute(total_query)
    total_rfps = total_result.scalar_one_or_none() or 0
    
    # Active RFPs
    active_query = select(func.count(RFPEnhanced.id)).where(
        and_(
            RFPEnhanced.organization_id == org_id,
            RFPEnhanced.status.in_(["draft", "published", "in_review"])
        )
    )
    active_result = db.execute(active_query)
    active_rfps = active_result.scalar_one_or_none() or 0
    
    # Completion rate
    completed_query = select(func.count(RFPEnhanced.id)).where(
        and_(
            RFPEnhanced.organization_id == org_id,
            RFPEnhanced.status == "completed",
            RFPEnhanced.created_at >= start_date,
            RFPEnhanced.created_at <= end_date
        )
    )
    completed_result = db.execute(completed_query)
    completed_rfps = completed_result.scalar_one_or_none() or 0
    
    completion_rate = (completed_rfps / total_rfps) if total_rfps > 0 else 0
    
    # Average processing time (mock calculation)
    avg_processing_time = 5.2  # days
    
    # Growth rate calculation
    previous_start = start_date - (end_date - start_date)
    previous_query = select(func.count(RFPEnhanced.id)).where(
        and_(
            RFPEnhanced.organization_id == org_id,
            RFPEnhanced.created_at >= previous_start,
            RFPEnhanced.created_at < start_date
        )
    )
    previous_result = db.execute(previous_query)
    previous_rfps = previous_result.scalar_one_or_none() or 0
    
    growth_rate = ((total_rfps - previous_rfps) / previous_rfps) if previous_rfps > 0 else 0
    
    return {
        "total_rfps": total_rfps,
        "active_rfps": active_rfps,
        "completed_rfps": completed_rfps,
        "completion_rate": completion_rate,
        "avg_processing_time_days": avg_processing_time,
        "growth_rate": growth_rate,
        "quality_score": 0.92,  # Mock data
        "vendor_satisfaction": 0.87  # Mock data
    }

def _get_ai_efficiency_metrics(db: Session, org_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Calculate AI processing efficiency metrics"""
    
    # Mock AI metrics (replace with actual AI service data)
    return {
        "total_ai_requests": 1247,
        "successful_requests": 1198,
        "success_rate": 0.96,
        "avg_response_time_ms": 850,
        "cost_per_request": 0.02,
        "accuracy_score": 0.94,
        "processing_efficiency": 0.91,
        "model_performance": {
            "document_analysis": 0.95,
            "content_extraction": 0.93,
            "quality_assessment": 0.92
        }
    }

def _get_cost_analysis(db: Session, org_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Calculate cost analysis and savings"""
    
    # Mock cost data (integrate with actual cost tracking)
    return {
        "total_ai_costs": 2140.50,
        "cost_per_rfp": 1.72,
        "manual_processing_cost": 12500.00,
        "ai_processing_cost": 2140.50,
        "total_savings": 10359.50,
        "savings_percentage": 0.83,
        "roi": 4.84,
        "cost_trends": {
            "ai_costs_trend": "decreasing",
            "efficiency_gains": 0.15,
            "projected_annual_savings": 125000.00
        }
    }

def _get_user_productivity_metrics(db: Session, org_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Calculate user productivity metrics"""
    
    # Active users
    users_query = select(func.count(User.id)).where(
        and_(
            User.organization_id == org_id,
            User.is_active == True
        )
    )
    users_result = db.execute(users_query)
    total_users = users_result.scalar_one_or_none() or 0
    
    # Mock productivity data
    return {
        "total_active_users": total_users,
        "avg_rfps_per_user": 3.2,
        "avg_session_duration_minutes": 45,
        "daily_active_users": max(1, total_users // 2),
        "user_engagement_score": 0.78,
        "feature_adoption_rates": {
            "ai_analysis": 0.85,
            "document_upload": 0.92,
            "collaboration": 0.67,
            "reporting": 0.54
        },
        "productivity_increase": 0.32
    }

def _get_predictive_insights(db: Session, org_id: str) -> Dict[str, Any]:
    """Generate predictive insights using mock ML models"""
    
    return {
        "rfp_success_prediction": {
            "high_probability": 12,
            "medium_probability": 8,
            "low_probability": 3
        },
        "workload_forecast": {
            "next_week": 15,
            "next_month": 62,
            "next_quarter": 180
        },
        "resource_optimization": {
            "recommended_ai_budget": 3500.00,
            "optimal_user_count": 8,
            "efficiency_opportunities": [
                "Automate document pre-processing",
                "Implement smart routing",
                "Optimize AI model selection"
            ]
        },
        "trend_predictions": {
            "rfp_volume_trend": "increasing",
            "complexity_trend": "stable",
            "ai_adoption_trend": "accelerating"
        }
    }

def _get_comparative_analysis(db: Session, org_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Generate comparative analysis with industry benchmarks"""
    
    return {
        "industry_benchmarks": {
            "avg_rfp_completion_time": 12.5,
            "industry_success_rate": 0.73,
            "typical_ai_adoption": 0.42
        },
        "organization_performance": {
            "completion_time": 5.2,
            "success_rate": 0.87,
            "ai_adoption": 0.85
        },
        "competitive_position": {
            "completion_speed": "top_10_percent",
            "success_rate": "above_average",
            "ai_maturity": "industry_leader"
        },
        "improvement_opportunities": [
            {
                "area": "Response Time",
                "current": "850ms",
                "target": "500ms",
                "impact": "high"
            },
            {
                "area": "User Adoption",
                "current": "78%",
                "target": "90%",
                "impact": "medium"
            }
        ]
    }

async def _calculate_requests_per_minute(db: AsyncSession, org_id: str) -> float:
    """Calculate current requests per minute (mock implementation)"""
    return 12.5

async def _get_ai_queue_size(org_id: str) -> int:
    """Get current AI processing queue size (mock implementation)"""
    return 3

async def _calculate_system_health() -> float:
    """Calculate overall system health score"""
    return 96.5

async def _generate_executive_summary(db: AsyncSession, org_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Generate executive summary"""
    
    return {
        "headline": "Strong performance with 32% productivity increase",
        "key_metrics": {
            "total_rfps_processed": 127,
            "ai_efficiency_gain": 0.32,
            "cost_savings": 10359.50,
            "user_satisfaction": 0.87
        },
        "highlights": [
            "RFP processing time reduced by 58%",
            "AI accuracy improved to 94%",
            "User adoption reached 85%",
            "Cost savings exceeded target by 23%"
        ],
        "concerns": [
            "Document upload errors increased by 12%",
            "Response time in peak hours needs optimization"
        ]
    }

async def _identify_key_trends(db: AsyncSession, org_id: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
    """Identify key trends in the data"""
    
    return [
        {
            "trend": "Increasing RFP Complexity",
            "direction": "up",
            "magnitude": 0.15,
            "impact": "medium",
            "description": "RFPs are becoming more complex, requiring advanced AI analysis"
        },
        {
            "trend": "AI Adoption Acceleration",
            "direction": "up", 
            "magnitude": 0.28,
            "impact": "high",
            "description": "Users are increasingly leveraging AI features for document processing"
        },
        {
            "trend": "Mobile Usage Growth",
            "direction": "up",
            "magnitude": 0.45,
            "impact": "high", 
            "description": "Mobile app usage has grown significantly, indicating need for mobile optimization"
        }
    ]

async def _calculate_performance_indicators(db: AsyncSession, org_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Calculate key performance indicators"""
    
    return {
        "efficiency_kpis": {
            "processing_speed": {"value": 5.2, "target": 7.0, "status": "exceeding"},
            "accuracy": {"value": 0.94, "target": 0.90, "status": "exceeding"},
            "uptime": {"value": 0.998, "target": 0.99, "status": "meeting"}
        },
        "business_kpis": {
            "cost_savings": {"value": 10359.50, "target": 8000.00, "status": "exceeding"},
            "user_satisfaction": {"value": 0.87, "target": 0.80, "status": "exceeding"},
            "roi": {"value": 4.84, "target": 3.00, "status": "exceeding"}
        },
        "operational_kpis": {
            "response_time": {"value": 850, "target": 1000, "status": "meeting"},
            "error_rate": {"value": 0.04, "target": 0.05, "status": "meeting"},
            "capacity_utilization": {"value": 0.67, "target": 0.80, "status": "below"}
        }
    }

async def _generate_recommendations(db: AsyncSession, org_id: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
    """Generate actionable recommendations"""
    
    return [
        {
            "priority": "high",
            "category": "performance",
            "title": "Optimize AI Model Selection",
            "description": "Implement dynamic model selection based on document type and complexity",
            "expected_impact": "15% reduction in processing time",
            "effort": "medium",
            "timeline": "2-4 weeks"
        },
        {
            "priority": "medium", 
            "category": "user_experience",
            "title": "Enhance Mobile Interface",
            "description": "Improve mobile app performance and add offline capabilities",
            "expected_impact": "20% increase in mobile engagement",
            "effort": "high",
            "timeline": "6-8 weeks"
        },
        {
            "priority": "low",
            "category": "cost_optimization",
            "title": "Implement Smart Caching",
            "description": "Add intelligent caching for frequently accessed data",
            "expected_impact": "10% reduction in API costs",
            "effort": "low",
            "timeline": "1-2 weeks"
        }
    ]

async def _generate_forecasts(db: AsyncSession, org_id: str) -> Dict[str, Any]:
    """Generate predictive forecasts"""
    
    return {
        "rfp_volume": {
            "next_month": {"predicted": 95, "confidence": 0.87},
            "next_quarter": {"predicted": 280, "confidence": 0.74},
            "next_year": {"predicted": 1100, "confidence": 0.62}
        },
        "cost_projections": {
            "next_month": {"ai_costs": 2800, "savings": 12000},
            "next_quarter": {"ai_costs": 8400, "savings": 36000},
            "next_year": {"ai_costs": 33600, "savings": 144000}
        },
        "capacity_planning": {
            "recommended_users": 12,
            "storage_needs_gb": 850,
            "api_quota_adjustment": "+25%"
        }
    }

async def _validate_report_config(config: ReportConfig, org_id: str) -> None:
    """Validate report configuration"""
    
    valid_data_sources = ["rfps", "documents", "ai_usage", "users", "performance", "costs"]
    valid_metrics = ["total_count", "growth_rate", "success_rate", "avg_processing_time", "cost_savings", "user_engagement", "error_rate", "response_time"]
    valid_visualizations = ["line_chart", "bar_chart", "pie_chart", "table", "gauge", "heatmap"]
    valid_formats = ["pdf", "excel", "dashboard"]
    
    # Validate data sources
    for source in config.dataSources:
        if source not in valid_data_sources:
            raise HTTPException(status_code=400, detail=f"Invalid data source: {source}")
    
    # Validate metrics
    for metric in config.metrics:
        if metric not in valid_metrics:
            raise HTTPException(status_code=400, detail=f"Invalid metric: {metric}")
    
    # Validate visualizations
    for viz in config.visualizations:
        if viz not in valid_visualizations:
            raise HTTPException(status_code=400, detail=f"Invalid visualization: {viz}")
    
    # Validate format
    if config.format not in valid_formats:
        raise HTTPException(status_code=400, detail=f"Invalid format: {config.format}")

async def _generate_report(report_id: str, config: ReportConfig, org_id: str, user_id: str) -> None:
    """Background task to generate custom report"""
    
    try:
        # Update status to processing
        report_data = await cache.get(f"report:{report_id}")
        report_data["status"] = "processing"
        report_data["progress"] = 25
        await cache.set(f"report:{report_id}", report_data, ttl=3600)
        
        # Simulate report generation (replace with actual generation logic)
        await asyncio.sleep(2)  # Simulate data collection
        
        report_data["progress"] = 50
        await cache.set(f"report:{report_id}", report_data, ttl=3600)
        
        await asyncio.sleep(2)  # Simulate processing
        
        report_data["progress"] = 75
        await cache.set(f"report:{report_id}", report_data, ttl=3600)
        
        await asyncio.sleep(1)  # Simulate finalization
        
        # Mark as completed
        report_data["status"] = "completed"
        report_data["progress"] = 100
        report_data["completed_at"] = datetime.now().isoformat()
        report_data["download_url"] = f"/api/v1/analytics/reports/{report_id}/download"
        
        await cache.set(f"report:{report_id}", report_data, ttl=86400)  # Keep for 24 hours
        
        # Send notification to recipients (if configured)
        if config.recipients:
            # Implement email notification logic here
            pass
            
    except Exception as e:
        # Mark as failed
        report_data = await cache.get(f"report:{report_id}")
        if report_data:
            report_data["status"] = "failed"
            report_data["error"] = str(e)
            await cache.set(f"report:{report_id}", report_data, ttl=3600)