"""
Compliance Analysis API Endpoints for TenderWise AI Platform
Module 2: Proposal Compliance & Vendor Assessment

REST API endpoints for managing compliance analysis workflow:
- Upload RFP and vendor proposals
- Execute compliance analysis
- Retrieve analysis results and rankings
- Export compliance matrices
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ...core.database_simple import get_db
from ...api.dependencies_simple import get_current_active_user
from ...models import User
from ...models.compliance_analysis import (
    ComplianceAnalysis, RFPRequirement, VendorProposal, ComplianceMatrix, ComplianceScore,
    AnalysisStatus, ComplianceStatus
)
from ...services.ai.compliance_analyzer import ComplianceAnalyzerService
from ...services.document.document_extractor import document_extractor
from ...schemas.compliance_analysis import (
    ComplianceAnalysisResponse, ComplianceAnalysisCreate, ComplianceMatrixResponse,
    VendorRankingResponse, ComplianceStatisticsResponse
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["compliance-analysis"])

# Initialize services
compliance_analyzer = ComplianceAnalyzerService()


@router.post("/upload", response_model=ComplianceAnalysisResponse)
async def upload_rfp_and_proposals(
    background_tasks: BackgroundTasks,
    rfp_file: UploadFile = File(..., description="RFP document (PDF, DOCX, DOC, TXT)"),
    proposal_files: List[UploadFile] = File(..., description="Vendor proposal documents"),
    company_context: str = Form("", description="Company context for analysis"),
    analysis_name: str = Form("", description="Name for this analysis"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload RFP document and vendor proposals for compliance analysis
    
    This endpoint:
    1. Validates uploaded files
    2. Extracts content from documents
    3. Creates compliance analysis record
    4. Initiates background analysis process
    """
    try:
        logger.info(f"Starting compliance analysis upload for user {current_user.id}")
        
        # Validate file uploads
        if len(proposal_files) > 10:  # Limit to 10 proposals
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 proposal files allowed per analysis"
            )
        
        # Extract RFP content
        logger.info("Extracting RFP content")
        # Read file content
        rfp_file_content = await rfp_file.read()
        rfp_content = await document_extractor.extract_text(rfp_file_content, rfp_file.filename)
        
        if not rfp_content or len(rfp_content.strip()) < 100:
            raise HTTPException(
                status_code=400,
                detail="RFP document appears to be empty or too short for analysis"
            )
        
        # Create compliance analysis record
        analysis = ComplianceAnalysis(
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            rfp_document_name=rfp_file.filename,
            rfp_content=rfp_content,
            rfp_metadata={
                "original_filename": rfp_file.filename,
                "file_size": rfp_file.size,
                "content_type": rfp_file.content_type,
                "company_context": company_context,
                "analysis_name": analysis_name or f"Analysis {rfp_file.filename}"
            },
            analysis_status=AnalysisStatus.PENDING,
            total_proposals=len(proposal_files)
        )
        
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        logger.info(f"Created compliance analysis record: {analysis.id}")
        
        # Process proposal files
        proposals_data = []
        for i, proposal_file in enumerate(proposal_files):
            try:
                # Extract proposal content
                proposal_file_content = await proposal_file.read()
                proposal_content = await document_extractor.extract_text(proposal_file_content, proposal_file.filename)
                
                if not proposal_content or len(proposal_content.strip()) < 50:
                    logger.warning(f"Proposal file {proposal_file.filename} appears empty, skipping")
                    continue
                
                # Create vendor proposal record
                vendor_proposal = VendorProposal(
                    compliance_analysis_id=analysis.id,
                    vendor_name=f"Vendor {i+1}",  # Default name, can be enhanced
                    document_name=proposal_file.filename,
                    document_size_bytes=proposal_file.size or 0,
                    document_type=proposal_file.content_type,
                    proposal_content=proposal_content,
                    proposal_metadata={
                        "original_filename": proposal_file.filename,
                        "file_size": proposal_file.size,
                        "content_type": proposal_file.content_type,
                        "upload_order": i + 1
                    },
                    word_count=len(proposal_content.split())
                )
                
                db.add(vendor_proposal)
                proposals_data.append(vendor_proposal)
                
            except Exception as e:
                logger.error(f"Error processing proposal file {proposal_file.filename}: {e}")
                continue
        
        # Update analysis with actual proposal count
        analysis.total_proposals = len(proposals_data)
        db.commit()
        
        if not proposals_data:
            raise HTTPException(
                status_code=400,
                detail="No valid proposal files could be processed"
            )
        
        logger.info(f"Processed {len(proposals_data)} proposal files")
        
        # Start background analysis
        background_tasks.add_task(
            run_compliance_analysis_background,
            analysis.id,
            db.bind.url
        )
        
        return ComplianceAnalysisResponse(
            id=analysis.id,
            rfp_document_name=analysis.rfp_document_name,
            analysis_status=analysis.analysis_status,
            total_requirements=analysis.total_requirements,
            total_proposals=analysis.total_proposals,
            processing_progress=analysis.processing_progress,
            created_at=analysis.created_at,
            message="Upload successful. Analysis started in background."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in upload_rfp_and_proposals: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/analyze/{analysis_id}")
async def start_compliance_analysis(
    analysis_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Start or restart compliance analysis for existing analysis record
    """
    try:
        # Get analysis record
        analysis = db.query(ComplianceAnalysis).filter(
            ComplianceAnalysis.id == analysis_id,
            ComplianceAnalysis.user_id == current_user.id
        ).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        if analysis.analysis_status == AnalysisStatus.PROCESSING:
            raise HTTPException(status_code=400, detail="Analysis is already in progress")
        
        # Reset analysis status
        analysis.analysis_status = AnalysisStatus.PROCESSING
        analysis.processing_progress = 0.0
        analysis.error_message = None
        db.commit()
        
        # Start background analysis
        background_tasks.add_task(
            run_compliance_analysis_background,
            analysis_id,
            db.bind.url
        )
        
        return {"message": "Analysis started", "analysis_id": analysis_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start analysis: {str(e)}")


@router.get("/results/{analysis_id}", response_model=ComplianceAnalysisResponse)
async def get_analysis_results(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get compliance analysis results and summary
    """
    try:
        analysis = db.query(ComplianceAnalysis).filter(
            ComplianceAnalysis.id == analysis_id,
            ComplianceAnalysis.user_id == current_user.id
        ).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return ComplianceAnalysisResponse(
            id=analysis.id,
            rfp_document_name=analysis.rfp_document_name,
            analysis_status=analysis.analysis_status,
            total_requirements=analysis.total_requirements,
            total_proposals=analysis.total_proposals,
            processing_progress=analysis.processing_progress,
            analysis_results=analysis.analysis_results,
            processing_time_seconds=analysis.processing_time_seconds,
            error_message=analysis.error_message,
            created_at=analysis.created_at,
            updated_at=analysis.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis results: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get results: {str(e)}")


@router.get("/matrix/{analysis_id}", response_model=List[ComplianceMatrixResponse])
async def get_compliance_matrix(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed compliance matrix for analysis
    """
    try:
        # Verify user has access to analysis
        analysis = db.query(ComplianceAnalysis).filter(
            ComplianceAnalysis.id == analysis_id,
            ComplianceAnalysis.user_id == current_user.id
        ).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Get compliance matrix with related data
        matrix_records = db.query(ComplianceMatrix).filter(
            ComplianceMatrix.compliance_analysis_id == analysis_id
        ).all()
        
        # Get requirements and proposals for context
        requirements = {req.id: req for req in analysis.requirements}
        proposals = {prop.id: prop for prop in analysis.proposals}
        
        # Build response
        matrix_response = []
        for record in matrix_records:
            requirement = requirements.get(record.requirement_id)
            proposal = proposals.get(record.proposal_id)
            
            matrix_response.append(ComplianceMatrixResponse(
                id=record.id,
                requirement_id=record.requirement_id,
                proposal_id=record.proposal_id,
                requirement_text=requirement.requirement_text if requirement else "",
                requirement_type=requirement.requirement_type if requirement else None,
                vendor_name=proposal.vendor_name if proposal else "",
                compliance_status=record.compliance_status,
                compliance_score=record.compliance_score,
                evidence_text=record.evidence_text,
                gap_description=record.gap_description,
                recommendations=record.recommendations,
                keywords_matched=record.keywords_matched
            ))
        
        return matrix_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting compliance matrix: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get matrix: {str(e)}")


@router.get("/rankings/{analysis_id}", response_model=List[VendorRankingResponse])
async def get_vendor_rankings(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get vendor rankings based on compliance scores
    """
    try:
        # Verify user has access to analysis
        analysis = db.query(ComplianceAnalysis).filter(
            ComplianceAnalysis.id == analysis_id,
            ComplianceAnalysis.user_id == current_user.id
        ).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Get compliance scores ordered by rank
        scores = db.query(ComplianceScore).filter(
            ComplianceScore.compliance_analysis_id == analysis_id
        ).order_by(ComplianceScore.rank_position).all()
        
        # Get proposals for vendor information
        proposals = {prop.id: prop for prop in analysis.proposals}
        
        # Build response
        rankings = []
        for score in scores:
            proposal = proposals.get(score.proposal_id)
            if not proposal:
                continue
                
            rankings.append(VendorRankingResponse(
                proposal_id=score.proposal_id,
                vendor_name=proposal.vendor_name,
                overall_score=score.overall_score,
                rank_position=score.rank_position,
                category_scores={
                    "technical": score.technical_score,
                    "functional": score.functional_score,
                    "commercial": score.commercial_score,
                    "legal": score.legal_score,
                    "operational": score.operational_score
                },
                compliance_distribution={
                    "compliant": score.total_compliant,
                    "partial": score.total_partial,
                    "non_compliant": score.total_non_compliant,
                    "not_addressed": score.total_not_addressed
                },
                strengths=score.strength_areas,
                weaknesses=score.weakness_areas,
                recommendations=score.recommendations
            ))
        
        return rankings
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting vendor rankings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get rankings: {str(e)}")


@router.get("/statistics", response_model=ComplianceStatisticsResponse)
async def get_compliance_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get overall compliance analysis statistics for the user
    """
    try:
        # Get user's analyses
        analyses = db.query(ComplianceAnalysis).filter(
            ComplianceAnalysis.user_id == current_user.id
        ).all()
        
        total_analyses = len(analyses)
        completed_analyses = sum(1 for a in analyses if a.analysis_status == AnalysisStatus.COMPLETED)
        processing_analyses = sum(1 for a in analyses if a.analysis_status == AnalysisStatus.PROCESSING)
        failed_analyses = sum(1 for a in analyses if a.analysis_status == AnalysisStatus.FAILED)
        
        # Calculate totals
        total_requirements = sum(a.total_requirements for a in analyses)
        total_proposals = sum(a.total_proposals for a in analyses)
        
        # Get recent analyses
        recent_analyses = db.query(ComplianceAnalysis).filter(
            ComplianceAnalysis.user_id == current_user.id
        ).order_by(desc(ComplianceAnalysis.created_at)).limit(5).all()
        
        return ComplianceStatisticsResponse(
            total_analyses=total_analyses,
            completed_analyses=completed_analyses,
            processing_analyses=processing_analyses,
            failed_analyses=failed_analyses,
            total_requirements_analyzed=total_requirements,
            total_proposals_analyzed=total_proposals,
            recent_analyses=[
                {
                    "id": a.id,
                    "rfp_document_name": a.rfp_document_name,
                    "status": a.analysis_status.value,
                    "created_at": a.created_at,
                    "total_proposals": a.total_proposals
                }
                for a in recent_analyses
            ]
        )
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@router.delete("/{analysis_id}")
async def delete_analysis(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete compliance analysis and all related data
    """
    try:
        analysis = db.query(ComplianceAnalysis).filter(
            ComplianceAnalysis.id == analysis_id,
            ComplianceAnalysis.user_id == current_user.id
        ).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Delete analysis (cascades to related records)
        db.delete(analysis)
        db.commit()
        
        return {"message": "Analysis deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete analysis: {str(e)}")


# Background task function
async def run_compliance_analysis_background(analysis_id: str, db_url: str):
    """
    Background task to run compliance analysis
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    try:
        # Create new database session for background task
        engine = create_engine(str(db_url))
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        logger.info(f"Starting background compliance analysis for {analysis_id}")
        
        # Get analysis record
        analysis = db.query(ComplianceAnalysis).filter(
            ComplianceAnalysis.id == analysis_id
        ).first()
        
        if not analysis:
            logger.error(f"Analysis {analysis_id} not found")
            return
        
        # Update status to processing
        analysis.analysis_status = AnalysisStatus.PROCESSING
        analysis.processing_progress = 10.0
        db.commit()
        
        start_time = asyncio.get_event_loop().time()
        
        # Step 1: Extract requirements from RFP (30% progress)
        logger.info("Extracting requirements from RFP")
        requirements_data = await compliance_analyzer.extract_requirements_from_rfp(
            analysis.rfp_content
        )
        
        # Save requirements to database
        for req_data in requirements_data:
            requirement = RFPRequirement(
                compliance_analysis_id=analysis.id,
                requirement_text=req_data['text'],
                requirement_summary=req_data['summary'],
                requirement_category=req_data['category'],
                requirement_type=req_data['type'],
                priority_level=req_data['priority'],
                section_reference=req_data['section_reference'],
                weight=req_data['weight'],
                keywords=req_data['keywords'],
                extraction_confidence=req_data['extraction_confidence']
            )
            db.add(requirement)
        
        analysis.total_requirements = len(requirements_data)
        analysis.processing_progress = 30.0
        db.commit()
        
        # Get saved requirements
        requirements = db.query(RFPRequirement).filter(
            RFPRequirement.compliance_analysis_id == analysis.id
        ).all()
        
        proposals = db.query(VendorProposal).filter(
            VendorProposal.compliance_analysis_id == analysis.id
        ).all()
        
        logger.info(f"Processing {len(requirements)} requirements against {len(proposals)} proposals")
        
        # Step 2: Analyze compliance for each proposal (60% progress)
        all_matches = []
        progress_step = 30.0 / len(proposals) if proposals else 30.0
        
        for i, proposal in enumerate(proposals):
            matches = await compliance_analyzer.analyze_proposal_compliance(
                requirements, proposal
            )
            all_matches.extend(matches)
            
            # Save compliance matrix records
            for match in matches:
                matrix_record = ComplianceMatrix(
                    compliance_analysis_id=analysis.id,
                    requirement_id=match.requirement_id,
                    proposal_id=match.proposal_id,
                    compliance_status=match.compliance_status,
                    compliance_score=match.compliance_score,
                    confidence_level=match.confidence_level,
                    evidence_text=match.evidence_text,
                    gap_description=match.gap_description,
                    recommendations=match.recommendations,
                    keywords_matched=match.keywords_matched
                )
                db.add(matrix_record)
            
            # Update progress
            analysis.processing_progress = 30.0 + (i + 1) * progress_step
            db.commit()
        
        # Step 3: Calculate vendor rankings (90% progress)
        logger.info("Calculating vendor rankings")
        compliance_matrix = db.query(ComplianceMatrix).filter(
            ComplianceMatrix.compliance_analysis_id == analysis.id
        ).all()
        
        rankings = await compliance_analyzer.calculate_vendor_rankings(
            compliance_matrix, proposals, requirements
        )
        
        # Save compliance scores
        for ranking in rankings:
            score_record = ComplianceScore(
                compliance_analysis_id=analysis.id,
                proposal_id=ranking.proposal_id,
                overall_score=ranking.overall_score,
                rank_position=ranking.rank_position,
                technical_score=ranking.category_scores.get('technical'),
                functional_score=ranking.category_scores.get('functional'),
                commercial_score=ranking.category_scores.get('commercial'),
                legal_score=ranking.category_scores.get('legal'),
                operational_score=ranking.category_scores.get('operational'),
                total_requirements=len(requirements),
                total_compliant=ranking.compliance_distribution.get('compliant', 0),
                total_partial=ranking.compliance_distribution.get('partial', 0),
                total_non_compliant=ranking.compliance_distribution.get('non_compliant', 0),
                total_not_addressed=ranking.compliance_distribution.get('not_addressed', 0),
                strength_areas=ranking.strengths,
                weakness_areas=ranking.weaknesses,
                recommendations=ranking.recommendations
            )
            db.add(score_record)
        
        analysis.processing_progress = 90.0
        db.commit()
        
        # Step 4: Generate analysis summary (100% progress)
        end_time = asyncio.get_event_loop().time()
        processing_time = end_time - start_time
        
        # Create analysis summary
        analysis_summary = {
            "requirements_extracted": len(requirements),
            "proposals_analyzed": len(proposals),
            "top_vendor": rankings[0].vendor_name if rankings else None,
            "top_score": rankings[0].overall_score if rankings else 0,
            "average_score": sum(r.overall_score for r in rankings) / len(rankings) if rankings else 0,
            "compliance_overview": {
                "total_assessments": len(all_matches),
                "compliant": sum(1 for m in all_matches if m.compliance_status == ComplianceStatus.COMPLIANT),
                "partial": sum(1 for m in all_matches if m.compliance_status == ComplianceStatus.PARTIAL),
                "non_compliant": sum(1 for m in all_matches if m.compliance_status == ComplianceStatus.NON_COMPLIANT),
                "not_addressed": sum(1 for m in all_matches if m.compliance_status == ComplianceStatus.NOT_ADDRESSED)
            }
        }
        
        # Complete analysis
        analysis.analysis_status = AnalysisStatus.COMPLETED
        analysis.processing_progress = 100.0
        analysis.analysis_results = analysis_summary
        analysis.processing_time_seconds = processing_time
        db.commit()
        
        logger.info(f"Compliance analysis {analysis_id} completed successfully in {processing_time:.2f} seconds")
        
    except Exception as e:
        logger.error(f"Error in background compliance analysis: {e}")
        
        # Update analysis with error
        if 'analysis' in locals() and 'db' in locals():
            analysis.analysis_status = AnalysisStatus.FAILED
            analysis.error_message = str(e)
            db.commit()
    
    finally:
        if 'db' in locals():
            db.close()