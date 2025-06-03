"""
AI RFP Assistant Service
Provides intelligent RFP analysis, improvement suggestions, and content generation
"""
import logging
import asyncio
from typing import Dict, Any, List, Optional, Union
import json
import re
from datetime import datetime

from .llm_service import llm_service, LLMMessage

logger = logging.getLogger(__name__)


class RFPAssistant:
    """AI-powered RFP assistance service"""
    
    def __init__(self):
        self.analysis_prompts = {
            "rfp_quality": """You are an expert RFP consultant. Analyze the provided RFP content and provide a comprehensive quality assessment.

            Evaluate the RFP based on:
            1. Clarity and completeness of requirements
            2. Structure and organization
            3. Evaluation criteria definition
            4. Timeline and deadlines
            5. Budget and commercial terms
            6. Compliance and legal considerations
            7. Vendor guidance and instructions

            Return a JSON response with:
            {
                "overall_score": 8.5,
                "strengths": ["Clear technical requirements", "Well-defined timeline"],
                "weaknesses": ["Missing evaluation criteria", "Unclear budget range"],
                "detailed_scores": {
                    "clarity": 8,
                    "completeness": 7,
                    "structure": 9,
                    "evaluation_criteria": 5,
                    "timeline": 8,
                    "commercial_terms": 6,
                    "compliance": 7
                },
                "suggestions": [
                    "Add weighted evaluation criteria with scoring methodology",
                    "Include budget range or cost expectations",
                    "Clarify deliverable acceptance criteria"
                ],
                "missing_sections": ["Evaluation methodology", "Risk assessment", "Change management"],
                "improvement_priority": "high|medium|low",
                "estimated_response_effort": "high|medium|low"
            }""",
            
            "content_generation": """You are an expert RFP writer. Generate high-quality RFP content based on the provided requirements.

            Create professional, clear, and comprehensive content that includes:
            - Clear objectives and scope
            - Detailed requirements (functional and non-functional)
            - Evaluation criteria and methodology
            - Timeline and milestones
            - Submission requirements
            - Commercial and legal terms

            Focus on clarity, completeness, and professional tone.""",
            
            "requirements_extraction": """Extract and structure the key requirements from this RFP content.

            Return a JSON response with:
            {
                "functional_requirements": ["List of functional requirements"],
                "non_functional_requirements": ["Performance, security, scalability requirements"],
                "technical_requirements": ["Technology, platform, integration requirements"],
                "compliance_requirements": ["Regulatory, legal, standard requirements"],
                "commercial_requirements": ["Pricing, payment, commercial terms"],
                "timeline_requirements": ["Delivery dates, milestones, deadlines"],
                "vendor_requirements": ["Qualifications, experience, certifications"],
                "submission_requirements": ["Format, deadline, required documents"]
            }""",
            
            "proposal_evaluation": """You are an expert proposal evaluator. Analyze this proposal against the RFP requirements and provide a comprehensive evaluation.

            Evaluate based on:
            - Technical approach and solution quality
            - Team qualifications and experience
            - Timeline feasibility and project plan
            - Cost competitiveness and value
            - Risk assessment and mitigation
            - Compliance with requirements

            Return a JSON response with scores, strengths, weaknesses, and recommendations."""
        }
    
    async def analyze_rfp_quality(
        self,
        rfp_content: str,
        rfp_type: str = "general",
        industry: str = "general",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Comprehensive RFP quality analysis
        """
        try:
            if not rfp_content or len(rfp_content.strip()) < 50:
                return self._get_minimal_rfp_analysis()
            
            # Prepare content for analysis
            analysis_content = self._prepare_rfp_content(rfp_content)
            
            messages = [
                LLMMessage(
                    role="system",
                    content=self.analysis_prompts["rfp_quality"]
                ),
                LLMMessage(
                    role="user",
                    content=f"RFP Type: {rfp_type}\nIndustry: {industry}\n\nRFP Content:\n{analysis_content}"
                )
            ]
            
            response = await llm_service.generate(
                messages=messages,
                temperature=0.3,
                max_tokens=1200
            )
            
            try:
                analysis = json.loads(response.content)
                
                # Validate and enhance analysis
                analysis = self._validate_rfp_analysis(analysis)
                analysis["analysis_timestamp"] = datetime.now().isoformat()
                analysis["rfp_type"] = rfp_type
                analysis["industry"] = industry
                
                return analysis
                
            except json.JSONDecodeError:
                return self._parse_unstructured_rfp_analysis(response.content, rfp_content)
                
        except Exception as e:
            logger.error(f"RFP quality analysis failed: {str(e)}")
            return self._get_error_rfp_analysis(str(e))
    
    async def generate_rfp_content(
        self,
        requirements: Dict[str, Any],
        rfp_type: str = "general",
        industry: str = "general",
        tone: str = "professional",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate RFP content based on requirements
        """
        try:
            # Format requirements for prompt
            requirements_text = self._format_requirements_for_prompt(requirements)
            
            system_prompt = f"{self.analysis_prompts['content_generation']}\n\nRFP Type: {rfp_type}\nIndustry: {industry}\nTone: {tone}"
            
            messages = [
                LLMMessage(role="system", content=system_prompt),
                LLMMessage(
                    role="user",
                    content=f"Generate comprehensive RFP content for:\n\n{requirements_text}"
                )
            ]
            
            response = await llm_service.generate(
                messages=messages,
                temperature=0.4,
                max_tokens=2000
            )
            
            # Structure the generated content
            structured_content = self._structure_generated_content(response.content)
            
            return {
                "generated_content": response.content,
                "structured_sections": structured_content,
                "word_count": len(response.content.split()),
                "generation_timestamp": datetime.now().isoformat(),
                "rfp_type": rfp_type,
                "industry": industry,
                "tone": tone,
                "confidence": response.confidence
            }
            
        except Exception as e:
            logger.error(f"RFP content generation failed: {str(e)}")
            return {
                "error": str(e),
                "generated_content": "",
                "structured_sections": {},
                "generation_timestamp": datetime.now().isoformat()
            }
    
    async def extract_requirements(
        self,
        rfp_content: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Extract and categorize requirements from RFP content
        """
        try:
            if not rfp_content or len(rfp_content.strip()) < 50:
                return self._get_empty_requirements()
            
            analysis_content = self._prepare_rfp_content(rfp_content)
            
            messages = [
                LLMMessage(
                    role="system",
                    content=self.analysis_prompts["requirements_extraction"]
                ),
                LLMMessage(
                    role="user",
                    content=f"Extract requirements from this RFP:\n\n{analysis_content}"
                )
            ]
            
            response = await llm_service.generate(
                messages=messages,
                temperature=0.2,
                max_tokens=1000
            )
            
            try:
                requirements = json.loads(response.content)
                
                # Validate requirements structure
                requirements = self._validate_requirements(requirements)
                requirements["extraction_timestamp"] = datetime.now().isoformat()
                requirements["total_requirements"] = sum(
                    len(req_list) for req_list in requirements.values() 
                    if isinstance(req_list, list)
                )
                
                return requirements
                
            except json.JSONDecodeError:
                return self._parse_unstructured_requirements(response.content)
                
        except Exception as e:
            logger.error(f"Requirements extraction failed: {str(e)}")
            return self._get_error_requirements(str(e))
    
    async def evaluate_proposal(
        self,
        rfp_content: str,
        proposal_content: str,
        evaluation_criteria: Dict[str, float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Evaluate a proposal against RFP requirements
        """
        try:
            if not rfp_content or not proposal_content:
                return self._get_minimal_evaluation()
            
            # Prepare content
            rfp_summary = self._prepare_rfp_content(rfp_content)[:1500]
            proposal_summary = self._prepare_rfp_content(proposal_content)[:1500]
            
            criteria_text = ""
            if evaluation_criteria:
                criteria_text = f"\n\nEvaluation Criteria:\n{json.dumps(evaluation_criteria, indent=2)}"
            
            messages = [
                LLMMessage(
                    role="system",
                    content=self.analysis_prompts["proposal_evaluation"]
                ),
                LLMMessage(
                    role="user",
                    content=f"RFP Requirements:\n{rfp_summary}\n\nProposal to Evaluate:\n{proposal_summary}{criteria_text}"
                )
            ]
            
            response = await llm_service.generate(
                messages=messages,
                temperature=0.3,
                max_tokens=1200
            )
            
            try:
                evaluation = json.loads(response.content)
                
                # Validate evaluation structure
                evaluation = self._validate_evaluation(evaluation)
                evaluation["evaluation_timestamp"] = datetime.now().isoformat()
                
                return evaluation
                
            except json.JSONDecodeError:
                return self._parse_unstructured_evaluation(response.content)
                
        except Exception as e:
            logger.error(f"Proposal evaluation failed: {str(e)}")
            return self._get_error_evaluation(str(e))
    
    async def suggest_improvements(
        self,
        rfp_content: str,
        focus_areas: List[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Suggest specific improvements for RFP content
        """
        try:
            # First analyze quality
            quality_analysis = await self.analyze_rfp_quality(rfp_content, **kwargs)
            
            # Generate targeted suggestions
            focus_text = ""
            if focus_areas:
                focus_text = f"\n\nFocus particularly on: {', '.join(focus_areas)}"
            
            improvement_prompt = f"""Based on the RFP analysis, provide specific, actionable improvement suggestions.

            Current weaknesses identified: {quality_analysis.get('weaknesses', [])}
            Missing sections: {quality_analysis.get('missing_sections', [])}
            
            Provide detailed suggestions with:
            - Specific text additions or modifications
            - Recommended sections to add
            - Structural improvements
            - Best practice recommendations{focus_text}
            
            Return suggestions in order of priority."""
            
            messages = [
                LLMMessage(role="system", content=improvement_prompt),
                LLMMessage(
                    role="user",
                    content=f"RFP Content:\n{self._prepare_rfp_content(rfp_content)}"
                )
            ]
            
            response = await llm_service.generate(
                messages=messages,
                temperature=0.4,
                max_tokens=1000
            )
            
            return {
                "quality_analysis": quality_analysis,
                "improvement_suggestions": response.content,
                "focus_areas": focus_areas or [],
                "suggestion_timestamp": datetime.now().isoformat(),
                "confidence": response.confidence
            }
            
        except Exception as e:
            logger.error(f"Improvement suggestions failed: {str(e)}")
            return {
                "error": str(e),
                "quality_analysis": {},
                "improvement_suggestions": "",
                "suggestion_timestamp": datetime.now().isoformat()
            }
    
    def _prepare_rfp_content(self, content: str) -> str:
        """Prepare RFP content for AI analysis"""
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content.strip())
        
        # Truncate if too long
        if len(content) > 5000:
            content = content[:4500] + "\n\n[Content truncated for analysis...]"
        
        return content
    
    def _validate_rfp_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance RFP analysis"""
        
        # Ensure required fields exist
        required_fields = {
            "overall_score": 5.0,
            "strengths": [],
            "weaknesses": [],
            "suggestions": [],
            "missing_sections": [],
            "improvement_priority": "medium"
        }
        
        for field, default in required_fields.items():
            if field not in analysis:
                analysis[field] = default
        
        # Validate overall_score
        if not isinstance(analysis.get("overall_score"), (int, float)):
            analysis["overall_score"] = 5.0
        else:
            analysis["overall_score"] = max(0, min(10, analysis["overall_score"]))
        
        # Ensure detailed_scores exists
        if "detailed_scores" not in analysis:
            analysis["detailed_scores"] = {
                "clarity": 5,
                "completeness": 5,
                "structure": 5,
                "evaluation_criteria": 5,
                "timeline": 5,
                "commercial_terms": 5,
                "compliance": 5
            }
        
        return analysis
    
    def _format_requirements_for_prompt(self, requirements: Dict[str, Any]) -> str:
        """Format requirements dictionary for AI prompt"""
        formatted = []
        
        for key, value in requirements.items():
            if isinstance(value, str):
                formatted.append(f"{key}: {value}")
            elif isinstance(value, list):
                formatted.append(f"{key}:\n" + "\n".join(f"  - {item}" for item in value))
            elif isinstance(value, dict):
                formatted.append(f"{key}:\n" + "\n".join(f"  {k}: {v}" for k, v in value.items()))
        
        return "\n\n".join(formatted)
    
    def _structure_generated_content(self, content: str) -> Dict[str, str]:
        """Structure generated RFP content into sections"""
        sections = {}
        
        # Common RFP section patterns
        section_patterns = [
            (r'(?i)(executive summary|overview)', 'executive_summary'),
            (r'(?i)(scope|project scope)', 'scope'),
            (r'(?i)(requirements|functional requirements)', 'requirements'),
            (r'(?i)(evaluation criteria|scoring)', 'evaluation_criteria'),
            (r'(?i)(timeline|schedule|milestones)', 'timeline'),
            (r'(?i)(submission|proposal submission)', 'submission_requirements'),
            (r'(?i)(commercial|pricing|cost)', 'commercial_terms'),
            (r'(?i)(legal|terms and conditions)', 'legal_terms')
        ]
        
        current_section = 'introduction'
        current_content = []
        
        lines = content.split('\n')
        
        for line in lines:
            # Check if line is a section header
            section_found = False
            for pattern, section_name in section_patterns:
                if re.search(pattern, line) and len(line.strip()) < 100:
                    # Save current section
                    if current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                    
                    # Start new section
                    current_section = section_name
                    current_content = []
                    section_found = True
                    break
            
            if not section_found:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def _get_minimal_rfp_analysis(self) -> Dict[str, Any]:
        """Return minimal analysis for empty RFP"""
        return {
            "overall_score": 1.0,
            "strengths": [],
            "weaknesses": ["No content provided"],
            "detailed_scores": {
                "clarity": 1, "completeness": 1, "structure": 1,
                "evaluation_criteria": 1, "timeline": 1,
                "commercial_terms": 1, "compliance": 1
            },
            "suggestions": ["Add RFP content for analysis"],
            "missing_sections": ["All sections"],
            "improvement_priority": "high",
            "estimated_response_effort": "unknown",
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def _get_error_rfp_analysis(self, error: str) -> Dict[str, Any]:
        """Return error analysis"""
        return {
            "error": error,
            "overall_score": 0.0,
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def _get_empty_requirements(self) -> Dict[str, Any]:
        """Return empty requirements structure"""
        return {
            "functional_requirements": [],
            "non_functional_requirements": [],
            "technical_requirements": [],
            "compliance_requirements": [],
            "commercial_requirements": [],
            "timeline_requirements": [],
            "vendor_requirements": [],
            "submission_requirements": [],
            "total_requirements": 0,
            "extraction_timestamp": datetime.now().isoformat()
        }
    
    def _parse_unstructured_rfp_analysis(self, content: str, rfp_content: str) -> Dict[str, Any]:
        """Parse unstructured AI response for RFP analysis"""
        analysis = self._get_minimal_rfp_analysis()
        
        # Try to extract score
        score_match = re.search(r'score[:\s]*(\d+(?:\.\d+)?)', content, re.IGNORECASE)
        if score_match:
            try:
                analysis["overall_score"] = float(score_match.group(1))
            except ValueError:
                pass
        
        # Extract suggestions
        suggestions = re.findall(r'-\s*([^-\n]+)', content)
        if suggestions:
            analysis["suggestions"] = [s.strip() for s in suggestions[:5]]
        
        return analysis
    
    def _validate_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Validate requirements structure"""
        required_categories = [
            "functional_requirements", "non_functional_requirements",
            "technical_requirements", "compliance_requirements",
            "commercial_requirements", "timeline_requirements",
            "vendor_requirements", "submission_requirements"
        ]
        
        for category in required_categories:
            if category not in requirements:
                requirements[category] = []
            elif not isinstance(requirements[category], list):
                requirements[category] = []
        
        return requirements
    
    def _validate_evaluation(self, evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """Validate evaluation structure"""
        required_fields = {
            "overall_score": 5.0,
            "technical_score": 5.0,
            "commercial_score": 5.0,
            "team_score": 5.0,
            "timeline_score": 5.0,
            "strengths": [],
            "weaknesses": [],
            "recommendations": [],
            "compliance_status": "partial"
        }
        
        for field, default in required_fields.items():
            if field not in evaluation:
                evaluation[field] = default
        
        return evaluation
    
    def _get_minimal_evaluation(self) -> Dict[str, Any]:
        """Return minimal evaluation"""
        return {
            "overall_score": 0.0,
            "technical_score": 0.0,
            "commercial_score": 0.0,
            "team_score": 0.0,
            "timeline_score": 0.0,
            "strengths": [],
            "weaknesses": ["Insufficient content for evaluation"],
            "recommendations": ["Provide complete proposal content"],
            "compliance_status": "unknown",
            "evaluation_timestamp": datetime.now().isoformat()
        }
    
    def _parse_unstructured_requirements(self, content: str) -> Dict[str, Any]:
        """Parse unstructured requirements"""
        requirements = self._get_empty_requirements()
        
        # Simple extraction based on patterns
        lines = content.split('\n')
        current_category = "functional_requirements"
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('{') and not line.startswith('}'):
                if any(word in line.lower() for word in ['functional', 'feature']):
                    current_category = "functional_requirements"
                elif any(word in line.lower() for word in ['technical', 'technology']):
                    current_category = "technical_requirements"
                elif any(word in line.lower() for word in ['compliance', 'regulation']):
                    current_category = "compliance_requirements"
                elif line.startswith('-') or line.startswith('•'):
                    requirements[current_category].append(line[1:].strip())
        
        return requirements
    
    def _get_error_requirements(self, error: str) -> Dict[str, Any]:
        """Return error requirements"""
        return {
            "error": error,
            **self._get_empty_requirements()
        }
    
    def _parse_unstructured_evaluation(self, content: str) -> Dict[str, Any]:
        """Parse unstructured evaluation"""
        return self._get_minimal_evaluation()
    
    def _get_error_evaluation(self, error: str) -> Dict[str, Any]:
        """Return error evaluation"""
        return {
            "error": error,
            **self._get_minimal_evaluation()
        }


# Global RFP assistant instance
rfp_assistant = RFPAssistant()