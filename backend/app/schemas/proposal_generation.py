"""
Pydantic schemas for Proposal Generation API
Module 3: AI-Powered Technical Proposal Generation
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

# Enums for status fields
class ProjectStatus(str, Enum):
    CREATED = "created"
    ANALYZING_RFP = "analyzing_rfp"
    REQUIREMENTS_MAPPED = "requirements_mapped"
    GENERATING_CONTENT = "generating_content"
    REVIEW_PENDING = "review_pending"
    READY_FOR_EXPORT = "ready_for_export"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class RequirementType(str, Enum):
    TECHNICAL = "technical"
    FUNCTIONAL = "functional"
    COMMERCIAL = "commercial"
    COMPLIANCE = "compliance"
    MANAGEMENT = "management"
    DELIVERY = "delivery"

class ContentType(str, Enum):
    EXECUTIVE_SUMMARY = "executive_summary"
    TECHNICAL_APPROACH = "technical_approach"
    METHODOLOGY = "methodology"
    TEAM_QUALIFICATIONS = "team_qualifications"
    PROJECT_TIMELINE = "project_timeline"
    RISK_MANAGEMENT = "risk_management"
    QUALITY_ASSURANCE = "quality_assurance"
    DELIVERABLES = "deliverables"
    PRICING = "pricing"
    APPENDIX = "appendix"

class GenerationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"

# Base schemas
class ProposalProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    client_name: Optional[str] = Field(None, max_length=255, description="Client organization name")
    opportunity_value: Optional[str] = Field(None, max_length=100, description="Estimated contract value")
    submission_deadline: Optional[datetime] = Field(None, description="Proposal submission deadline")

class ProposalProjectCreate(ProposalProjectBase):
    generation_settings: Optional[Dict[str, Any]] = Field(default_factory=dict, description="AI generation preferences")
    export_settings: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Document export preferences")
    collaboration_settings: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Team collaboration settings")

class ProposalProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    client_name: Optional[str] = Field(None, max_length=255)
    opportunity_value: Optional[str] = Field(None, max_length=100)
    submission_deadline: Optional[datetime] = None
    status: Optional[ProjectStatus] = None
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    generation_settings: Optional[Dict[str, Any]] = None
    export_settings: Optional[Dict[str, Any]] = None
    collaboration_settings: Optional[Dict[str, Any]] = None

class ProposalProject(ProposalProjectBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    uuid: str
    status: ProjectStatus
    progress_percentage: int
    rfp_filename: Optional[str] = None
    rfp_file_path: Optional[str] = None
    rfp_file_size: Optional[int] = None
    rfp_upload_date: Optional[datetime] = None
    ai_analysis_completed: bool
    requirements_extracted: bool
    content_generation_started: bool
    total_requirements: int
    completed_sections: int
    total_sections: int
    estimated_completion_date: Optional[datetime] = None
    content_quality_score: Optional[int] = None
    completeness_score: Optional[int] = None
    consistency_score: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    created_by_id: Optional[int] = None
    assigned_to_id: Optional[int] = None
    organization_id: Optional[int] = None
    generation_settings: Optional[Dict[str, Any]] = None
    export_settings: Optional[Dict[str, Any]] = None
    collaboration_settings: Optional[Dict[str, Any]] = None

# RFP Requirements Analysis schemas
class RFPRequirementAnalysisBase(BaseModel):
    requirement_text: str = Field(..., description="The requirement text extracted from RFP")
    requirement_type: RequirementType = Field(..., description="Type of requirement")
    section_title: Optional[str] = Field(None, max_length=255, description="Section title from RFP")
    page_number: Optional[int] = Field(None, description="Page number in RFP")
    paragraph_number: Optional[str] = Field(None, max_length=50, description="Paragraph reference")

class RFPRequirementAnalysisCreate(RFPRequirementAnalysisBase):
    project_id: int = Field(..., description="Reference to proposal project")
    priority_level: Optional[str] = Field(None, description="Priority level (High/Medium/Low)")
    complexity_score: Optional[int] = Field(None, ge=1, le=10, description="Complexity rating 1-10")
    word_count_estimate: Optional[int] = Field(None, description="Estimated words needed for response")
    assigned_content_type: Optional[ContentType] = Field(None, description="Assigned content section type")
    estimated_effort_hours: Optional[int] = Field(None, description="Estimated effort in hours")
    extraction_confidence: Optional[int] = Field(None, ge=0, le=100, description="AI extraction confidence")
    keywords: Optional[List[str]] = Field(default_factory=list, description="Key terms")
    related_requirements: Optional[List[int]] = Field(default_factory=list, description="Related requirement IDs")

class RFPRequirementAnalysis(RFPRequirementAnalysisBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    uuid: str
    project_id: int
    priority_level: Optional[str] = None
    complexity_score: Optional[int] = None
    word_count_estimate: Optional[int] = None
    assigned_content_type: Optional[ContentType] = None
    response_status: str
    estimated_effort_hours: Optional[int] = None
    extraction_confidence: Optional[int] = None
    keywords: Optional[List[str]] = None
    related_requirements: Optional[List[int]] = None
    clarity_score: Optional[int] = None
    measurability_score: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    processing_notes: Optional[str] = None
    manual_review_required: bool

# Content Template schemas
class ContentTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    content_type: ContentType = Field(..., description="Type of content this template generates")
    template_content: str = Field(..., description="Template content with placeholders")

class ContentTemplateCreate(ContentTemplateBase):
    variables: Optional[List[str]] = Field(default_factory=list, description="Template variable names")
    styling_info: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Formatting information")
    industry_tags: Optional[List[str]] = Field(default_factory=list, description="Applicable industries")
    service_tags: Optional[List[str]] = Field(default_factory=list, description="Applicable services")
    complexity_level: Optional[str] = Field(None, description="Basic/Intermediate/Advanced")
    is_public: bool = Field(True, description="Whether template is publicly available")

class ContentTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    template_content: Optional[str] = None
    variables: Optional[List[str]] = None
    styling_info: Optional[Dict[str, Any]] = None
    industry_tags: Optional[List[str]] = None
    service_tags: Optional[List[str]] = None
    complexity_level: Optional[str] = None
    is_public: Optional[bool] = None
    is_approved: Optional[bool] = None

class ContentTemplate(ContentTemplateBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    uuid: str
    variables: Optional[List[str]] = None
    styling_info: Optional[Dict[str, Any]] = None
    industry_tags: Optional[List[str]] = None
    service_tags: Optional[List[str]] = None
    complexity_level: Optional[str] = None
    usage_count: int
    success_rate: Optional[int] = None
    average_rating: Optional[int] = None
    word_count: Optional[int] = None
    estimated_completion_time: Optional[int] = None
    last_used_date: Optional[datetime] = None
    is_public: bool
    is_approved: bool
    created_by_id: Optional[int] = None
    organization_id: Optional[int] = None
    version: str
    parent_template_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    ai_optimized: bool
    optimization_notes: Optional[str] = None

# Generated Section schemas
class GeneratedSectionBase(BaseModel):
    section_title: str = Field(..., min_length=1, max_length=255, description="Section title")
    content_type: ContentType = Field(..., description="Type of content section")
    section_order: int = Field(0, description="Order in document")

class GeneratedSectionCreate(GeneratedSectionBase):
    project_id: int = Field(..., description="Reference to proposal project")
    requirement_id: Optional[int] = Field(None, description="Reference to requirement")
    template_id: Optional[int] = Field(None, description="Reference to template used")
    generated_content: str = Field(..., description="Generated content text")
    original_prompt: Optional[str] = Field(None, description="AI prompt used")
    ai_provider: Optional[str] = Field(None, description="AI service used")

class GeneratedSectionUpdate(BaseModel):
    section_title: Optional[str] = Field(None, min_length=1, max_length=255)
    generated_content: Optional[str] = None
    section_order: Optional[int] = None
    generation_status: Optional[GenerationStatus] = None
    human_reviewed: Optional[bool] = None
    human_approved: Optional[bool] = None
    human_review_notes: Optional[str] = None

class GeneratedSection(GeneratedSectionBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    uuid: str
    project_id: int
    requirement_id: Optional[int] = None
    template_id: Optional[int] = None
    generated_content: str
    original_prompt: Optional[str] = None
    ai_provider: Optional[str] = None
    word_count: Optional[int] = None
    estimated_reading_time: Optional[int] = None
    generation_status: GenerationStatus
    generation_started_at: Optional[datetime] = None
    generation_completed_at: Optional[datetime] = None
    generation_duration: Optional[int] = None
    ai_confidence_score: Optional[int] = None
    content_quality_score: Optional[int] = None
    relevance_score: Optional[int] = None
    completeness_score: Optional[int] = None
    human_reviewed: bool
    human_approved: bool
    human_review_notes: Optional[str] = None
    reviewed_by_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    edit_count: int
    version_number: int
    is_current_version: bool
    created_at: datetime
    updated_at: datetime
    improvement_suggestions: Optional[List[str]] = None
    related_sections: Optional[List[int]] = None

# Proposal Document schemas
class ProposalDocumentBase(BaseModel):
    document_name: str = Field(..., min_length=1, max_length=255, description="Document name")
    document_type: Optional[str] = Field(None, description="Type of document")
    format_type: Optional[str] = Field(None, description="Export format")

class ProposalDocumentCreate(ProposalDocumentBase):
    project_id: int = Field(..., description="Reference to proposal project")
    export_settings: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Export configuration")

class ProposalDocumentUpdate(BaseModel):
    document_name: Optional[str] = Field(None, min_length=1, max_length=255)
    assembly_status: Optional[str] = None
    is_final_version: Optional[bool] = None
    submission_ready: Optional[bool] = None
    approval_notes: Optional[str] = None

class ProposalDocument(ProposalDocumentBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    uuid: str
    project_id: int
    section_count: int
    total_word_count: int
    total_page_count: int
    assembled_content: Optional[str] = None
    table_of_contents: Optional[Dict[str, Any]] = None
    section_mapping: Optional[Dict[str, Any]] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    export_settings: Optional[Dict[str, Any]] = None
    overall_quality_score: Optional[int] = None
    consistency_score: Optional[int] = None
    professional_score: Optional[int] = None
    assembly_status: str
    is_final_version: bool
    submission_ready: bool
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    approval_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    exported_at: Optional[datetime] = None
    collaborators: Optional[List[int]] = None
    change_log: Optional[List[Dict[str, Any]]] = None

# Request/Response schemas for specific operations
class RFPUploadRequest(BaseModel):
    project_id: int = Field(..., description="Project to upload RFP for")
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")

class RFPAnalysisRequest(BaseModel):
    project_id: int = Field(..., description="Project to analyze")
    analysis_settings: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Analysis configuration")

class ContentGenerationRequest(BaseModel):
    project_id: int = Field(..., description="Project to generate content for")
    requirement_ids: Optional[List[int]] = Field(default_factory=list, description="Specific requirements to address")
    template_ids: Optional[List[int]] = Field(default_factory=list, description="Templates to use")
    generation_settings: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Generation preferences")

class DocumentAssemblyRequest(BaseModel):
    project_id: int = Field(..., description="Project to assemble document for")
    section_ids: List[int] = Field(..., description="Sections to include")
    assembly_settings: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Assembly configuration")

class ExportRequest(BaseModel):
    document_id: int = Field(..., description="Document to export")
    format_type: str = Field(..., description="Export format (pdf, docx, html)")
    export_settings: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Export configuration")

# Statistics and summary schemas
class ProjectStatistics(BaseModel):
    total_projects: int
    active_projects: int
    completed_projects: int
    projects_by_status: Dict[str, int]
    total_requirements_processed: int
    total_content_generated: int
    average_completion_time: Optional[float] = None

class RequirementsSummary(BaseModel):
    project_id: int
    total_requirements: int
    requirements_by_type: Dict[str, int]
    completed_responses: int
    completion_percentage: float
    estimated_total_effort: int

class ContentGenerationSummary(BaseModel):
    project_id: int
    total_sections: int
    completed_sections: int
    sections_by_type: Dict[str, int]
    sections_by_status: Dict[str, int]
    average_quality_score: Optional[float] = None
    total_word_count: int

class QualityMetrics(BaseModel):
    content_quality_score: Optional[int] = None
    completeness_score: Optional[int] = None
    consistency_score: Optional[int] = None
    relevance_score: Optional[int] = None
    overall_score: Optional[int] = None

# Response schemas for list operations
class ProposalProjectList(BaseModel):
    projects: List[ProposalProject]
    total_count: int
    page: int
    page_size: int
    total_pages: int

class ContentTemplateList(BaseModel):
    templates: List[ContentTemplate]
    total_count: int
    page: int
    page_size: int
    total_pages: int

class GeneratedSectionList(BaseModel):
    sections: List[GeneratedSection]
    total_count: int
    page: int
    page_size: int
    total_pages: int