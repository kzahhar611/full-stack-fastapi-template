from datetime import datetime, timedelta
from typing import Dict, List, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text

from app.core.database import get_db
from ...api.dependencies import get_current_user
from app.models.user import User
from app.models.rfp import RFP
from app.models.organization import Organization
# AuditLog model not implemented yet
from app.services.ai.ai_config import ai_service
from app.core.logging import logger

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_analytics(
    time_range: str = Query('30d', regex='^(24h|7d|30d|90d)$'),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive dashboard analytics data."""
    try:
        # Calculate time filter
        now = datetime.utcnow()
        if time_range == '24h':
            start_date = now - timedelta(hours=24)
        elif time_range == '7d':
            start_date = now - timedelta(days=7)
        elif time_range == '30d':
            start_date = now - timedelta(days=30)
        else:  # 90d
            start_date = now - timedelta(days=90)

        # AI Usage Analytics
        ai_usage = await get_ai_usage_analytics(db, start_date, now)
        
        # Document Analytics
        document_analytics = await get_document_analytics(db, start_date, now)
        
        # RFP Analytics
        rfp_analytics = await get_rfp_analytics(db, start_date, now, current_user)
        
        # Performance Metrics
        performance_metrics = await get_performance_metrics()

        return {
            "success": True,
            "data": {
                "ai_usage": ai_usage,
                "documents": document_analytics,
                "rfps": rfp_analytics,
                "performance": performance_metrics,
                "time_range": time_range,
                "generated_at": now.isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Dashboard analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate analytics")

@router.get("/real-time")
async def get_real_time_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get real-time system metrics."""
    try:
        # Mock active users (in real app, would use audit logs)
        active_users = 5
        
        # Mock requests per minute (in real app, would use audit logs)
        requests_per_minute = 12

        # AI processing queue (simulated - in real app would check actual queue)
        ai_processing_queue = 0
        
        # System health (check AI service status)
        try:
            ai_status = ai_service.get_status()
            system_health = "healthy" if ai_status.get("initialized") else "degraded"
        except:
            system_health = "degraded"

        return {
            "success": True,
            "data": {
                "active_users": active_users,
                "requests_per_minute": requests_per_minute,
                "ai_processing_queue": ai_processing_queue,
                "system_health": system_health
            }
        }
    except Exception as e:
        logger.error(f"Real-time metrics error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get real-time metrics")

@router.get("/ai-usage")
async def get_ai_usage_analytics_endpoint(
    time_range: str = Query('30d', regex='^(24h|7d|30d|90d)$'),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed AI usage analytics."""
    try:
        now = datetime.utcnow()
        if time_range == '24h':
            start_date = now - timedelta(hours=24)
        elif time_range == '7d':
            start_date = now - timedelta(days=7)
        elif time_range == '30d':
            start_date = now - timedelta(days=30)
        else:  # 90d
            start_date = now - timedelta(days=90)

        ai_usage = await get_ai_usage_analytics(db, start_date, now)
        
        return {
            "success": True,
            "data": ai_usage
        }
    except Exception as e:
        logger.error(f"AI usage analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get AI usage analytics")

@router.get("/documents")
async def get_document_analytics_endpoint(
    time_range: str = Query('30d', regex='^(24h|7d|30d|90d)$'),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed document analytics."""
    try:
        now = datetime.utcnow()
        if time_range == '24h':
            start_date = now - timedelta(hours=24)
        elif time_range == '7d':
            start_date = now - timedelta(days=7)
        elif time_range == '30d':
            start_date = now - timedelta(days=30)
        else:  # 90d
            start_date = now - timedelta(days=90)

        document_analytics = await get_document_analytics(db, start_date, now)
        
        return {
            "success": True,
            "data": document_analytics
        }
    except Exception as e:
        logger.error(f"Document analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get document analytics")

@router.get("/performance")
async def get_performance_metrics_endpoint(
    current_user: User = Depends(get_current_user)
):
    """Get system performance metrics."""
    try:
        performance_metrics = await get_performance_metrics()
        
        return {
            "success": True,
            "data": performance_metrics
        }
    except Exception as e:
        logger.error(f"Performance metrics error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get performance metrics")

# Helper functions
async def get_ai_usage_analytics(db: Session, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Generate AI usage analytics."""
    try:
        # Get current AI status and usage
        ai_status = ai_service.get_status()
        usage_stats = ai_status.get("usage_stats", {})
        
        # Mock daily usage data (in real app, this would come from usage tracking)
        daily_usage = []
        current_date = start_date.date()
        end_date_only = end_date.date()
        
        while current_date <= end_date_only:
            # Mock data - in real app, query from usage logs
            daily_usage.append({
                "date": current_date.isoformat(),
                "requests": max(0, 10 + int((current_date - start_date.date()).days) * 2),
                "tokens": max(0, 1000 + int((current_date - start_date.date()).days) * 200),
                "cost": max(0, 0.02 + int((current_date - start_date.date()).days) * 0.004)
            })
            current_date += timedelta(days=1)

        return {
            "total_requests": usage_stats.get("total_requests", 0),
            "total_tokens": usage_stats.get("total_tokens", 0),
            "total_cost": usage_stats.get("total_cost", 0.0),
            "requests_by_provider": {
                "OpenAI": usage_stats.get("total_requests", 0),
                "Anthropic": 0
            },
            "cost_by_provider": {
                "OpenAI": usage_stats.get("total_cost", 0.0),
                "Anthropic": 0.0
            },
            "daily_usage": daily_usage
        }
    except Exception as e:
        logger.error(f"AI usage analytics error: {str(e)}")
        return {
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "requests_by_provider": {},
            "cost_by_provider": {},
            "daily_usage": []
        }

async def get_document_analytics(db: Session, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Generate document analytics."""
    try:
        # Mock document analytics (in real app, query from document processing logs)
        return {
            "total_processed": 25,
            "avg_quality_score": 8.7,
            "processing_time_avg": 3.2,
            "classification_breakdown": {
                "RFP Document": 12,
                "Technical Specification": 8,
                "Contract": 3,
                "Proposal": 2
            },
            "quality_trends": [
                {"date": (start_date + timedelta(days=i)).date().isoformat(), 
                 "avg_score": 8.5 + (i * 0.1), "count": 2 + i}
                for i in range(0, (end_date - start_date).days + 1, 3)
            ]
        }
    except Exception as e:
        logger.error(f"Document analytics error: {str(e)}")
        return {
            "total_processed": 0,
            "avg_quality_score": 0.0,
            "processing_time_avg": 0.0,
            "classification_breakdown": {},
            "quality_trends": []
        }

async def get_rfp_analytics(db: Session, start_date: datetime, end_date: datetime, user: User) -> Dict[str, Any]:
    """Generate RFP analytics."""
    try:
        # Query actual RFP data
        total_rfps_query = db.query(func.count(RFP.id))
        if not user.is_super_user:
            total_rfps_query = total_rfps_query.filter(RFP.organization_id == user.organization_id)
        
        total_rfps = total_rfps_query.scalar() or 0
        
        # Status breakdown
        status_query = db.query(RFP.status, func.count(RFP.id)).group_by(RFP.status)
        if not user.is_super_user:
            status_query = status_query.filter(RFP.organization_id == user.organization_id)
        
        status_results = status_query.all()
        by_status = {status: count for status, count in status_results}
        
        # Average budget
        avg_budget_query = db.query(func.avg(RFP.estimated_budget)).filter(RFP.estimated_budget.isnot(None))
        if not user.is_super_user:
            avg_budget_query = avg_budget_query.filter(RFP.organization_id == user.organization_id)
        
        avg_budget = avg_budget_query.scalar() or 0.0
        
        # Timeline performance (mock data)
        timeline_performance = [
            {"month": f"2024-{i:02d}", "created": 5 + i, "completed": 3 + i, "success_rate": 0.8 + (i * 0.02)}
            for i in range(1, 13)
        ]
        
        return {
            "total": total_rfps,
            "by_status": by_status,
            "avg_budget": float(avg_budget),
            "success_rate": 0.85,  # Mock success rate
            "timeline_performance": timeline_performance
        }
    except Exception as e:
        logger.error(f"RFP analytics error: {str(e)}")
        return {
            "total": 0,
            "by_status": {},
            "avg_budget": 0.0,
            "success_rate": 0.0,
            "timeline_performance": []
        }

async def get_performance_metrics() -> Dict[str, Any]:
    """Generate system performance metrics."""
    try:
        # Mock performance metrics (in real app, these would come from monitoring systems)
        return {
            "avg_response_time": 1.8,  # seconds
            "uptime_percentage": 0.9995,  # 99.95%
            "error_rate": 0.002,  # 0.2%
            "cache_hit_rate": 0.85  # 85%
        }
    except Exception as e:
        logger.error(f"Performance metrics error: {str(e)}")
        return {
            "avg_response_time": 0.0,
            "uptime_percentage": 0.0,
            "error_rate": 0.0,
            "cache_hit_rate": 0.0
        }