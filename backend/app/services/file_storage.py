"""
File storage service for RFP documents and attachments
"""
import os
import uuid
import shutil
import magic
import aiofiles
from pathlib import Path
from typing import Optional, BinaryIO, Tuple, List
from fastapi import HTTPException, UploadFile
from ..core.config import get_settings


class FileStorageService:
    """Service for handling file uploads and storage"""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_upload_dir = Path(self.settings.UPLOAD_DIR)
        self.max_file_size = self.settings.MAX_FILE_SIZE_MB * 1024 * 1024  # Convert to bytes
        self.allowed_extensions = {
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.txt', '.rtf', '.zip', '.rar', '.7z',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff',
            '.dwg', '.dxf', '.svg'
        }
        self.allowed_mime_types = {
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'text/plain',
            'application/rtf',
            'application/zip',
            'application/x-rar-compressed',
            'application/x-7z-compressed',
            'image/jpeg',
            'image/png',
            'image/gif',
            'image/bmp',
            'image/tiff',
            'image/svg+xml',
            'application/octet-stream'  # For CAD files and others
        }
        
        # Ensure upload directory exists
        self._ensure_upload_dir()
    
    def _ensure_upload_dir(self) -> None:
        """Ensure upload directory exists"""
        try:
            self.base_upload_dir.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            (self.base_upload_dir / "rfp_documents").mkdir(exist_ok=True)
            (self.base_upload_dir / "temp").mkdir(exist_ok=True)
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create upload directory: {str(e)}"
            )
    
    def validate_file(self, file: UploadFile) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded file
        Returns: (is_valid, error_message)
        """
        # Check file size
        if hasattr(file.file, 'seek') and hasattr(file.file, 'tell'):
            # Get file size
            file.file.seek(0, 2)  # Seek to end
            file_size = file.file.tell()
            file.file.seek(0)  # Reset to beginning
            
            if file_size > self.max_file_size:
                return False, f"File size ({file_size / (1024*1024):.1f} MB) exceeds maximum allowed size ({self.settings.MAX_FILE_SIZE_MB} MB)"
        
        # Check filename
        if not file.filename:
            return False, "Filename is required"
        
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in self.allowed_extensions:
            return False, f"File extension '{file_ext}' is not allowed. Allowed extensions: {', '.join(sorted(self.allowed_extensions))}"
        
        # Check MIME type
        if file.content_type and file.content_type not in self.allowed_mime_types:
            return False, f"File type '{file.content_type}' is not allowed"
        
        return True, None
    
    def generate_secure_filename(self, original_filename: str) -> str:
        """Generate a secure filename with UUID"""
        file_ext = Path(original_filename).suffix.lower()
        secure_name = f"{uuid.uuid4().hex}{file_ext}"
        return secure_name
    
    async def save_file(
        self,
        file: UploadFile,
        subfolder: str = "rfp_documents"
    ) -> Tuple[str, str, int, str]:
        """
        Save uploaded file to storage
        Returns: (file_path, secure_filename, file_size, detected_mime_type)
        """
        # Validate file
        is_valid, error_msg = self.validate_file(file)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Generate secure filename
        secure_filename = self.generate_secure_filename(file.filename)
        
        # Create subfolder path
        subfolder_path = self.base_upload_dir / subfolder
        subfolder_path.mkdir(exist_ok=True)
        
        # Full file path
        file_path = subfolder_path / secure_filename
        
        try:
            # Save file
            async with aiofiles.open(file_path, 'wb') as buffer:
                while True:
                    chunk = await file.read(8192)  # Read in 8KB chunks
                    if not chunk:
                        break
                    await buffer.write(chunk)
            
            # Get file info
            file_size = file_path.stat().st_size
            
            # Detect MIME type
            try:
                detected_mime_type = magic.from_file(str(file_path), mime=True)
            except Exception:
                detected_mime_type = file.content_type or "application/octet-stream"
            
            # Return relative path for database storage
            relative_path = str(file_path.relative_to(self.base_upload_dir))
            
            return relative_path, secure_filename, file_size, detected_mime_type
            
        except Exception as e:
            # Clean up file if save failed
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save file: {str(e)}"
            )
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file from storage"""
        try:
            full_path = self.base_upload_dir / file_path
            if full_path.exists() and full_path.is_file():
                full_path.unlink()
                return True
            return False
        except Exception:
            return False
    
    def get_file_path(self, relative_path: str) -> Path:
        """Get full file path from relative path"""
        return self.base_upload_dir / relative_path
    
    def file_exists(self, relative_path: str) -> bool:
        """Check if file exists"""
        full_path = self.get_file_path(relative_path)
        return full_path.exists() and full_path.is_file()
    
    async def copy_file(self, source_path: str, dest_subfolder: str) -> str:
        """Copy file to new location"""
        source_full_path = self.get_file_path(source_path)
        if not source_full_path.exists():
            raise HTTPException(status_code=404, detail="Source file not found")
        
        # Generate new filename
        original_name = source_full_path.name
        new_filename = self.generate_secure_filename(original_name)
        
        # Create destination path
        dest_folder = self.base_upload_dir / dest_subfolder
        dest_folder.mkdir(exist_ok=True)
        dest_path = dest_folder / new_filename
        
        # Copy file
        shutil.copy2(source_full_path, dest_path)
        
        # Return relative path
        return str(dest_path.relative_to(self.base_upload_dir))
    
    def get_file_info(self, relative_path: str) -> dict:
        """Get file information"""
        full_path = self.get_file_path(relative_path)
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        stat = full_path.stat()
        
        try:
            mime_type = magic.from_file(str(full_path), mime=True)
        except Exception:
            mime_type = "application/octet-stream"
        
        return {
            "size": stat.st_size,
            "mime_type": mime_type,
            "created_at": stat.st_ctime,
            "modified_at": stat.st_mtime,
            "extension": full_path.suffix.lower()
        }
    
    def cleanup_temp_files(self, max_age_hours: int = 24) -> int:
        """Clean up temporary files older than max_age_hours"""
        temp_dir = self.base_upload_dir / "temp"
        if not temp_dir.exists():
            return 0
        
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        cleaned_count = 0
        
        for file_path in temp_dir.iterdir():
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    try:
                        file_path.unlink()
                        cleaned_count += 1
                    except Exception:
                        pass
        
        return cleaned_count
    
    def get_storage_stats(self) -> dict:
        """Get storage statistics"""
        stats = {
            "total_files": 0,
            "total_size": 0,
            "by_subfolder": {}
        }
        
        for subfolder in self.base_upload_dir.iterdir():
            if subfolder.is_dir():
                folder_stats = {"files": 0, "size": 0}
                
                for file_path in subfolder.rglob("*"):
                    if file_path.is_file():
                        folder_stats["files"] += 1
                        folder_stats["size"] += file_path.stat().st_size
                
                stats["by_subfolder"][subfolder.name] = folder_stats
                stats["total_files"] += folder_stats["files"]
                stats["total_size"] += folder_stats["size"]
        
        return stats


# Global instance
file_storage_service = FileStorageService()