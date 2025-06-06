"""
RFP Analysis API Endpoints - Module 1: Strategic Decision Support
"""
import logging
import asyncio
from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks, Form
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime
import uuid

from ...core.database_simple import get_db
from ...models import Organization, User
from ...models.rfp_simple import RFP, RFPStatus
from ...models.rfp_analysis import RFPAnalysis, AnalysisStatus, DecisionType, AnalysisTemplate
from ...api.dependencies_simple import get_current_active_user
from ...services.ai.rfp_analyzer import rfp_analyzer, AnalysisResult
from ...services.document.document_extractor import document_extractor
from ...schemas.common import StatusResponse

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# REQUEST/RESPONSE SCHEMAS
# =============================================================================

from pydantic import BaseModel, Field
from datetime import datetime


class RFPAnalysisRequest(BaseModel):
    """Request model for RFP analysis"""
    rfp_id: int = Field(..., description="RFP ID to analyze")
    company_context: Optional[Dict[str, Any]] = Field(None, description="Company context for analysis")
    analysis_template_id: Optional[int] = Field(None, description="Analysis template to use")
    force_reanalysis: bool = Field(False, description="Force re-analysis even if exists")


class RFPUploadAnalysisRequest(BaseModel):
    """Request model for upload and analyze"""
    title: str = Field(..., description="RFP title")
    description: Optional[str] = Field(None, description="RFP description")
    company_context: Optional[Dict[str, Any]] = Field(None, description="Company context")
    analysis_template_id: Optional[int] = Field(None, description="Analysis template ID")


class AnalysisResponse(BaseModel):
    """Response model for analysis results"""
    id: int
    uuid: str
    analysis_id: str
    rfp_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    # Decision
    decision: Optional[Dict[str, Any]]
    
    # Risk Assessment
    risk_assessment: Optional[Dict[str, Any]]
    
    # Project Insights
    project_insights: Optional[Dict[str, Any]]
    
    # KPIs
    kpi_dashboard: Optional[Dict[str, Any]]
    strategic_score: Optional[float]
    complexity_score: Optional[float]
    
    # Metadata
    analysis_duration_seconds: Optional[int]
    error_message: Optional[str]
    
    class Config:
        from_attributes = True


class AnalysisListResponse(BaseModel):
    """Response model for analysis list"""
    analyses: List[AnalysisResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


class DecisionUpdateRequest(BaseModel):
    """Request model for updating analysis decision"""
    decision: str = Field(..., description="New decision: go, no_go, conditional, needs_review")
    reason_for_change: str = Field(..., description="Reason for decision change")
    reviewer_notes: Optional[str] = Field(None, description="Additional reviewer notes")


class AnalysisStatsResponse(BaseModel):
    """Response model for analysis statistics"""
    total_analyses: int
    go_decisions: int
    no_go_decisions: int
    conditional_decisions: int
    needs_review_decisions: int
    average_win_probability: float
    average_risk_score: float
    top_risk_factors: List[str]
    recent_analyses: List[AnalysisResponse]


# =============================================================================
# ANALYSIS ENDPOINTS
# =============================================================================

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_rfp(
    request: RFPAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Analyze an existing RFP for Go/No-Go decision
    """
    # Verify RFP exists and user has access
    rfp = db.query(RFP).filter(
        and_(
            RFP.id == request.rfp_id,
            RFP.organization_id == current_user.organization_id
        )
    ).first()
    
    if not rfp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFP not found or access denied"
        )
    
    # Check if analysis already exists and not forcing re-analysis
    existing_analysis = db.query(RFPAnalysis).filter(
        and_(
            RFPAnalysis.rfp_id == request.rfp_id,
            RFPAnalysis.status == AnalysisStatus.COMPLETED
        )
    ).first()
    
    if existing_analysis and not request.force_reanalysis:
        return AnalysisResponse.model_validate(existing_analysis.to_dict())
    
    # Create new analysis record
    analysis = RFPAnalysis(
        analysis_id=f"analysis_{request.rfp_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        rfp_id=request.rfp_id,
        organization_id=current_user.organization_id,
        created_by_id=current_user.id,
        status=AnalysisStatus.PENDING,
        company_context=request.company_context or {},
        analysis_parameters={"template_id": request.analysis_template_id}
    )
    
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    
    # Start background analysis
    background_tasks.add_task(
        _perform_analysis_background,
        analysis.id,
        rfp.content or rfp.description or "",
        request.company_context
    )
    
    logger.info(f"Started RFP analysis for RFP {request.rfp_id}, Analysis ID: {analysis.analysis_id}")
    
    return AnalysisResponse.model_validate(analysis.to_dict())


@router.post("/upload-and-analyze", response_model=AnalysisResponse)
async def upload_and_analyze(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    company_context: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Upload RFP document and perform analysis
    """
    try:
        # Read and extract document content
        file_content = await file.read()
        
        # Extract text from document
        extracted_text = await document_extractor.extract_text(
            file_content, 
            file.filename or "document.pdf"
        )
        
        if not extracted_text or len(extracted_text.strip()) < 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract sufficient text from document"
            )
        
        # Create RFP record
        rfp = RFP(
            title=title,
            rfp_number=f"RFP-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            description=description,
            content=extracted_text,
            organization_id=current_user.organization_id,
            created_by_id=current_user.id,
            submission_deadline=None,  # Will be extracted from content if available
            status=RFPStatus.DRAFT
        )
        
        db.add(rfp)
        db.commit()
        db.refresh(rfp)
        
        # Parse company context
        parsed_context = {}
        if company_context:
            try:
                import json
                parsed_context = json.loads(company_context)
            except:
                parsed_context = {"notes": company_context}
        
        # Create analysis record
        analysis = RFPAnalysis(
            analysis_id=f"analysis_{rfp.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            rfp_id=rfp.id,
            organization_id=current_user.organization_id,
            created_by_id=current_user.id,
            status=AnalysisStatus.PENDING,
            company_context=parsed_context,
            analysis_parameters={}
        )
        
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        # Start background analysis
        background_tasks.add_task(
            _perform_analysis_background,
            analysis.id,
            extracted_text,
            parsed_context
        )
        
        logger.info(f"Created RFP {rfp.id} and started analysis {analysis.analysis_id}")
        
        return AnalysisResponse.model_validate(analysis.to_dict())
        
    except Exception as e:
        logger.error(f"Error in upload and analyze: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}"
        )


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get analysis results by analysis ID
    """
    analysis = db.query(RFPAnalysis).filter(
        and_(
            RFPAnalysis.analysis_id == analysis_id,
            RFPAnalysis.organization_id == current_user.organization_id
        )
    ).first()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found or access denied"
        )
    
    return AnalysisResponse.model_validate(analysis.to_dict())


@router.get("/{analysis_id}/dashboard", response_model=Dict[str, Any])
async def get_analysis_dashboard(
    analysis_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get KPI dashboard data for analysis
    """
    analysis = db.query(RFPAnalysis).filter(
        and_(
            RFPAnalysis.analysis_id == analysis_id,
            RFPAnalysis.organization_id == current_user.organization_id
        )
    ).first()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found or access denied"
        )
    
    if analysis.status != AnalysisStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Analysis not yet completed"
        )
    
    return analysis.kpi_dashboard or {}


@router.post("/{analysis_id}/decision", response_model=StatusResponse)
async def update_decision(
    analysis_id: str,
    request: DecisionUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update analysis decision (manual override)
    """
    analysis = db.query(RFPAnalysis).filter(
        and_(
            RFPAnalysis.analysis_id == analysis_id,
            RFPAnalysis.organization_id == current_user.organization_id
        )
    ).first()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found or access denied"
        )
    
    # Validate decision type
    try:
        new_decision = DecisionType(request.decision)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid decision type"
        )
    
    # Store previous decision
    previous_decision = analysis.decision
    
    # Update decision
    analysis.decision = new_decision
    analysis.updated_at = datetime.utcnow()
    
    # Create decision history record
    from ...models.rfp_analysis import DecisionHistory
    history = DecisionHistory(
        analysis_id=analysis.id,
        previous_decision=previous_decision,
        new_decision=new_decision,
        reason_for_change=request.reason_for_change,
        reviewer_notes=request.reviewer_notes,
        reviewer_id=current_user.id
    )
    
    db.add(history)
    db.commit()
    
    logger.info(f"Decision updated for analysis {analysis_id} by user {current_user.id}")
    
    return StatusResponse(success=True, message="Decision updated successfully")


@router.get("/rfp/{rfp_id}/analyses", response_model=AnalysisListResponse)
async def get_rfp_analyses(
    rfp_id: int,
    page: int = 1,
    per_page: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get all analyses for a specific RFP
    """
    # Verify RFP access
    rfp = db.query(RFP).filter(
        and_(
            RFP.id == rfp_id,
            RFP.organization_id == current_user.organization_id
        )
    ).first()
    
    if not rfp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFP not found or access denied"
        )
    
    # Get analyses with pagination
    offset = (page - 1) * per_page
    
    query = db.query(RFPAnalysis).filter(
        RFPAnalysis.rfp_id == rfp_id
    ).order_by(desc(RFPAnalysis.created_at))
    
    total = query.count()
    analyses = query.offset(offset).limit(per_page).all()
    
    return AnalysisListResponse(
        analyses=[AnalysisResponse.model_validate(a.to_dict()) for a in analyses],
        total=total,
        page=page,
        per_page=per_page,
        has_next=offset + per_page < total,
        has_prev=page > 1
    )


@router.get("/stats", response_model=AnalysisStatsResponse)
async def get_analysis_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get analysis statistics for organization
    """
    # Get all completed analyses for organization
    analyses = db.query(RFPAnalysis).filter(
        and_(
            RFPAnalysis.organization_id == current_user.organization_id,
            RFPAnalysis.status == AnalysisStatus.COMPLETED
        )
    ).all()
    
    if not analyses:
        return AnalysisStatsResponse(
            total_analyses=0,
            go_decisions=0,
            no_go_decisions=0,
            conditional_decisions=0,
            needs_review_decisions=0,
            average_win_probability=0.0,
            average_risk_score=0.0,
            top_risk_factors=[],
            recent_analyses=[]
        )
    
    # Calculate statistics
    total_analyses = len(analyses)
    decision_counts = {
        DecisionType.GO: 0,
        DecisionType.NO_GO: 0,
        DecisionType.CONDITIONAL: 0,
        DecisionType.NEEDS_REVIEW: 0
    }
    
    win_probabilities = []
    risk_scores = []
    all_risk_factors = []
    
    for analysis in analyses:
        if analysis.decision:
            decision_counts[analysis.decision] += 1
        
        if analysis.estimated_win_probability:
            win_probabilities.append(float(analysis.estimated_win_probability))
        
        if analysis.risk_score:
            risk_scores.append(float(analysis.risk_score))
        
        # Collect risk factors
        for risk_list in [analysis.technical_risks, analysis.commercial_risks, 
                         analysis.operational_risks, analysis.legal_risks]:
            for risk in risk_list:
                if isinstance(risk, dict) and 'description' in risk:
                    all_risk_factors.append(risk['description'])
    
    # Calculate averages
    avg_win_prob = sum(win_probabilities) / len(win_probabilities) if win_probabilities else 0.0
    avg_risk_score = sum(risk_scores) / len(risk_scores) if risk_scores else 0.0
    
    # Find top risk factors (most common)
    from collections import Counter
    risk_counter = Counter(all_risk_factors)
    top_risk_factors = [risk for risk, count in risk_counter.most_common(5)]
    
    # Get recent analyses
    recent = db.query(RFPAnalysis).filter(
        and_(
            RFPAnalysis.organization_id == current_user.organization_id,
            RFPAnalysis.status == AnalysisStatus.COMPLETED
        )
    ).order_by(desc(RFPAnalysis.created_at)).limit(5).all()
    
    return AnalysisStatsResponse(
        total_analyses=total_analyses,
        go_decisions=decision_counts[DecisionType.GO],
        no_go_decisions=decision_counts[DecisionType.NO_GO],
        conditional_decisions=decision_counts[DecisionType.CONDITIONAL],
        needs_review_decisions=decision_counts[DecisionType.NEEDS_REVIEW],
        average_win_probability=avg_win_prob,
        average_risk_score=avg_risk_score,
        top_risk_factors=top_risk_factors,
        recent_analyses=[AnalysisResponse.model_validate(a.to_dict()) for a in recent]
    )


# =============================================================================
# BACKGROUND TASKS
# =============================================================================

async def _perform_analysis_background(
    analysis_id: int,
    rfp_content: str,
    company_context: Optional[Dict[str, Any]] = None
):
    """
    Perform RFP analysis in background
    """
    from ...core.database_simple import SessionLocal
    
    db = SessionLocal()
    try:
        # Get analysis record
        analysis = db.query(RFPAnalysis).filter(RFPAnalysis.id == analysis_id).first()
        if not analysis:
            logger.error(f"Analysis {analysis_id} not found")
            return
        
        # Update status to in progress
        analysis.status = AnalysisStatus.IN_PROGRESS
        analysis.updated_at = datetime.utcnow()
        db.commit()
        
        start_time = datetime.utcnow()
        
        try:
            # Perform comprehensive analysis
            result: AnalysisResult = await rfp_analyzer.analyze_rfp_comprehensive(
                rfp_content=rfp_content,
                rfp_id=str(analysis.rfp_id),
                company_context=company_context
            )
            
            # Update analysis record with results
            analysis.status = AnalysisStatus.COMPLETED
            analysis.decision = DecisionType(result.go_no_go_decision.decision.value)
            analysis.confidence_score = result.go_no_go_decision.confidence_score
            analysis.primary_justification = result.go_no_go_decision.primary_justification
            analysis.detailed_reasoning = result.go_no_go_decision.detailed_reasoning
            analysis.risk_factors = result.go_no_go_decision.risk_factors
            analysis.success_factors = result.go_no_go_decision.success_factors
            analysis.conditions = result.go_no_go_decision.conditions
            analysis.estimated_win_probability = result.go_no_go_decision.estimated_win_probability
            
            # Risk assessment
            analysis.overall_risk_level = result.risk_assessment.overall_risk_level
            analysis.risk_score = result.risk_assessment.risk_score
            analysis.technical_risks = result.risk_assessment.technical_risks
            analysis.commercial_risks = result.risk_assessment.commercial_risks
            analysis.operational_risks = result.risk_assessment.operational_risks
            analysis.legal_risks = result.risk_assessment.legal_risks
            analysis.mitigation_strategies = result.risk_assessment.mitigation_strategies
            
            # Project insights
            analysis.project_complexity = result.project_insights.project_complexity
            analysis.estimated_duration_months = result.project_insights.estimated_duration_months
            analysis.estimated_cost_range = result.project_insights.estimated_cost_range or {}
            analysis.technology_stack = result.project_insights.technology_stack
            analysis.required_team_size = result.project_insights.required_team_size
            analysis.key_success_factors = result.project_insights.key_success_factors
            analysis.competitive_advantages = result.project_insights.competitive_advantages
            analysis.potential_challenges = result.project_insights.potential_challenges
            
            # KPI dashboard and scores
            analysis.kpi_dashboard = result.kpi_dashboard
            analysis.strategic_score = result.kpi_dashboard.get("strategic_score")
            analysis.complexity_score = result.kpi_dashboard.get("complexity_score")
            
            # Raw analysis data
            analysis.raw_analysis = result.raw_analysis
            analysis.strategic_analysis = result.raw_analysis.get("strategic_analysis", {})
            
            # Calculate duration
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            analysis.analysis_duration_seconds = int(duration)
            
            analysis.updated_at = end_time
            
            logger.info(f"Completed analysis {analysis.analysis_id} in {duration:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Error during analysis {analysis.analysis_id}: {str(e)}")
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = str(e)
            analysis.retry_count += 1
            analysis.updated_at = datetime.utcnow()
        
        db.commit()
        
    except Exception as e:
        logger.error(f"Critical error in background analysis {analysis_id}: {str(e)}")
    finally:
        db.close()