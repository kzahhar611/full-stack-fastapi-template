"""
Proposal Generation API Endpoints
Module 3: AI-Powered Technical Proposal Generation
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
import os
import uuid
from datetime import datetime

from ...core.database_simple import get_db
from ...core.auth_simple import get_current_user
from ...schemas.proposal_generation import (
    ProposalProject, ProposalProjectCreate, ProposalProjectUpdate, ProposalProjectList,
    RFPRequirementAnalysis, RFPRequirementAnalysisCreate,
    ContentTemplate, ContentTemplateCreate, ContentTemplateUpdate, ContentTemplateList,
    GeneratedSection, GeneratedSectionCreate, GeneratedSectionUpdate, GeneratedSectionList,
    ProposalDocument, ProposalDocumentCreate, ProposalDocumentUpdate,
    RFPUploadRequest, RFPAnalysisRequest, ContentGenerationRequest,
    DocumentAssemblyRequest, ExportRequest,
    ProjectStatistics, RequirementsSummary, ContentGenerationSummary
)
from ...services.ai.proposal_generator import ProposalGeneratorService
from ...services.ai.llm_service import LLMService
from ...services.document.document_extractor import DocumentExtractionService
from ...models.user import User

# Temporarily use text-based SQL queries until models are integrated
# This will be replaced with proper SQLAlchemy models in the next iteration

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
llm_service = LLMService()
proposal_generator = ProposalGeneratorService(llm_service)
document_service = DocumentExtractionService()

# --- Project Management Endpoints ---

@router.get("/projects", response_model=ProposalProjectList)
async def list_projects(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List proposal generation projects"""
    try:
        # Build query
        query = db.query(DBProposalProject).filter(
            DBProposalProject.organization_id == current_user.organization_id
        )
        
        if status:
            query = query.filter(DBProposalProject.status == status)
        
        # Get total count
        total_count = query.count()
        
        # Get paginated results
        projects = query.offset(skip).limit(limit).all()
        
        return ProposalProjectList(
            projects=projects,
            total_count=total_count,
            page=skip // limit + 1,
            page_size=limit,
            total_pages=(total_count + limit - 1) // limit
        )
        
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        raise HTTPException(status_code=500, detail="Failed to list projects")

@router.post("/projects", response_model=ProposalProject)
async def create_project(
    project: ProposalProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new proposal generation project"""
    try:
        # Create project record
        db_project = DBProposalProject(
            uuid=str(uuid.uuid4()),
            name=project.name,
            description=project.description,
            client_name=project.client_name,
            opportunity_value=project.opportunity_value,
            submission_deadline=project.submission_deadline,
            status="created",
            progress_percentage=0,
            created_by_id=current_user.id,
            organization_id=current_user.organization_id,
            generation_settings=project.generation_settings,
            export_settings=project.export_settings,
            collaboration_settings=project.collaboration_settings
        )
        
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        
        logger.info(f"Created proposal project: {db_project.name} (ID: {db_project.id})")
        return db_project
        
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create project")

@router.get("/projects/{project_id}", response_model=ProposalProject)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific proposal project"""
    try:
        project = db.query(ProposalProject).filter(
            ProposalProject.id == project_id,
            ProposalProject.organization_id == current_user.organization_id
        ).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return project
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get project")

@router.put("/projects/{project_id}", response_model=ProposalProject)
async def update_project(
    project_id: int,
    project_update: ProposalProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a proposal project"""
    try:
        project = db.query(ProposalProject).filter(
            ProposalProject.id == project_id,
            ProposalProject.organization_id == current_user.organization_id
        ).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Update fields
        update_data = project_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
        
        project.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(project)
        
        return project
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating project {project_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update project")

@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a proposal project"""
    try:
        project = db.query(ProposalProject).filter(
            ProposalProject.id == project_id,
            ProposalProject.organization_id == current_user.organization_id
        ).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        db.delete(project)
        db.commit()
        
        return {"message": "Project deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting project {project_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete project")

# --- RFP Upload and Analysis Endpoints ---

@router.post("/projects/{project_id}/upload-rfp")
async def upload_rfp(
    project_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload RFP document for a project"""
    try:
        # Verify project exists
        project = db.query(ProposalProject).filter(
            ProposalProject.id == project_id,
            ProposalProject.organization_id == current_user.organization_id
        ).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        allowed_extensions = {'.pdf', '.docx', '.doc', '.txt'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file_ext} not supported. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save file
        uploads_dir = os.path.join(os.getcwd(), "uploads", "rfps")
        os.makedirs(uploads_dir, exist_ok=True)
        
        file_uuid = str(uuid.uuid4())
        file_path = os.path.join(uploads_dir, f"{file_uuid}{file_ext}")
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Update project
        project.rfp_filename = file.filename
        project.rfp_file_path = file_path
        project.rfp_file_size = len(content)
        project.rfp_upload_date = datetime.utcnow()
        project.status = "analyzing_rfp"
        project.updated_at = datetime.utcnow()
        
        db.commit()
        
        # Start background analysis
        background_tasks.add_task(
            analyze_rfp_background,
            project_id,
            file_path,
            current_user.id
        )
        
        return {
            "message": "RFP uploaded successfully",
            "filename": file.filename,
            "size": len(content),
            "status": "analysis_started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading RFP: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload RFP")

@router.post("/projects/{project_id}/analyze-rfp")
async def analyze_rfp_manual(
    project_id: int,
    analysis_request: RFPAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually trigger RFP analysis"""
    try:
        project = db.query(ProposalProject).filter(
            ProposalProject.id == project_id,
            ProposalProject.organization_id == current_user.organization_id
        ).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        if not project.rfp_file_path:
            raise HTTPException(status_code=400, detail="No RFP file uploaded")
        
        # Start analysis
        background_tasks.add_task(
            analyze_rfp_background,
            project_id,
            project.rfp_file_path,
            current_user.id
        )
        
        return {"message": "RFP analysis started"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting RFP analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to start analysis")

# --- Requirements Management Endpoints ---

@router.get("/projects/{project_id}/requirements", response_model=List[RFPRequirementAnalysis])
async def get_project_requirements(
    project_id: int,
    requirement_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get requirements for a project"""
    try:
        # Verify project access
        project = db.query(ProposalProject).filter(
            ProposalProject.id == project_id,
            ProposalProject.organization_id == current_user.organization_id
        ).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Build query
        query = db.query(RFPRequirementAnalysis).filter(
            RFPRequirementAnalysis.project_id == project_id
        )
        
        if requirement_type:
            query = query.filter(RFPRequirementAnalysis.requirement_type == requirement_type)
        
        requirements = query.all()
        return requirements
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting requirements: {e}")
        raise HTTPException(status_code=500, detail="Failed to get requirements")

@router.get("/projects/{project_id}/requirements/summary", response_model=RequirementsSummary)
async def get_requirements_summary(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get requirements summary for a project"""
    try:
        # Verify project access
        project = db.query(ProposalProject).filter(
            ProposalProject.id == project_id,
            ProposalProject.organization_id == current_user.organization_id
        ).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get requirements statistics
        requirements = db.query(RFPRequirementAnalysis).filter(
            RFPRequirementAnalysis.project_id == project_id
        ).all()
        
        total_requirements = len(requirements)
        
        # Count by type
        requirements_by_type = {}
        completed_responses = 0
        total_effort = 0
        
        for req in requirements:
            req_type = req.requirement_type.value if req.requirement_type else 'unknown'
            requirements_by_type[req_type] = requirements_by_type.get(req_type, 0) + 1
            
            if req.response_status == 'completed':
                completed_responses += 1
            
            if req.estimated_effort_hours:
                total_effort += req.estimated_effort_hours
        
        completion_percentage = (completed_responses / total_requirements * 100) if total_requirements > 0 else 0
        
        return RequirementsSummary(
            project_id=project_id,
            total_requirements=total_requirements,
            requirements_by_type=requirements_by_type,
            completed_responses=completed_responses,
            completion_percentage=completion_percentage,
            estimated_total_effort=total_effort
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting requirements summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get requirements summary")

# --- Content Template Endpoints ---

@router.get("/templates", response_model=ContentTemplateList)
async def list_templates(
    skip: int = 0,
    limit: int = 50,
    content_type: Optional[str] = None,
    industry: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List available content templates"""
    try:
        # Build query
        query = db.query(ContentTemplate).filter(
            ContentTemplate.is_approved == True
        ).filter(
            # Public templates or organization templates
            (ContentTemplate.is_public == True) | 
            (ContentTemplate.organization_id == current_user.organization_id)
        )
        
        if content_type:
            query = query.filter(ContentTemplate.content_type == content_type)
        
        # Filter by industry tag
        if industry:
            query = query.filter(ContentTemplate.industry_tags.contains(f'"{industry}"'))
        
        # Get total count
        total_count = query.count()
        
        # Get paginated results
        templates = query.offset(skip).limit(limit).all()
        
        return ContentTemplateList(
            templates=templates,
            total_count=total_count,
            page=skip // limit + 1,
            page_size=limit,
            total_pages=(total_count + limit - 1) // limit
        )
        
    except Exception as e:
        logger.error(f"Error listing templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to list templates")

@router.post("/templates", response_model=ContentTemplate)
async def create_template(
    template: ContentTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new content template"""
    try:
        # Calculate word count
        word_count = len(template.template_content.split())
        
        # Create template
        db_template = ContentTemplate(
            uuid=str(uuid.uuid4()),
            name=template.name,
            description=template.description,
            content_type=template.content_type,
            template_content=template.template_content,
            variables=template.variables,
            styling_info=template.styling_info,
            industry_tags=template.industry_tags,
            service_tags=template.service_tags,
            complexity_level=template.complexity_level,
            word_count=word_count,
            estimated_completion_time=max(15, word_count // 10),  # ~10 words per minute
            is_public=template.is_public,
            is_approved=False,  # Requires approval
            created_by_id=current_user.id,
            organization_id=current_user.organization_id
        )
        
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        
        return db_template
        
    except Exception as e:
        logger.error(f"Error creating template: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create template")

# --- Content Generation Endpoints ---

@router.post("/projects/{project_id}/generate-content")
async def generate_content(
    project_id: int,
    generation_request: ContentGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate content for proposal sections"""
    try:
        # Verify project
        project = db.query(ProposalProject).filter(
            ProposalProject.id == project_id,
            ProposalProject.organization_id == current_user.organization_id
        ).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Start content generation
        background_tasks.add_task(
            generate_content_background,
            project_id,
            generation_request.requirement_ids,
            generation_request.template_ids,
            generation_request.generation_settings,
            current_user.id
        )
        
        # Update project status
        project.content_generation_started = True
        project.status = "generating_content"
        project.updated_at = datetime.utcnow()
        db.commit()
        
        return {"message": "Content generation started"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting content generation: {e}")
        raise HTTPException(status_code=500, detail="Failed to start content generation")

@router.get("/projects/{project_id}/sections", response_model=GeneratedSectionList)
async def get_project_sections(
    project_id: int,
    content_type: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get generated sections for a project"""
    try:
        # Verify project access
        project = db.query(ProposalProject).filter(
            ProposalProject.id == project_id,
            ProposalProject.organization_id == current_user.organization_id
        ).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Build query
        query = db.query(GeneratedSection).filter(
            GeneratedSection.project_id == project_id,
            GeneratedSection.is_current_version == True
        )
        
        if content_type:
            query = query.filter(GeneratedSection.content_type == content_type)
        
        if status:
            query = query.filter(GeneratedSection.generation_status == status)
        
        # Get total count
        total_count = query.count()
        
        # Get paginated results
        sections = query.order_by(GeneratedSection.section_order).offset(skip).limit(limit).all()
        
        return GeneratedSectionList(
            sections=sections,
            total_count=total_count,
            page=skip // limit + 1,
            page_size=limit,
            total_pages=(total_count + limit - 1) // limit
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sections: {e}")
        raise HTTPException(status_code=500, detail="Failed to get sections")

# --- Statistics and Summary Endpoints ---

@router.get("/statistics", response_model=ProjectStatistics)
async def get_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get proposal generation statistics"""
    try:
        # Get project statistics
        projects = db.query(ProposalProject).filter(
            ProposalProject.organization_id == current_user.organization_id
        ).all()
        
        total_projects = len(projects)
        active_projects = len([p for p in projects if p.status not in ['completed', 'archived']])
        completed_projects = len([p for p in projects if p.status == 'completed'])
        
        # Count by status
        projects_by_status = {}
        for project in projects:
            status = project.status
            projects_by_status[status] = projects_by_status.get(status, 0) + 1
        
        # Get requirements and content statistics
        total_requirements = db.query(RFPRequirementAnalysis).join(ProposalProject).filter(
            ProposalProject.organization_id == current_user.organization_id
        ).count()
        
        total_content = db.query(GeneratedSection).join(ProposalProject).filter(
            ProposalProject.organization_id == current_user.organization_id
        ).count()
        
        return ProjectStatistics(
            total_projects=total_projects,
            active_projects=active_projects,
            completed_projects=completed_projects,
            projects_by_status=projects_by_status,
            total_requirements_processed=total_requirements,
            total_content_generated=total_content
        )
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")

# --- Background Task Functions ---

async def analyze_rfp_background(project_id: int, file_path: str, user_id: int):
    """Background task for RFP analysis"""
    try:
        logger.info(f"Starting background RFP analysis for project {project_id}")
        
        # Extract document content
        content = await document_service.extract_text(file_path)
        
        # Analyze with AI
        project_context = {
            'project_id': project_id,
            'project_name': f'Project {project_id}'
        }
        
        requirements = await proposal_generator.analyze_rfp_requirements(
            content, project_context
        )
        
        # Save requirements to database
        # Note: This would need proper database session handling in production
        logger.info(f"Extracted {len(requirements)} requirements for project {project_id}")
        
        # Update project status
        # Note: Update project analysis completion status
        
    except Exception as e:
        logger.error(f"Error in background RFP analysis: {e}")

async def generate_content_background(
    project_id: int,
    requirement_ids: List[int],
    template_ids: List[int],
    settings: Dict[str, Any],
    user_id: int
):
    """Background task for content generation"""
    try:
        logger.info(f"Starting background content generation for project {project_id}")
        
        # Get requirements and generate content
        # Note: This would implement the actual content generation logic
        logger.info(f"Content generation completed for project {project_id}")
        
    except Exception as e:
        logger.error(f"Error in background content generation: {e}")