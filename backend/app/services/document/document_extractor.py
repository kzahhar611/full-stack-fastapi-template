"""
Document Text Extraction Service
Handles various document formats for RFP content extraction
"""
import logging
import io
import re
from typing import Optional, Union
import tempfile
import os

logger = logging.getLogger(__name__)


class DocumentExtractor:
    """Document text extraction service"""
    
    def __init__(self):
        self.supported_extensions = {
            '.pdf': self._extract_from_pdf,
            '.docx': self._extract_from_docx,
            '.doc': self._extract_from_doc,
            '.txt': self._extract_from_txt,
            '.rtf': self._extract_from_rtf
        }
    
    async def extract_text(self, file_content: bytes, filename: str) -> str:
        """
        Extract text from document based on file extension
        
        Args:
            file_content: Binary content of the file
            filename: Original filename with extension
            
        Returns:
            Extracted text content
        """
        try:
            # Get file extension
            ext = os.path.splitext(filename.lower())[1]
            
            if ext not in self.supported_extensions:
                # Try to detect content type from content
                ext = self._detect_file_type(file_content)
            
            if ext not in self.supported_extensions:
                # Fallback - try to decode as text
                try:
                    return file_content.decode('utf-8', errors='ignore')
                except:
                    raise ValueError(f"Unsupported file format: {ext}")
            
            # Extract text using appropriate method
            extractor = self.supported_extensions[ext]
            text = await extractor(file_content)
            
            # Clean and validate text
            cleaned_text = self._clean_text(text)
            
            if len(cleaned_text.strip()) < 50:
                raise ValueError("Insufficient text content extracted from document")
            
            logger.info(f"Successfully extracted {len(cleaned_text)} characters from {filename}")
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Error extracting text from {filename}: {str(e)}")
            raise
    
    def _detect_file_type(self, content: bytes) -> str:
        """Detect file type from content"""
        # PDF signature
        if content.startswith(b'%PDF'):
            return '.pdf'
        
        # DOCX signature (ZIP format)
        if content.startswith(b'PK\x03\x04'):
            # Check for docx content
            if b'word/' in content[:1000]:
                return '.docx'
        
        # DOC signature
        if content.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'):
            return '.doc'
        
        # RTF signature
        if content.startswith(b'{\\rtf'):
            return '.rtf'
        
        # Default to text
        return '.txt'
    
    async def _extract_from_pdf(self, content: bytes) -> str:
        """Extract text from PDF"""
        try:
            import PyPDF2
            
            pdf_file = io.BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text
            
        except ImportError:
            # Fallback using pypdf (newer library)
            try:
                import pypdf
                
                pdf_file = io.BytesIO(content)
                pdf_reader = pypdf.PdfReader(pdf_file)
                
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                return text
                
            except ImportError:
                # Final fallback - basic PDF text extraction
                return self._basic_pdf_extraction(content)
    
    async def _extract_from_docx(self, content: bytes) -> str:
        """Extract text from DOCX"""
        try:
            import docx
            
            doc_file = io.BytesIO(content)
            doc = docx.Document(doc_file)
            
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            # Also extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        text += cell.text + " "
                    text += "\n"
            
            return text
            
        except ImportError:
            # Fallback using python-docx
            try:
                from docx import Document
                
                doc_file = io.BytesIO(content)
                doc = Document(doc_file)
                
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                
                return text
                
            except ImportError:
                raise ValueError("python-docx library not available for DOCX extraction")
    
    async def _extract_from_doc(self, content: bytes) -> str:
        """Extract text from DOC (legacy Word format)"""
        try:
            import textract
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.doc', delete=False) as tmp_file:
                tmp_file.write(content)
                tmp_file.flush()
                
                try:
                    text = textract.process(tmp_file.name).decode('utf-8')
                    return text
                finally:
                    os.unlink(tmp_file.name)
                    
        except ImportError:
            # Fallback - try basic text extraction
            return self._basic_text_extraction(content)
    
    async def _extract_from_txt(self, content: bytes) -> str:
        """Extract text from plain text file"""
        try:
            # Try UTF-8 first
            return content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                # Try Latin-1
                return content.decode('latin-1')
            except UnicodeDecodeError:
                # Try Windows-1252
                return content.decode('windows-1252', errors='ignore')
    
    async def _extract_from_rtf(self, content: bytes) -> str:
        """Extract text from RTF"""
        try:
            from striprtf.striprtf import rtf_to_text
            
            rtf_string = content.decode('utf-8', errors='ignore')
            return rtf_to_text(rtf_string)
            
        except ImportError:
            # Basic RTF text extraction
            return self._basic_rtf_extraction(content)
    
    def _basic_pdf_extraction(self, content: bytes) -> str:
        """Basic PDF text extraction without libraries"""
        try:
            # Very basic PDF text extraction
            text = content.decode('latin-1', errors='ignore')
            
            # Remove PDF header/footer noise
            lines = text.split('\n')
            clean_lines = []
            
            for line in lines:
                # Skip lines that look like PDF commands
                if not any(cmd in line for cmd in ['obj', 'endobj', 'stream', 'endstream', '<<', '>>']):
                    # Extract readable text
                    readable = re.sub(r'[^\x20-\x7E\n]', ' ', line)
                    if len(readable.strip()) > 2:
                        clean_lines.append(readable.strip())
            
            return '\n'.join(clean_lines)
            
        except:
            raise ValueError("Unable to extract text from PDF without required libraries")
    
    def _basic_text_extraction(self, content: bytes) -> str:
        """Basic text extraction for unsupported formats"""
        try:
            # Try to decode as text with error handling
            text = content.decode('utf-8', errors='ignore')
            return self._clean_text(text)
        except:
            # Last resort - extract any printable characters
            printable_chars = ''.join(chr(b) for b in content if 32 <= b <= 126 or b in [9, 10, 13])
            return self._clean_text(printable_chars)
    
    def _basic_rtf_extraction(self, content: bytes) -> str:
        """Basic RTF text extraction"""
        try:
            rtf_text = content.decode('utf-8', errors='ignore')
            
            # Remove RTF control words and groups
            text = re.sub(r'\\[a-z]+\d*', '', rtf_text)  # Remove control words
            text = re.sub(r'[{}]', '', text)  # Remove braces
            text = re.sub(r'\\[^a-z]', '', text)  # Remove other control sequences
            
            return self._clean_text(text)
            
        except:
            return self._basic_text_extraction(content)
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove excessive newlines
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        
        # Remove non-printable characters except newlines and tabs
        text = re.sub(r'[^\x20-\x7E\n\t]', ' ', text)
        
        # Clean up multiple spaces
        text = re.sub(r' +', ' ', text)
        
        # Remove leading/trailing whitespace from lines
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(line for line in lines if line)
        
        return text.strip()


# Global instance
document_extractor = DocumentExtractor()