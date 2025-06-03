"""
AI Services API Endpoints
Provides REST API access to AI capabilities
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ...core.database_enhanced import get_db
from ...api.dependencies_simple import get_current_user
from ...models.user_simple import User
from ...models.rfp_enhanced import RFPEnhanced, RFPDocument
from ...services.ai.llm_service import llm_service
from ...services.ai.document_analyzer import document_analyzer
from ...services.ai.rfp_assistant import rfp_assistant
from ...services.ai.ai_config import ai_config

router = APIRouter()


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class AIStatusResponse(BaseModel):
    """AI service status response"""
    initialized: bool
    mock_mode: bool
    providers: List[str]
    primary_provider: Optional[str]
    total_providers: int
    usage_stats: Dict[str, Any]


class DocumentAnalysisRequest(BaseModel):
    """Document analysis request"""
    content: str = Field(..., description="Document content to analyze")
    filename: Optional[str] = Field(None, description="Original filename")
    document_type: Optional[str] = Field(None, description="Existing document type")


class DocumentAnalysisResponse(BaseModel):
    """Document analysis response"""
    document_type: str
    summary: str
    key_points: List[str]
    quality_score: float
    complexity: str
    completeness: str
    metadata: Dict[str, Any]
    suggestions: List[str]
    keywords: List[str]
    compliance_notes: List[str]
    analysis_timestamp: str


class RFPAnalysisRequest(BaseModel):
    """RFP analysis request"""
    content: str = Field(..., description="RFP content to analyze")
    rfp_type: str = Field("general", description="Type of RFP")
    industry: str = Field("general", description="Industry context")


class RFPAnalysisResponse(BaseModel):
    """RFP analysis response"""
    overall_score: float
    strengths: List[str]
    weaknesses: List[str]
    detailed_scores: Dict[str, float]
    suggestions: List[str]
    missing_sections: List[str]
    improvement_priority: str
    estimated_response_effort: str
    analysis_timestamp: str


class ContentGenerationRequest(BaseModel):
    """Content generation request"""
    requirements: Dict[str, Any] = Field(..., description="Requirements for content generation")
    rfp_type: str = Field("general", description="Type of RFP")
    industry: str = Field("general", description="Industry context")
    tone: str = Field("professional", description="Tone of content")


class ContentGenerationResponse(BaseModel):
    """Content generation response"""
    generated_content: str
    structured_sections: Dict[str, str]
    word_count: int
    generation_timestamp: str
    confidence: Optional[float]


class RequirementsExtractionRequest(BaseModel):
    """Requirements extraction request"""
    content: str = Field(..., description="RFP content to extract requirements from")


class RequirementsExtractionResponse(BaseModel):
    """Requirements extraction response"""
    functional_requirements: List[str]
    non_functional_requirements: List[str]
    technical_requirements: List[str]
    compliance_requirements: List[str]
    commercial_requirements: List[str]
    timeline_requirements: List[str]
    vendor_requirements: List[str]
    submission_requirements: List[str]
    total_requirements: int
    extraction_timestamp: str


class ChatRequest(BaseModel):
    """AI chat request"""
    message: str = Field(..., description="User message")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    rfp_id: Optional[int] = Field(None, description="RFP ID for context")


class ChatResponse(BaseModel):
    """AI chat response"""
    response: str
    confidence: Optional[float]
    suggestions: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProviderConfigRequest(BaseModel):
    """Provider configuration request"""
    provider: str = Field(..., description="Provider name (openai, anthropic, azure)")
    api_key: str = Field(..., description="API key")
    config: Dict[str, Any] = Field(default_factory=dict, description="Additional configuration")


# =============================================================================
# AI STATUS AND CONFIGURATION
# =============================================================================

@router.get("/status", response_model=AIStatusResponse)
async def get_ai_status(
    current_user: User = Depends(get_current_user)
):
    """Get AI service status"""
    status = ai_config.get_status()
    return AIStatusResponse(**status)


@router.post("/initialize")
async def initialize_ai_services(
    force_mock: bool = False,
    current_user: User = Depends(get_current_user),
):
    """Initialize AI services"""
    if current_user.role.value not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = ai_config.initialize_ai_services(force_mock=force_mock)
    return result


@router.post("/providers/{provider}/configure")
async def configure_provider(
    provider: str,
    config_request: ProviderConfigRequest,
    current_user: User = Depends(get_current_user),
):
    """Configure AI provider"""
    if current_user.role.value not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    success = ai_config.add_api_key(
        provider=provider,
        api_key=config_request.api_key,
        **config_request.config
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=f"Failed to configure {provider} provider")
    
    return {"message": f"{provider} provider configured successfully"}


@router.delete("/providers/{provider}")
async def remove_provider(
    provider: str,
    current_user: User = Depends(get_current_user),
):
    """Remove AI provider"""
    if current_user.role.value not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    success = ai_config.remove_provider(provider)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Provider {provider} not found")
    
    return {"message": f"{provider} provider removed successfully"}


@router.post("/providers/test")
async def test_providers(
    provider: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """Test AI providers"""
    if current_user.role.value not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = ai_config.test_provider(provider)
    return result


# =============================================================================
# DOCUMENT ANALYSIS
# =============================================================================

@router.post("/documents/analyze", response_model=DocumentAnalysisResponse)
async def analyze_document_content(
    request: DocumentAnalysisRequest,
    current_user: User = Depends(get_current_user),
):
    """Analyze document content using AI"""
    
    try:
        analysis = await document_analyzer.analyze_document(
            content=request.content,
            filename=request.filename,
            existing_type=request.document_type
        )
        
        return DocumentAnalysisResponse(**analysis)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document analysis failed: {str(e)}")


@router.post("/documents/{document_id}/analyze")
async def analyze_existing_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze existing document by ID"""
    
    # Get document
    document = db.query(RFPDocument).filter(
        RFPDocument.id == document_id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check access permissions
    rfp = db.query(RFPEnhanced).filter(
        RFPEnhanced.id == document.rfp_id,
        RFPEnhanced.organization_id == current_user.organization_id
    ).first()
    
    if not rfp:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Read document content (simplified - in production, you'd extract text from file)
        content = f"Document: {document.original_filename}\nType: {document.document_type}\nSize: {document.file_size} bytes"
        
        analysis = await document_analyzer.analyze_document(
            content=content,
            filename=document.original_filename,
            existing_type=document.document_type.value
        )
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document analysis failed: {str(e)}")


# =============================================================================
# RFP ANALYSIS AND ASSISTANCE
# =============================================================================

@router.post("/rfp/analyze", response_model=RFPAnalysisResponse)
async def analyze_rfp_quality(
    request: RFPAnalysisRequest,
    current_user: User = Depends(get_current_user),
):
    """Analyze RFP quality and provide recommendations"""
    
    try:
        analysis = await rfp_assistant.analyze_rfp_quality(
            rfp_content=request.content,
            rfp_type=request.rfp_type,
            industry=request.industry
        )
        
        return RFPAnalysisResponse(**analysis)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RFP analysis failed: {str(e)}")


@router.post("/rfp/{rfp_id}/analyze")
async def analyze_existing_rfp(
    rfp_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze existing RFP by ID"""
    
    # Get RFP
    rfp = db.query(RFPEnhanced).filter(
        RFPEnhanced.id == rfp_id,
        RFPEnhanced.organization_id == current_user.organization_id
    ).first()
    
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    
    try:
        # Combine RFP content
        content_parts = []
        if rfp.title:
            content_parts.append(f"Title: {rfp.title}")
        if rfp.description:
            content_parts.append(f"Description: {rfp.description}")
        if rfp.description_html:
            content_parts.append(f"Detailed Description: {rfp.description_html}")
        if rfp.requirements:
            content_parts.append(f"Requirements: {rfp.requirements}")
        if rfp.requirements_html:
            content_parts.append(f"Detailed Requirements: {rfp.requirements_html}")
        if rfp.evaluation_criteria:
            content_parts.append(f"Evaluation Criteria: {rfp.evaluation_criteria}")
        
        rfp_content = "\n\n".join(content_parts)
        
        analysis = await rfp_assistant.analyze_rfp_quality(
            rfp_content=rfp_content,
            rfp_type=rfp.category or "general",
            industry="general"
        )
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RFP analysis failed: {str(e)}")


@router.post("/rfp/generate", response_model=ContentGenerationResponse)
async def generate_rfp_content(
    request: ContentGenerationRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate RFP content based on requirements"""
    
    try:
        result = await rfp_assistant.generate_rfp_content(
            requirements=request.requirements,
            rfp_type=request.rfp_type,
            industry=request.industry,
            tone=request.tone
        )
        
        return ContentGenerationResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")


@router.post("/rfp/extract-requirements", response_model=RequirementsExtractionResponse)
async def extract_rfp_requirements(
    request: RequirementsExtractionRequest,
    current_user: User = Depends(get_current_user),
):
    """Extract requirements from RFP content"""
    
    try:
        requirements = await rfp_assistant.extract_requirements(
            rfp_content=request.content
        )
        
        return RequirementsExtractionResponse(**requirements)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Requirements extraction failed: {str(e)}")


@router.post("/rfp/{rfp_id}/suggest-improvements")
async def suggest_rfp_improvements(
    rfp_id: int,
    focus_areas: List[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get improvement suggestions for existing RFP"""
    
    # Get RFP
    rfp = db.query(RFPEnhanced).filter(
        RFPEnhanced.id == rfp_id,
        RFPEnhanced.organization_id == current_user.organization_id
    ).first()
    
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    
    try:
        # Combine RFP content
        content_parts = []
        if rfp.title:
            content_parts.append(f"Title: {rfp.title}")
        if rfp.description:
            content_parts.append(f"Description: {rfp.description}")
        if rfp.description_html:
            content_parts.append(f"Detailed Description: {rfp.description_html}")
        if rfp.requirements:
            content_parts.append(f"Requirements: {rfp.requirements}")
        if rfp.requirements_html:
            content_parts.append(f"Detailed Requirements: {rfp.requirements_html}")
        if rfp.evaluation_criteria:
            content_parts.append(f"Evaluation Criteria: {rfp.evaluation_criteria}")
        
        rfp_content = "\n\n".join(content_parts)
        
        suggestions = await rfp_assistant.suggest_improvements(
            rfp_content=rfp_content,
            focus_areas=focus_areas
        )
        
        return suggestions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Improvement suggestions failed: {str(e)}")


# =============================================================================
# AI CHAT INTERFACE
# =============================================================================

@router.post("/chat", response_model=ChatResponse)
async def ai_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Chat with AI assistant"""
    
    try:
        # Build context
        context_parts = [request.message]
        
        # Add RFP context if provided
        if request.rfp_id:
            rfp = db.query(RFPEnhanced).filter(
                RFPEnhanced.id == request.rfp_id,
                RFPEnhanced.organization_id == current_user.organization_id
            ).first()
            
            if rfp:
                rfp_context = f"RFP Context - Title: {rfp.title}, Description: {rfp.description}"
                context_parts.append(rfp_context)
        
        # Add additional context
        if request.context:
            context_parts.append(f"Additional Context: {request.context}")
        
        full_message = "\n\n".join(context_parts)
        
        # Generate response
        response = await llm_service.generate(
            messages=full_message,
            temperature=0.7,
            max_tokens=800
        )
        
        # Generate suggestions based on the conversation
        suggestions = []
        message_lower = request.message.lower()
        
        if "analyze" in message_lower:
            suggestions.extend(["Analyze document quality", "Extract key requirements", "Suggest improvements"])
        elif "generate" in message_lower or "create" in message_lower:
            suggestions.extend(["Generate RFP content", "Create evaluation criteria", "Draft requirements"])
        elif "improve" in message_lower:
            suggestions.extend(["Suggest specific improvements", "Review for completeness", "Check compliance"])
        
        return ChatResponse(
            response=response.content,
            confidence=response.confidence,
            suggestions=suggestions[:3],  # Limit to 3 suggestions
            metadata={
                "provider": str(response.provider),
                "model": response.model,
                "usage": response.usage.model_dump(),
                "context_included": bool(request.rfp_id or request.context)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


# =============================================================================
# USAGE STATISTICS
# =============================================================================

@router.get("/usage/stats")
async def get_usage_statistics(
    current_user: User = Depends(get_current_user),
):
    """Get AI usage statistics"""
    
    if current_user.role.value not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    stats = llm_service.get_usage_stats()
    
    return {
        "usage_stats": stats,
        "providers": llm_service.get_available_providers(),
        "primary_provider": str(llm_service.primary_provider) if llm_service.primary_provider else None
    }


@router.get("/usage/provider/{provider}")
async def get_provider_usage(
    provider: str,
    current_user: User = Depends(get_current_user),
):
    """Get usage statistics for specific provider"""
    
    if current_user.role.value not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from ...services.ai.llm_service import LLMProvider
        provider_enum = LLMProvider(provider.lower())
        stats = llm_service.get_usage_stats(provider_enum)
        
        return {
            "provider": provider,
            "stats": stats
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}")


# =============================================================================
# BULK OPERATIONS
# =============================================================================

@router.post("/documents/bulk-analyze")
async def bulk_analyze_documents(
    document_ids: List[int],
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bulk analyze multiple documents"""
    
    if len(document_ids) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 documents per bulk operation")
    
    # Verify access to all documents
    documents = db.query(RFPDocument).join(RFPEnhanced).filter(
        RFPDocument.id.in_(document_ids),
        RFPEnhanced.organization_id == current_user.organization_id
    ).all()
    
    if len(documents) != len(document_ids):
        raise HTTPException(status_code=403, detail="Access denied to some documents")
    
    # Start background analysis
    async def analyze_documents():
        results = []
        for document in documents:
            try:
                content = f"Document: {document.original_filename}\nType: {document.document_type}"
                analysis = await document_analyzer.analyze_document(
                    content=content,
                    filename=document.original_filename,
                    existing_type=document.document_type.value
                )
                results.append({
                    "document_id": document.id,
                    "status": "success",
                    "analysis": analysis
                })
            except Exception as e:
                results.append({
                    "document_id": document.id,
                    "status": "error",
                    "error": str(e)
                })
        
        # Store results (in production, you'd save to database)
        logger.info(f"Bulk analysis completed for {len(results)} documents")
    
    background_tasks.add_task(analyze_documents)
    
    return {
        "message": f"Bulk analysis started for {len(documents)} documents",
        "document_count": len(documents),
        "status": "processing"
    }