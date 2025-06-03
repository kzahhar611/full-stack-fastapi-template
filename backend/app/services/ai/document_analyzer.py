"""
AI Document Analyzer Service
Provides intelligent document classification, content extraction, and analysis
"""
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
import json
import re
from datetime import datetime

from .llm_service import llm_service, LLMMessage

logger = logging.getLogger(__name__)


class DocumentAnalyzer:
    """AI-powered document analysis service"""
    
    def __init__(self):
        self.classification_prompts = {
            "document_type": """Analyze this document and classify it into one of these categories:
            - REQUIREMENT: Requirements documents, specifications, needs analysis
            - SPECIFICATION: Technical specifications, design documents, standards
            - PROPOSAL: Proposals, bids, responses to RFPs
            - CONTRACT: Contracts, agreements, legal documents
            - EVALUATION: Evaluation criteria, scoring sheets, assessments
            - ATTACHMENT: Supporting documents, references, appendices
            
            Return only the category name.""",
            
            "content_analysis": """Analyze this document comprehensively and provide a JSON response with:
            {
                "summary": "Brief summary of the document content",
                "key_points": ["List of main points or requirements"],
                "quality_score": 8.5,
                "complexity": "low|medium|high",
                "completeness": "incomplete|partial|complete",
                "metadata": {
                    "estimated_pages": 5,
                    "sections": 3,
                    "has_tables": true,
                    "has_images": false,
                    "language": "english"
                },
                "suggestions": ["Specific suggestions for improvement"],
                "keywords": ["extracted", "important", "keywords"],
                "compliance_notes": ["Any compliance or regulatory notes"]
            }"""
        }
    
    async def analyze_document(
        self,
        content: str,
        filename: str = None,
        existing_type: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Comprehensive document analysis
        """
        try:
            # Basic content validation
            if not content or len(content.strip()) < 10:
                return self._get_minimal_analysis(filename)
            
            # Prepare content for analysis (truncate if too long)
            analysis_content = self._prepare_content_for_analysis(content)
            
            # Run classification and content analysis in parallel
            classification_task = self._classify_document_type(analysis_content, existing_type)
            content_analysis_task = self._analyze_content(analysis_content)
            
            document_type, content_analysis = await asyncio.gather(
                classification_task,
                content_analysis_task,
                return_exceptions=True
            )
            
            # Handle any exceptions
            if isinstance(document_type, Exception):
                logger.warning(f"Document classification failed: {document_type}")
                document_type = existing_type or "ATTACHMENT"
            
            if isinstance(content_analysis, Exception):
                logger.warning(f"Content analysis failed: {content_analysis}")
                content_analysis = self._get_basic_content_analysis(content)
            
            # Combine results
            result = {
                "document_type": document_type,
                "filename": filename,
                "analysis_timestamp": datetime.now().isoformat(),
                **content_analysis
            }
            
            # Add file-based insights
            if filename:
                result.update(self._analyze_filename(filename))
            
            logger.info(f"Document analysis completed for {filename or 'unnamed document'}")
            return result
            
        except Exception as e:
            logger.error(f"Document analysis failed: {str(e)}")
            return self._get_error_analysis(str(e), filename)
    
    async def _classify_document_type(
        self,
        content: str,
        existing_type: str = None
    ) -> str:
        """Classify document type using AI"""
        
        # If we have existing type and content is short, trust existing
        if existing_type and len(content) < 500:
            return existing_type
        
        messages = [
            LLMMessage(
                role="system",
                content=self.classification_prompts["document_type"]
            ),
            LLMMessage(
                role="user",
                content=f"Document content:\n\n{content[:2000]}"
            )
        ]
        
        response = await llm_service.generate(
            messages=messages,
            temperature=0.1,
            max_tokens=50
        )
        
        # Extract and validate document type
        doc_type = response.content.strip().upper()
        valid_types = ["REQUIREMENT", "SPECIFICATION", "PROPOSAL", "CONTRACT", "EVALUATION", "ATTACHMENT"]
        
        for valid_type in valid_types:
            if valid_type in doc_type:
                return valid_type
        
        return existing_type or "ATTACHMENT"
    
    async def _analyze_content(self, content: str) -> Dict[str, Any]:
        """Analyze document content comprehensively"""
        
        messages = [
            LLMMessage(
                role="system",
                content=self.classification_prompts["content_analysis"]
            ),
            LLMMessage(
                role="user",
                content=f"Analyze this document content:\n\n{content[:3000]}"
            )
        ]
        
        response = await llm_service.generate(
            messages=messages,
            temperature=0.3,
            max_tokens=800
        )
        
        try:
            # Try to parse JSON response
            analysis = json.loads(response.content)
            
            # Validate required fields
            required_fields = ["summary", "key_points", "quality_score"]
            for field in required_fields:
                if field not in analysis:
                    analysis[field] = self._get_default_value(field)
            
            # Ensure quality_score is numeric
            if not isinstance(analysis.get("quality_score"), (int, float)):
                analysis["quality_score"] = 5.0
            
            return analysis
            
        except json.JSONDecodeError:
            # Fallback to structured parsing
            return self._parse_unstructured_analysis(response.content, content)
    
    def _prepare_content_for_analysis(self, content: str) -> str:
        """Prepare content for AI analysis"""
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content.strip())
        
        # Truncate if too long (keep first part for context)
        if len(content) > 4000:
            content = content[:3500] + "\n\n[Document truncated for analysis...]"
        
        return content
    
    def _analyze_filename(self, filename: str) -> Dict[str, Any]:
        """Extract insights from filename"""
        insights = {}
        
        filename_lower = filename.lower()
        
        # File type hints
        if any(word in filename_lower for word in ['req', 'requirement']):
            insights['filename_hints'] = ['requirements']
        elif any(word in filename_lower for word in ['spec', 'specification']):
            insights['filename_hints'] = ['specifications']
        elif any(word in filename_lower for word in ['proposal', 'bid']):
            insights['filename_hints'] = ['proposal']
        elif any(word in filename_lower for word in ['contract', 'agreement']):
            insights['filename_hints'] = ['contract']
        elif any(word in filename_lower for word in ['eval', 'score', 'assessment']):
            insights['filename_hints'] = ['evaluation']
        else:
            insights['filename_hints'] = ['general']
        
        # Extract version if present
        version_match = re.search(r'v(\d+(?:\.\d+)*)', filename_lower)
        if version_match:
            insights['version'] = version_match.group(1)
        
        # Extract date if present
        date_match = re.search(r'(\d{4}[-_]\d{2}[-_]\d{2})', filename)
        if date_match:
            insights['date_in_filename'] = date_match.group(1)
        
        return insights
    
    def _get_basic_content_analysis(self, content: str) -> Dict[str, Any]:
        """Basic content analysis without AI"""
        word_count = len(content.split())
        char_count = len(content)
        
        # Estimate pages (assuming ~250 words per page)
        estimated_pages = max(1, word_count // 250)
        
        # Count sections (looking for headers)
        section_count = len(re.findall(r'\n\s*\d+\.|\n\s*[A-Z][^a-z]*\n', content))
        
        # Look for tables
        has_tables = bool(re.search(r'\|.*\||\t.*\t', content))
        
        # Basic quality assessment
        quality_score = 5.0
        if word_count > 500:
            quality_score += 1
        if section_count > 2:
            quality_score += 1
        if has_tables:
            quality_score += 0.5
        
        return {
            "summary": f"Document with {word_count} words covering {section_count} main sections.",
            "key_points": ["Content analysis", "Basic structure identified"],
            "quality_score": min(10, quality_score),
            "complexity": "medium" if word_count > 1000 else "low",
            "completeness": "partial",
            "metadata": {
                "estimated_pages": estimated_pages,
                "sections": section_count,
                "has_tables": has_tables,
                "has_images": False,
                "word_count": word_count,
                "char_count": char_count
            },
            "suggestions": ["Review for completeness", "Add more detail if needed"],
            "keywords": [],
            "compliance_notes": []
        }
    
    def _parse_unstructured_analysis(self, ai_response: str, content: str) -> Dict[str, Any]:
        """Parse AI response when JSON parsing fails"""
        
        # Get basic analysis as fallback
        basic_analysis = self._get_basic_content_analysis(content)
        
        # Try to extract summary from AI response
        summary_match = re.search(r'summary[:\s]*([^\n]+)', ai_response, re.IGNORECASE)
        if summary_match:
            basic_analysis["summary"] = summary_match.group(1).strip()
        
        # Try to extract quality score
        score_match = re.search(r'quality[_\s]*score[:\s]*(\d+(?:\.\d+)?)', ai_response, re.IGNORECASE)
        if score_match:
            try:
                basic_analysis["quality_score"] = float(score_match.group(1))
            except ValueError:
                pass
        
        return basic_analysis
    
    def _get_minimal_analysis(self, filename: str = None) -> Dict[str, Any]:
        """Return minimal analysis for empty/invalid content"""
        return {
            "document_type": "ATTACHMENT",
            "filename": filename,
            "summary": "Document appears to be empty or unreadable",
            "key_points": [],
            "quality_score": 1.0,
            "complexity": "low",
            "completeness": "incomplete",
            "metadata": {
                "estimated_pages": 0,
                "sections": 0,
                "has_tables": False,
                "has_images": False
            },
            "suggestions": ["Verify document content", "Re-upload if necessary"],
            "keywords": [],
            "compliance_notes": [],
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def _get_error_analysis(self, error: str, filename: str = None) -> Dict[str, Any]:
        """Return error analysis"""
        return {
            "document_type": "ATTACHMENT",
            "filename": filename,
            "summary": f"Analysis failed: {error}",
            "key_points": [],
            "quality_score": 0.0,
            "complexity": "unknown",
            "completeness": "unknown",
            "metadata": {
                "error": error,
                "analysis_failed": True
            },
            "suggestions": ["Manual review required"],
            "keywords": [],
            "compliance_notes": [],
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def _get_default_value(self, field: str) -> Any:
        """Get default value for missing fields"""
        defaults = {
            "summary": "Document content analyzed",
            "key_points": [],
            "quality_score": 5.0,
            "complexity": "medium",
            "completeness": "partial",
            "suggestions": [],
            "keywords": [],
            "compliance_notes": []
        }
        return defaults.get(field, None)
    
    async def find_similar_documents(
        self,
        content: str,
        document_embeddings: List[Tuple[int, List[float]]] = None,
        similarity_threshold: float = 0.8
    ) -> List[Dict[str, Any]]:
        """Find similar documents using embeddings"""
        
        if not document_embeddings:
            return []
        
        try:
            # Generate embedding for current document
            current_embedding = await llm_service.embed(content[:2000])
            
            # Calculate similarities
            similarities = []
            for doc_id, embedding in document_embeddings:
                similarity = self._cosine_similarity(current_embedding, embedding)
                if similarity >= similarity_threshold:
                    similarities.append({
                        "document_id": doc_id,
                        "similarity_score": similarity
                    })
            
            # Sort by similarity
            similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            return similarities[:5]  # Return top 5 similar documents
            
        except Exception as e:
            logger.error(f"Similarity analysis failed: {str(e)}")
            return []
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        import math
        
        if len(a) != len(b):
            return 0.0
        
        dot_product = sum(x * y for x, y in zip(a, b))
        magnitude_a = math.sqrt(sum(x * x for x in a))
        magnitude_b = math.sqrt(sum(x * x for x in b))
        
        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0
        
        return dot_product / (magnitude_a * magnitude_b)


# Global document analyzer instance
document_analyzer = DocumentAnalyzer()