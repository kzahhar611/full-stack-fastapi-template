"""
Proposal Generation Models for TenderWise AI Platform
Handles AI-powered technical proposal generation workflow
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid

Base = declarative_base()

class ProjectStatus(enum.Enum):
    """Status enum for proposal projects"""
    CREATED = "created"
    ANALYZING_RFP = "analyzing_rfp"
    REQUIREMENTS_MAPPED = "requirements_mapped"
    GENERATING_CONTENT = "generating_content"
    REVIEW_PENDING = "review_pending"
    READY_FOR_EXPORT = "ready_for_export"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class RequirementType(enum.Enum):
    """Types of RFP requirements"""
    TECHNICAL = "technical"
    FUNCTIONAL = "functional"
    COMMERCIAL = "commercial"
    COMPLIANCE = "compliance"
    MANAGEMENT = "management"
    DELIVERY = "delivery"

class ContentType(enum.Enum):
    """Types of content blocks"""
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

class GenerationStatus(enum.Enum):
    """Status of content generation"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"

class ProposalProject(Base):
    """Main table for proposal generation projects"""
    __tablename__ = "proposal_projects"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Project details
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    client_name = Column(String(255))
    opportunity_value = Column(String(100))  # Store as string to handle various formats
    submission_deadline = Column(DateTime)
    
    # Status and tracking
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.CREATED, index=True)
    progress_percentage = Column(Integer, default=0)
    
    # RFP information
    rfp_filename = Column(String(255))
    rfp_file_path = Column(String(500))
    rfp_file_size = Column(Integer)
    rfp_upload_date = Column(DateTime)
    
    # AI analysis results
    ai_analysis_completed = Column(Boolean, default=False)
    requirements_extracted = Column(Boolean, default=False)
    content_generation_started = Column(Boolean, default=False)
    
    # Metadata
    total_requirements = Column(Integer, default=0)
    completed_sections = Column(Integer, default=0)
    total_sections = Column(Integer, default=0)
    estimated_completion_date = Column(DateTime)
    
    # Quality metrics
    content_quality_score = Column(Integer)  # 0-100
    completeness_score = Column(Integer)     # 0-100
    consistency_score = Column(Integer)      # 0-100
    
    # Timestamps and ownership
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    assigned_to_id = Column(Integer, ForeignKey("users.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    
    # Additional configuration
    generation_settings = Column(JSON)  # AI generation preferences
    export_settings = Column(JSON)      # Document export preferences
    collaboration_settings = Column(JSON)  # Team collaboration settings

class RFPRequirementAnalysis(Base):
    """Extracted and analyzed requirements from RFP documents"""
    __tablename__ = "rfp_requirements_analysis"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Reference to project
    project_id = Column(Integer, ForeignKey("proposal_projects.id"), nullable=False, index=True)
    
    # Requirement details
    requirement_text = Column(Text, nullable=False)
    requirement_type = Column(SQLEnum(RequirementType), nullable=False, index=True)
    section_title = Column(String(255))
    page_number = Column(Integer)
    paragraph_number = Column(String(50))
    
    # AI analysis
    priority_level = Column(String(20))  # High, Medium, Low
    complexity_score = Column(Integer)   # 1-10
    word_count_estimate = Column(Integer)  # Estimated words needed for response
    
    # Response planning
    assigned_content_type = Column(SQLEnum(ContentType), index=True)
    response_status = Column(String(50), default="not_started")
    estimated_effort_hours = Column(Integer)
    
    # AI confidence and metadata
    extraction_confidence = Column(Integer)  # 0-100
    keywords = Column(JSON)  # List of key terms
    related_requirements = Column(JSON)  # IDs of related requirements
    
    # Quality indicators
    clarity_score = Column(Integer)      # How clear the requirement is (1-10)
    measurability_score = Column(Integer)  # How measurable it is (1-10)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Processing metadata
    processing_notes = Column(Text)
    manual_review_required = Column(Boolean, default=False)

class ContentTemplate(Base):
    """Reusable content templates and blocks"""
    __tablename__ = "content_templates"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Template identification
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    content_type = Column(SQLEnum(ContentType), nullable=False, index=True)
    
    # Template content
    template_content = Column(Text, nullable=False)  # Main template text
    variables = Column(JSON)  # Template variables and placeholders
    styling_info = Column(JSON)  # Formatting and style information
    
    # Categorization and search
    industry_tags = Column(JSON)  # List of applicable industries
    service_tags = Column(JSON)   # List of applicable services
    complexity_level = Column(String(20))  # Basic, Intermediate, Advanced
    
    # Usage and quality metrics
    usage_count = Column(Integer, default=0)
    success_rate = Column(Integer)  # 0-100 based on proposal wins
    average_rating = Column(Integer)  # User ratings 1-5
    
    # Template metadata
    word_count = Column(Integer)
    estimated_completion_time = Column(Integer)  # Minutes
    last_used_date = Column(DateTime)
    
    # Access control
    is_public = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    
    # Version control
    version = Column(String(20), default="1.0")
    parent_template_id = Column(Integer, ForeignKey("content_templates.id"))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # AI enhancement
    ai_optimized = Column(Boolean, default=False)
    optimization_notes = Column(Text)

class GeneratedSection(Base):
    """AI-generated content sections for proposals"""
    __tablename__ = "generated_sections"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # References
    project_id = Column(Integer, ForeignKey("proposal_projects.id"), nullable=False, index=True)
    requirement_id = Column(Integer, ForeignKey("rfp_requirements_analysis.id"), index=True)
    template_id = Column(Integer, ForeignKey("content_templates.id"), index=True)
    
    # Section details
    section_title = Column(String(255), nullable=False)
    content_type = Column(SQLEnum(ContentType), nullable=False, index=True)
    section_order = Column(Integer, default=0)
    
    # Generated content
    generated_content = Column(Text, nullable=False)
    original_prompt = Column(Text)  # AI prompt used for generation
    ai_provider = Column(String(50))  # Which AI service was used
    
    # Content metadata
    word_count = Column(Integer)
    estimated_reading_time = Column(Integer)  # Minutes
    
    # Generation details
    generation_status = Column(SQLEnum(GenerationStatus), default=GenerationStatus.PENDING, index=True)
    generation_started_at = Column(DateTime)
    generation_completed_at = Column(DateTime)
    generation_duration = Column(Integer)  # Seconds
    
    # Quality assessment
    ai_confidence_score = Column(Integer)   # 0-100
    content_quality_score = Column(Integer) # 0-100
    relevance_score = Column(Integer)       # 0-100
    completeness_score = Column(Integer)    # 0-100
    
    # Human review
    human_reviewed = Column(Boolean, default=False)
    human_approved = Column(Boolean, default=False)
    human_review_notes = Column(Text)
    reviewed_by_id = Column(Integer, ForeignKey("users.id"))
    reviewed_at = Column(DateTime)
    
    # Editing and versions
    edit_count = Column(Integer, default=0)
    version_number = Column(Integer, default=1)
    is_current_version = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Enhancement suggestions
    improvement_suggestions = Column(JSON)
    related_sections = Column(JSON)  # References to related sections

class ProposalDocument(Base):
    """Assembled proposal documents"""
    __tablename__ = "proposal_documents"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Project reference
    project_id = Column(Integer, ForeignKey("proposal_projects.id"), nullable=False, index=True)
    
    # Document details
    document_name = Column(String(255), nullable=False)
    document_type = Column(String(50))  # proposal, cover_letter, presentation
    format_type = Column(String(20))    # pdf, docx, html
    
    # Assembly information
    section_count = Column(Integer, default=0)
    total_word_count = Column(Integer, default=0)
    total_page_count = Column(Integer, default=0)
    
    # Document content
    assembled_content = Column(Text)     # Full assembled document
    table_of_contents = Column(JSON)     # TOC structure
    section_mapping = Column(JSON)       # Map of sections to generated content
    
    # Export information
    file_path = Column(String(500))
    file_size = Column(Integer)
    export_settings = Column(JSON)       # Export configuration used
    
    # Quality metrics
    overall_quality_score = Column(Integer)    # 0-100
    consistency_score = Column(Integer)        # 0-100
    professional_score = Column(Integer)       # 0-100
    
    # Status and workflow
    assembly_status = Column(String(50), default="draft")  # draft, review, approved, submitted
    is_final_version = Column(Boolean, default=False)
    submission_ready = Column(Boolean, default=False)
    
    # Approval workflow
    approved_by_id = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime)
    approval_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    exported_at = Column(DateTime)
    
    # Collaboration
    collaborators = Column(JSON)  # List of user IDs with access
    change_log = Column(JSON)     # History of changes

class GenerationHistory(Base):
    """Audit trail and version control for proposal generation"""
    __tablename__ = "generation_history"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # References
    project_id = Column(Integer, ForeignKey("proposal_projects.id"), nullable=False, index=True)
    section_id = Column(Integer, ForeignKey("generated_sections.id"), index=True)
    document_id = Column(Integer, ForeignKey("proposal_documents.id"), index=True)
    
    # Action details
    action_type = Column(String(50), nullable=False)  # generated, edited, approved, exported
    action_description = Column(Text)
    
    # Before/after content (for edits)
    content_before = Column(Text)
    content_after = Column(Text)
    changes_summary = Column(Text)
    
    # User and timing
    performed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    performed_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Metadata
    ai_provider_used = Column(String(50))
    processing_time = Column(Integer)  # Seconds
    quality_metrics = Column(JSON)     # Quality scores at time of action
    
    # Context
    user_notes = Column(Text)
    system_notes = Column(Text)
    related_actions = Column(JSON)  # References to related history entries