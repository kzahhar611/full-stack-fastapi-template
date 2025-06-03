"""
RFP Document Management API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime
import os
import mimetypes

from ...core.database_enhanced import get_db
from ...api.dependencies_simple import get_current_user
from ...models.user_simple import User
from ...models.rfp_enhanced import RFPEnhanced, RFPDocument, DocumentType
from ...schemas.rfp_enhanced import RFPDocumentResponse, RFPDocumentUpdate
from ...services.file_storage import file_storage_service

router = APIRouter()


# =============================================================================
# DOCUMENT UPLOAD & MANAGEMENT
# =============================================================================

@router.post("/{rfp_id}/documents", response_model=RFPDocumentResponse)
async def upload_rfp_document(
    rfp_id: int,
    file: UploadFile = File(...),
    document_type: DocumentType = Form(DocumentType.ATTACHMENT),
    description: Optional[str] = Form(None),
    is_public: bool = Form(False),
    is_required: bool = Form(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload document to RFP"""
    
    # Check if RFP exists and user has access
    rfp = db.query(RFPEnhanced).filter(
        RFPEnhanced.id == rfp_id,
        RFPEnhanced.organization_id == current_user.organization_id
    ).first()
    
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    
    # Check permissions (creator, admin, or manager can upload)
    if (rfp.created_by_id != current_user.id and 
        current_user.role.value not in ["super_admin", "admin", "manager"]):
        raise HTTPException(status_code=403, detail="Not authorized to upload documents to this RFP")
    
    try:
        # Save file using storage service
        file_path, secure_filename, file_size, mime_type = await file_storage_service.save_file(
            file, subfolder=f"rfp_{rfp_id}"
        )
        
        # Create document record
        document = RFPDocument(
            rfp_id=rfp_id,
            filename=secure_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type,
            document_type=document_type,
            description=description,
            is_public=is_public,
            is_required=is_required,
            uploaded_by_id=current_user.id
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Return response with download URL
        response_data = {
            **document.__dict__,
            "download_url": f"/api/v1/rfps-enhanced/{rfp_id}/documents/{document.id}/download"
        }
        
        return RFPDocumentResponse(**response_data)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to upload document: {str(e)}")


@router.get("/{rfp_id}/documents", response_model=List[RFPDocumentResponse])
async def list_rfp_documents(
    rfp_id: int,
    include_private: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List documents for an RFP"""
    
    # Check if RFP exists and user has access
    rfp = db.query(RFPEnhanced).filter(
        RFPEnhanced.id == rfp_id,
        RFPEnhanced.organization_id == current_user.organization_id
    ).first()
    
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    
    # Build query
    query = db.query(RFPDocument).filter(RFPDocument.rfp_id == rfp_id)
    
    # Filter by visibility
    if not include_private or current_user.role.value in ["viewer"]:
        query = query.filter(RFPDocument.is_public == True)
    
    documents = query.order_by(RFPDocument.upload_date.desc()).all()
    
    # Add download URLs
    response_docs = []
    for doc in documents:
        doc_data = {
            **doc.__dict__,
            "download_url": f"/api/v1/rfps-enhanced/{rfp_id}/documents/{doc.id}/download"
        }
        response_docs.append(RFPDocumentResponse(**doc_data))
    
    return response_docs


@router.get("/{rfp_id}/documents/{document_id}", response_model=RFPDocumentResponse)
async def get_rfp_document(
    rfp_id: int,
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get document metadata"""
    
    document = db.query(RFPDocument).filter(
        RFPDocument.id == document_id,
        RFPDocument.rfp_id == rfp_id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check RFP access
    rfp = db.query(RFPEnhanced).filter(
        RFPEnhanced.id == rfp_id,
        RFPEnhanced.organization_id == current_user.organization_id
    ).first()
    
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    
    # Check document visibility
    if not document.is_public and current_user.role.value in ["viewer"]:
        raise HTTPException(status_code=403, detail="Access denied to private document")
    
    response_data = {
        **document.__dict__,
        "download_url": f"/api/v1/rfps-enhanced/{rfp_id}/documents/{document.id}/download"
    }
    
    return RFPDocumentResponse(**response_data)


@router.put("/{rfp_id}/documents/{document_id}", response_model=RFPDocumentResponse)
async def update_rfp_document(
    rfp_id: int,
    document_id: int,
    document_update: RFPDocumentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update document metadata"""
    
    document = db.query(RFPDocument).filter(
        RFPDocument.id == document_id,
        RFPDocument.rfp_id == rfp_id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check RFP access and permissions
    rfp = db.query(RFPEnhanced).filter(
        RFPEnhanced.id == rfp_id,
        RFPEnhanced.organization_id == current_user.organization_id
    ).first()
    
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    
    # Check permissions (uploader, creator, admin, or manager can edit)
    if (document.uploaded_by_id != current_user.id and 
        rfp.created_by_id != current_user.id and
        current_user.role.value not in ["super_admin", "admin", "manager"]):
        raise HTTPException(status_code=403, detail="Not authorized to edit this document")
    
    # Update fields
    update_data = document_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(document, field, value)
    
    db.commit()
    db.refresh(document)
    
    response_data = {
        **document.__dict__,
        "download_url": f"/api/v1/rfps-enhanced/{rfp_id}/documents/{document.id}/download"
    }
    
    return RFPDocumentResponse(**response_data)


@router.delete("/{rfp_id}/documents/{document_id}")
async def delete_rfp_document(
    rfp_id: int,
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete document"""
    
    document = db.query(RFPDocument).filter(
        RFPDocument.id == document_id,
        RFPDocument.rfp_id == rfp_id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check RFP access and permissions
    rfp = db.query(RFPEnhanced).filter(
        RFPEnhanced.id == rfp_id,
        RFPEnhanced.organization_id == current_user.organization_id
    ).first()
    
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    
    # Check permissions
    if (document.uploaded_by_id != current_user.id and 
        rfp.created_by_id != current_user.id and
        current_user.role.value not in ["super_admin", "admin", "manager"]):
        raise HTTPException(status_code=403, detail="Not authorized to delete this document")
    
    # Delete file from storage
    await file_storage_service.delete_file(document.file_path)
    
    # Delete database record
    db.delete(document)
    db.commit()
    
    return {"message": "Document deleted successfully"}


@router.get("/{rfp_id}/documents/{document_id}/download")
async def download_rfp_document(
    rfp_id: int,
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download document file"""
    
    document = db.query(RFPDocument).filter(
        RFPDocument.id == document_id,
        RFPDocument.rfp_id == rfp_id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check RFP access
    rfp = db.query(RFPEnhanced).filter(
        RFPEnhanced.id == rfp_id,
        RFPEnhanced.organization_id == current_user.organization_id
    ).first()
    
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    
    # Check document visibility
    if not document.is_public and current_user.role.value in ["viewer"]:
        raise HTTPException(status_code=403, detail="Access denied to private document")
    
    # Get file path
    file_path = file_storage_service.get_file_path(document.file_path)
    
    if not file_storage_service.file_exists(document.file_path):
        raise HTTPException(status_code=404, detail="File not found on storage")
    
    # Increment download count
    rfp.download_count += 1
    db.commit()
    
    # Return file response
    return FileResponse(
        path=file_path,
        filename=document.original_filename,
        media_type=document.mime_type
    )


# =============================================================================
# BULK OPERATIONS
# =============================================================================

@router.post("/{rfp_id}/documents/bulk-upload")
async def bulk_upload_documents(
    rfp_id: int,
    files: List[UploadFile] = File(...),
    document_type: DocumentType = Form(DocumentType.ATTACHMENT),
    is_public: bool = Form(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Bulk upload multiple documents"""
    
    # Check if RFP exists and user has access
    rfp = db.query(RFPEnhanced).filter(
        RFPEnhanced.id == rfp_id,
        RFPEnhanced.organization_id == current_user.organization_id
    ).first()
    
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    
    # Check permissions
    if (rfp.created_by_id != current_user.id and 
        current_user.role.value not in ["super_admin", "admin", "manager"]):
        raise HTTPException(status_code=403, detail="Not authorized to upload documents to this RFP")
    
    # Limit number of files
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed per bulk upload")
    
    uploaded_documents = []
    failed_uploads = []
    
    for file in files:
        try:
            # Save file
            file_path, secure_filename, file_size, mime_type = await file_storage_service.save_file(
                file, subfolder=f"rfp_{rfp_id}"
            )
            
            # Create document record
            document = RFPDocument(
                rfp_id=rfp_id,
                filename=secure_filename,
                original_filename=file.filename,
                file_path=file_path,
                file_size=file_size,
                mime_type=mime_type,
                document_type=document_type,
                description=f"Bulk uploaded: {file.filename}",
                is_public=is_public,
                is_required=False,
                uploaded_by_id=current_user.id
            )
            
            db.add(document)
            db.flush()
            
            uploaded_documents.append({
                "original_filename": file.filename,
                "document_id": document.id,
                "status": "success"
            })
            
        except Exception as e:
            failed_uploads.append({
                "original_filename": file.filename,
                "status": "failed",
                "error": str(e)
            })
    
    db.commit()
    
    return {
        "message": f"Bulk upload completed. {len(uploaded_documents)} successful, {len(failed_uploads)} failed.",
        "uploaded_documents": uploaded_documents,
        "failed_uploads": failed_uploads
    }


@router.delete("/{rfp_id}/documents/bulk-delete")
async def bulk_delete_documents(
    rfp_id: int,
    document_ids: List[int],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bulk delete multiple documents"""
    
    # Check if RFP exists and user has access
    rfp = db.query(RFPEnhanced).filter(
        RFPEnhanced.id == rfp_id,
        RFPEnhanced.organization_id == current_user.organization_id
    ).first()
    
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    
    # Check permissions
    if (rfp.created_by_id != current_user.id and 
        current_user.role.value not in ["super_admin", "admin", "manager"]):
        raise HTTPException(status_code=403, detail="Not authorized to delete documents from this RFP")
    
    # Get documents
    documents = db.query(RFPDocument).filter(
        RFPDocument.id.in_(document_ids),
        RFPDocument.rfp_id == rfp_id
    ).all()
    
    if not documents:
        raise HTTPException(status_code=404, detail="No documents found")
    
    deleted_count = 0
    failed_deletes = []
    
    for document in documents:
        try:
            # Delete file from storage
            await file_storage_service.delete_file(document.file_path)
            
            # Delete database record
            db.delete(document)
            deleted_count += 1
            
        except Exception as e:
            failed_deletes.append({
                "document_id": document.id,
                "filename": document.original_filename,
                "error": str(e)
            })
    
    db.commit()
    
    return {
        "message": f"Bulk delete completed. {deleted_count} documents deleted.",
        "deleted_count": deleted_count,
        "failed_deletes": failed_deletes
    }