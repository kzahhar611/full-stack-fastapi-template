"""
TenderWise AI - File Service
"""

import os
import uuid
import aiofiles
from typing import Optional, List
from datetime import datetime
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from core.config import settings
from models.rfp import RFPDocument
from models.user import User

class FileService:
    """File handling service"""
    
    # Allowed file types
    ALLOWED_EXTENSIONS = {
        'pdf', 'doc', 'docx', 'txt', 'xlsx', 'xls', 
        'ppt', 'pptx', 'jpg', 'jpeg', 'png', 'gif'
    }
    
    # Allowed MIME types
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-powerpoint',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'image/jpeg',
        'image/png',
        'image/gif'
    }

    @staticmethod
    def validate_file(file: UploadFile) -> bool:
        """Validate uploaded file"""
        # Check file size
        if hasattr(file, 'size') and file.size > settings.MAX_FILE_SIZE:
            return False
        
        # Check file extension
        if file.filename:
            file_ext = file.filename.split('.')[-1].lower()
            if file_ext not in FileService.ALLOWED_EXTENSIONS:
                return False
        
        # Check MIME type
        if file.content_type not in FileService.ALLOWED_MIME_TYPES:
            return False
        
        return True

    @staticmethod
    def generate_file_path(original_filename: str, folder: str = "rfp_documents") -> tuple[str, str]:
        """Generate unique file path"""
        # Create folder if it doesn't exist
        upload_dir = os.path.join(settings.UPLOAD_FOLDER, folder)
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        file_ext = original_filename.split('.')[-1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        return file_path, unique_filename

    @staticmethod
    async def save_file(file: UploadFile, file_path: str) -> int:
        """Save uploaded file to disk"""
        try:
            # Read file content
            content = await file.read()
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
            
            return len(content)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error saving file: {str(e)}"
            )

    @staticmethod
    async def upload_rfp_document(
        db: Session,
        rfp_id: int,
        file: UploadFile,
        uploaded_by: int,
        document_type: Optional[str] = None
    ) -> RFPDocument:
        """Upload document for RFP"""
        # Validate file
        if not FileService.validate_file(file):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type or size too large"
            )
        
        # Generate file path
        file_path, filename = FileService.generate_file_path(file.filename or "document")
        
        # Save file
        file_size = await FileService.save_file(file, file_path)
        
        # Create database record
        document = RFPDocument(
            rfp_id=rfp_id,
            filename=filename,
            original_filename=file.filename or "document",
            file_path=file_path,
            file_size=file_size,
            content_type=file.content_type or "application/octet-stream",
            document_type=document_type,
            processing_status="uploaded",
            uploaded_by=uploaded_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        return document

    @staticmethod
    def delete_file(file_path: str) -> bool:
        """Delete file from disk"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False

    @staticmethod
    def delete_rfp_document(db: Session, document_id: int) -> bool:
        """Delete RFP document"""
        document = db.query(RFPDocument).filter(RFPDocument.id == document_id).first()
        if not document:
            return False
        
        # Delete file from disk
        FileService.delete_file(document.file_path)
        
        # Delete database record
        db.delete(document)
        db.commit()
        
        return True

    @staticmethod
    def get_rfp_documents(db: Session, rfp_id: int) -> List[RFPDocument]:
        """Get all documents for an RFP"""
        return db.query(RFPDocument).filter(RFPDocument.rfp_id == rfp_id).all()

    @staticmethod
    def get_document_by_id(db: Session, document_id: int) -> Optional[RFPDocument]:
        """Get document by ID"""
        return db.query(RFPDocument).filter(RFPDocument.id == document_id).first()