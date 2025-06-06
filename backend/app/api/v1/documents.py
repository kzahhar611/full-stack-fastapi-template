"""
Document Generation API Endpoints
Handles HTML, PDF, and PowerPoint generation
"""
import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io

from ...core.database_simple import get_db
from ...models import User
from ...models.rfp_simple import RFP
from ...models.rfp_analysis import RFPAnalysis
from ...api.dependencies_simple import get_current_active_user
from ...services.document.document_generator import document_generator, DocumentFormat, DocumentType
from ...schemas.common import StatusResponse

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

from pydantic import BaseModel, Field
from datetime import datetime


class DocumentGenerationRequest(BaseModel):
    """Request model for document generation"""
    template_name: str = Field(..., description="Template name to use")
    format: str = Field(..., description="Output format: html, pdf, pptx")
    filename: Optional[str] = Field(None, description="Custom filename")
    data: Dict[str, Any] = Field(..., description="Data to populate template")


class AnalysisDocumentRequest(BaseModel):
    """Request model for analysis document generation"""
    analysis_id: str = Field(..., description="Analysis ID")
    format: str = Field(..., description="Output format: html, pdf, pptx")
    filename: Optional[str] = Field(None, description="Custom filename")
    include_sections: Optional[list[str]] = Field(None, description="Sections to include")
    template_name: Optional[str] = Field("rfp_analysis_report", description="Template to use")


class DocumentResponse(BaseModel):
    """Response model for document generation"""
    filename: str
    format: str
    content_type: str
    size: int
    generated_at: datetime
    download_url: str


class TemplateListResponse(BaseModel):
    """Response model for template listing"""
    templates: list[Dict[str, Any]]
    total: int


# =============================================================================
# DOCUMENT GENERATION ENDPOINTS
# =============================================================================

@router.post("/generate", response_model=DocumentResponse)
async def generate_document(
    request: DocumentGenerationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Generate document from template and data
    """
    try:
        # Validate format
        try:
            doc_format = DocumentFormat(request.format.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported format: {request.format}"
            )
        
        # Generate document
        generated_doc = await document_generator.generate_document(
            template_name=request.template_name,
            data=request.data,
            format=doc_format,
            filename=request.filename
        )
        
        logger.info(f"Generated document: {generated_doc.filename} for user {current_user.id}")
        
        return DocumentResponse(
            filename=generated_doc.filename,
            format=generated_doc.format.value,
            content_type=generated_doc.content_type,
            size=generated_doc.size,
            generated_at=generated_doc.generated_at,
            download_url=f"/api/v1/documents/download/{generated_doc.filename}"
        )
        
    except Exception as e:
        logger.error(f"Error generating document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate document: {str(e)}"
        )


@router.post("/generate/analysis/{analysis_id}")
async def generate_analysis_document(
    analysis_id: str,
    request: AnalysisDocumentRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> StreamingResponse:
    """
    Generate document for RFP analysis results
    """
    try:
        # Get analysis data
        analysis = db.query(RFPAnalysis).filter(
            RFPAnalysis.analysis_id == analysis_id,
            RFPAnalysis.organization_id == current_user.organization_id
        ).first()
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found or access denied"
            )
        
        # Get RFP data
        rfp = db.query(RFP).filter(RFP.id == analysis.rfp_id).first()
        if not rfp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Associated RFP not found"
            )
        
        # Validate format
        try:
            doc_format = DocumentFormat(request.format.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported format: {request.format}"
            )
        
        # Prepare template data
        template_data = _prepare_analysis_template_data(analysis, rfp, current_user)
        
        # Generate document
        generated_doc = await document_generator.generate_document(
            template_name=request.template_name,
            data=template_data,
            format=doc_format,
            filename=request.filename
        )
        
        # Return as streaming response
        file_stream = io.BytesIO(generated_doc.content)
        
        logger.info(f"Generated analysis document: {generated_doc.filename} for analysis {analysis_id}")
        
        return StreamingResponse(
            io.BytesIO(generated_doc.content),
            media_type=generated_doc.content_type,
            headers={
                "Content-Disposition": f"attachment; filename={generated_doc.filename}",
                "Content-Length": str(generated_doc.size)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating analysis document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate analysis document: {str(e)}"
        )


@router.get("/templates", response_model=TemplateListResponse)
async def list_templates(
    type: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    List available document templates
    """
    try:
        # Filter by type if provided
        doc_type = None
        if type:
            try:
                doc_type = DocumentType(type.lower())
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid template type: {type}"
                )
        
        templates = document_generator.list_templates(doc_type)
        
        template_data = []
        for template in templates:
            template_data.append({
                "name": template.name,
                "type": template.type.value,
                "format": template.format.value,
                "description": template.description,
                "variables": template.variables
            })
        
        return TemplateListResponse(
            templates=template_data,
            total=len(template_data)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list templates: {str(e)}"
        )


@router.post("/templates/create", response_model=StatusResponse)
async def create_template(
    name: str,
    type: str,
    format: str,
    content: str,
    description: str = "",
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Create a new document template
    """
    try:
        # Validate type and format
        try:
            doc_type = DocumentType(type.lower())
            doc_format = DocumentFormat(format.lower())
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid type or format: {str(e)}"
            )
        
        # Create template
        template = document_generator.create_template(
            name=name,
            type=doc_type,
            format=doc_format,
            content=content,
            description=description
        )
        
        logger.info(f"Created template: {name} by user {current_user.id}")
        
        return StatusResponse(
            success=True,
            message=f"Template '{name}' created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create template: {str(e)}"
        )


# =============================================================================
# QUICK GENERATION ENDPOINTS
# =============================================================================

@router.get("/generate/analysis/{analysis_id}/pdf")
async def download_analysis_pdf(
    analysis_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> StreamingResponse:
    """
    Quick download of analysis PDF
    """
    request = AnalysisDocumentRequest(
        analysis_id=analysis_id,
        format="pdf",
        template_name="rfp_analysis_report"
    )
    
    return await generate_analysis_document(analysis_id, request, current_user, db)


@router.get("/generate/analysis/{analysis_id}/html")
async def download_analysis_html(
    analysis_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> StreamingResponse:
    """
    Quick download of analysis HTML
    """
    request = AnalysisDocumentRequest(
        analysis_id=analysis_id,
        format="html",
        template_name="rfp_analysis_report"
    )
    
    return await generate_analysis_document(analysis_id, request, current_user, db)


@router.get("/generate/analysis/{analysis_id}/pptx")
async def download_analysis_pptx(
    analysis_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> StreamingResponse:
    """
    Quick download of analysis PowerPoint
    """
    request = AnalysisDocumentRequest(
        analysis_id=analysis_id,
        format="pptx",
        template_name="rfp_analysis_report"
    )
    
    return await generate_analysis_document(analysis_id, request, current_user, db)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _prepare_analysis_template_data(
    analysis: RFPAnalysis, 
    rfp: RFP, 
    user: User
) -> Dict[str, Any]:
    """Prepare template data for analysis document generation"""
    
    # Determine decision color
    decision_colors = {
        "go": "#10b981",
        "no_go": "#dc2626", 
        "conditional": "#f59e0b",
        "needs_review": "#3b82f6"
    }
    
    decision_type = analysis.decision.value if analysis.decision else "needs_review"
    decision_color = decision_colors.get(decision_type, "#64748b")
    
    return {
        # Basic Information
        "rfp_title": rfp.title,
        "analysis_id": analysis.analysis_id,
        "generated_at": analysis.created_at,
        "analysis_duration_seconds": analysis.analysis_duration_seconds or 0,
        "analyst_name": user.full_name,
        "company_name": user.organization.name if user.organization else "Your Organization",
        "contact_email": user.email,
        
        # Decision Information
        "decision": decision_type,
        "decision_color": decision_color,
        "confidence_score": float(analysis.confidence_score) if analysis.confidence_score else 0.0,
        "win_probability": float(analysis.estimated_win_probability) if analysis.estimated_win_probability else 0.0,
        "primary_justification": analysis.primary_justification or "No justification provided",
        "detailed_reasoning": analysis.detailed_reasoning or [],
        "success_factors": analysis.success_factors or [],
        "risk_factors": analysis.risk_factors or [],
        "conditions": analysis.conditions or [],
        
        # Risk Assessment
        "overall_risk_level": analysis.overall_risk_level.value if analysis.overall_risk_level else "medium",
        "risk_score": float(analysis.risk_score) if analysis.risk_score else 5.0,
        "technical_risks": analysis.technical_risks or [],
        "commercial_risks": analysis.commercial_risks or [],
        "operational_risks": analysis.operational_risks or [],
        "legal_risks": analysis.legal_risks or [],
        "mitigation_strategies": analysis.mitigation_strategies or [],
        
        # Project Insights
        "project_complexity": analysis.project_complexity or "medium",
        "estimated_duration_months": analysis.estimated_duration_months or 6,
        "estimated_cost_range": analysis.estimated_cost_range or {"min": 100000, "max": 500000},
        "technology_stack": analysis.technology_stack or [],
        "required_team_size": analysis.required_team_size or 5,
        "key_success_factors": analysis.key_success_factors or [],
        "competitive_advantages": analysis.competitive_advantages or [],
        "potential_challenges": analysis.potential_challenges or [],
        
        # KPI Data
        "strategic_score": float(analysis.strategic_score) if analysis.strategic_score else 0.7,
        "complexity_score": float(analysis.complexity_score) if analysis.complexity_score else 0.5,
        "kpi_dashboard": analysis.kpi_dashboard or {}
    }