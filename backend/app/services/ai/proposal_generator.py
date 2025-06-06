"""
AI-Powered Proposal Generation Service
Module 3: Technical Proposal Generation for TenderWise AI Platform
"""

import logging
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import uuid

from ..ai.llm_service import LLMService, LLMProvider
from ...schemas.proposal_generation import (
    RequirementType, ContentType, GenerationStatus,
    RFPRequirementAnalysisCreate, GeneratedSectionCreate
)

logger = logging.getLogger(__name__)

class ProposalGeneratorService:
    """AI service for generating technical proposals"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.requirement_patterns = self._load_requirement_patterns()
        self.content_prompts = self._load_content_generation_prompts()
        
    def _load_requirement_patterns(self) -> Dict[RequirementType, List[str]]:
        """Load patterns for identifying different types of requirements"""
        return {
            RequirementType.TECHNICAL: [
                r"technical.*(?:requirement|specification|standard)",
                r"system.*(?:requirement|architecture|design)",
                r"(?:hardware|software|infrastructure).*requirement",
                r"technology.*(?:stack|platform|framework)",
                r"security.*(?:requirement|standard|protocol)",
                r"performance.*(?:requirement|criteria|benchmark)",
                r"integration.*(?:requirement|specification)",
                r"platform.*(?:requirement|compatibility)",
                r"database.*(?:requirement|specification)",
                r"api.*(?:requirement|specification|standard)"
            ],
            RequirementType.FUNCTIONAL: [
                r"functional.*requirement",
                r"business.*(?:requirement|rule|logic)",
                r"user.*(?:requirement|story|need)",
                r"feature.*(?:requirement|specification)",
                r"capability.*(?:requirement|need)",
                r"process.*(?:requirement|flow|workflow)",
                r"data.*(?:requirement|processing|management)",
                r"reporting.*(?:requirement|capability)",
                r"interface.*(?:requirement|specification)",
                r"workflow.*(?:requirement|process)"
            ],
            RequirementType.COMMERCIAL: [
                r"commercial.*(?:requirement|term|condition)",
                r"pricing.*(?:requirement|model|structure)",
                r"contract.*(?:requirement|term|condition)",
                r"payment.*(?:requirement|term|schedule)",
                r"licensing.*(?:requirement|term|fee)",
                r"cost.*(?:requirement|constraint|limit)",
                r"budget.*(?:requirement|constraint|allocation)",
                r"financial.*(?:requirement|term|condition)",
                r"warranty.*(?:requirement|term|period)",
                r"maintenance.*(?:requirement|agreement|cost)"
            ],
            RequirementType.COMPLIANCE: [
                r"compliance.*(?:requirement|standard|regulation)",
                r"regulatory.*(?:requirement|standard|compliance)",
                r"legal.*(?:requirement|compliance|obligation)",
                r"audit.*(?:requirement|standard|compliance)",
                r"certification.*(?:requirement|standard)",
                r"standards?.*(?:compliance|adherence)",
                r"policy.*(?:requirement|compliance|adherence)",
                r"governance.*(?:requirement|framework|policy)",
                r"risk.*(?:management|assessment|mitigation)",
                r"quality.*(?:standard|assurance|control)"
            ],
            RequirementType.MANAGEMENT: [
                r"project.*(?:management|requirement|methodology)",
                r"delivery.*(?:management|requirement|methodology)",
                r"team.*(?:requirement|structure|qualification)",
                r"communication.*(?:requirement|protocol|plan)",
                r"reporting.*(?:requirement|schedule|format)",
                r"milestone.*(?:requirement|schedule|deliverable)",
                r"resource.*(?:requirement|allocation|management)",
                r"schedule.*(?:requirement|constraint|timeline)",
                r"quality.*(?:management|assurance|control)",
                r"change.*(?:management|control|process)"
            ],
            RequirementType.DELIVERY: [
                r"delivery.*(?:requirement|schedule|timeline)",
                r"implementation.*(?:requirement|schedule|plan)",
                r"deployment.*(?:requirement|schedule|plan)",
                r"installation.*(?:requirement|schedule|process)",
                r"transition.*(?:requirement|plan|schedule)",
                r"training.*(?:requirement|schedule|plan)",
                r"support.*(?:requirement|level|schedule)",
                r"maintenance.*(?:requirement|schedule|plan)",
                r"documentation.*(?:requirement|deliverable|standard)",
                r"acceptance.*(?:requirement|criteria|testing)"
            ]
        }
    
    def _load_content_generation_prompts(self) -> Dict[ContentType, Dict[str, str]]:
        """Load prompts for generating different types of content"""
        return {
            ContentType.EXECUTIVE_SUMMARY: {
                "system": "You are an expert proposal writer specializing in executive summaries. Create compelling, concise summaries that highlight key value propositions and competitive advantages.",
                "template": """Create an executive summary for a proposal responding to the following RFP requirements:

Requirements to Address:
{requirements}

Client Information:
- Client: {client_name}
- Project: {project_name}
- Opportunity Value: {opportunity_value}

Company Information:
- Our strengths: {company_strengths}
- Relevant experience: {relevant_experience}
- Unique differentiators: {differentiators}

Generate a professional executive summary that:
1. Demonstrates understanding of client needs
2. Highlights our unique value proposition
3. Summarizes our approach and benefits
4. Creates compelling case for selection
5. Maintains executive-level focus (500-800 words)"""
            },
            ContentType.TECHNICAL_APPROACH: {
                "system": "You are a technical architect and proposal expert. Create detailed technical approaches that demonstrate deep understanding and innovative solutions.",
                "template": """Create a technical approach section responding to these RFP requirements:

Technical Requirements:
{technical_requirements}

Project Context:
- Project: {project_name}
- Client: {client_name}
- Industry: {industry}
- Technology Focus: {technology_focus}

Our Technical Capabilities:
- Core technologies: {core_technologies}
- Methodologies: {methodologies}
- Tools and platforms: {tools_platforms}

Generate a comprehensive technical approach that:
1. Demonstrates understanding of technical requirements
2. Presents innovative and practical solutions
3. Shows methodology and implementation approach
4. Addresses technical risks and mitigation strategies
5. Highlights technical differentiators and expertise
6. Maintains professional technical depth (1000-1500 words)"""
            },
            ContentType.METHODOLOGY: {
                "system": "You are a project methodology expert. Create detailed methodology sections that demonstrate proven approaches and best practices.",
                "template": """Create a methodology section for this proposal:

Project Requirements:
{requirements}

Project Details:
- Project: {project_name}
- Duration: {project_duration}
- Complexity: {complexity_level}
- Delivery Model: {delivery_model}

Our Methodological Approach:
- Primary methodology: {primary_methodology}
- Quality frameworks: {quality_frameworks}
- Risk management approach: {risk_approach}

Generate a detailed methodology section that:
1. Outlines our systematic approach
2. Describes phases and key activities
3. Shows quality assurance processes
4. Addresses risk management
5. Demonstrates proven track record
6. Aligns with client expectations (800-1200 words)"""
            },
            ContentType.TEAM_QUALIFICATIONS: {
                "system": "You are an HR and staffing expert for technical projects. Create compelling team qualification sections that highlight relevant experience and expertise.",
                "template": """Create a team qualifications section for this proposal:

Project Requirements:
{requirements}

Required Skills/Roles:
{required_skills}

Our Team Structure:
- Project Manager: {pm_profile}
- Technical Lead: {tech_lead_profile}
- Key Team Members: {team_members}
- Support Resources: {support_resources}

Team Highlights:
- Combined experience: {combined_experience}
- Relevant certifications: {certifications}
- Past project successes: {past_successes}

Generate a compelling team qualifications section that:
1. Demonstrates team expertise alignment with requirements
2. Highlights relevant experience and achievements
3. Shows clear roles and responsibilities
4. Includes key certifications and credentials
5. Provides evidence of past performance
6. Builds confidence in team capability (800-1200 words)"""
            },
            ContentType.PROJECT_TIMELINE: {
                "system": "You are a project planning expert. Create detailed, realistic project timelines that demonstrate thorough planning and understanding.",
                "template": """Create a project timeline section for this proposal:

Project Requirements:
{requirements}

Project Constraints:
- Duration: {project_duration}
- Key Milestones: {key_milestones}
- Critical Dependencies: {dependencies}
- Resource Availability: {resource_constraints}

Our Planning Approach:
- Methodology: {methodology}
- Phase Structure: {phase_structure}
- Risk Buffers: {risk_buffers}

Generate a detailed project timeline that:
1. Shows realistic and achievable schedule
2. Identifies key phases and milestones
3. Addresses dependencies and constraints
4. Includes risk mitigation time buffers
5. Demonstrates thorough planning
6. Aligns with client expectations (600-1000 words)"""
            },
            ContentType.RISK_MANAGEMENT: {
                "system": "You are a risk management expert for technical projects. Create comprehensive risk management sections that demonstrate proactive risk planning.",
                "template": """Create a risk management section for this proposal:

Project Requirements:
{requirements}

Project Context:
- Project complexity: {complexity_level}
- Technology risks: {technology_risks}
- Timeline constraints: {timeline_constraints}
- Resource constraints: {resource_constraints}

Our Risk Management Approach:
- Risk framework: {risk_framework}
- Mitigation strategies: {mitigation_strategies}
- Contingency planning: {contingency_plans}

Generate a comprehensive risk management section that:
1. Identifies potential project risks
2. Categorizes risks by impact and probability
3. Provides specific mitigation strategies
4. Shows contingency planning
5. Demonstrates proactive risk management
6. Builds client confidence (700-1000 words)"""
            },
            ContentType.QUALITY_ASSURANCE: {
                "system": "You are a quality assurance expert. Create detailed QA sections that demonstrate commitment to quality and proven QA processes.",
                "template": """Create a quality assurance section for this proposal:

Project Requirements:
{requirements}

Quality Requirements:
{quality_requirements}

Our QA Approach:
- QA methodology: {qa_methodology}
- Testing strategies: {testing_strategies}
- Quality metrics: {quality_metrics}
- Review processes: {review_processes}

Generate a comprehensive quality assurance section that:
1. Outlines our systematic QA approach
2. Describes testing and validation processes
3. Shows quality metrics and measurement
4. Addresses continuous improvement
5. Demonstrates quality commitment
6. Aligns with industry standards (600-900 words)"""
            },
            ContentType.DELIVERABLES: {
                "system": "You are a project deliverables expert. Create clear, comprehensive deliverables sections that set proper expectations.",
                "template": """Create a deliverables section for this proposal:

Project Requirements:
{requirements}

Expected Deliverables:
{expected_deliverables}

Our Delivery Approach:
- Delivery methodology: {delivery_methodology}
- Quality standards: {quality_standards}
- Documentation standards: {documentation_standards}

Generate a detailed deliverables section that:
1. Lists all project deliverables clearly
2. Describes deliverable specifications
3. Shows delivery schedule and milestones
4. Outlines quality and acceptance criteria
5. Addresses documentation and handover
6. Sets clear expectations (600-1000 words)"""
            }
        }
    
    async def analyze_rfp_requirements(
        self, 
        rfp_content: str, 
        project_context: Dict[str, Any]
    ) -> List[RFPRequirementAnalysisCreate]:
        """Extract and analyze requirements from RFP content"""
        
        logger.info(f"Starting RFP analysis for project: {project_context.get('project_name', 'Unknown')}")
        
        try:
            # Create analysis prompt
            analysis_prompt = f"""
            Analyze the following RFP document and extract all requirements. For each requirement:

            1. Identify the requirement text
            2. Classify the requirement type (technical, functional, commercial, compliance, management, delivery)
            3. Determine priority level (High, Medium, Low)
            4. Assess complexity (1-10 scale)
            5. Estimate response word count needed
            6. Extract key terms and concepts
            7. Rate clarity and measurability (1-10 scale)

            RFP Content:
            {rfp_content[:10000]}  # Limit content for API efficiency

            Respond with a JSON array of requirements in this format:
            [
                {{
                    "requirement_text": "specific requirement text",
                    "requirement_type": "technical|functional|commercial|compliance|management|delivery",
                    "section_title": "section name from RFP",
                    "page_number": number or null,
                    "priority_level": "High|Medium|Low",
                    "complexity_score": 1-10,
                    "word_count_estimate": estimated_words,
                    "keywords": ["key", "terms"],
                    "clarity_score": 1-10,
                    "measurability_score": 1-10,
                    "extraction_confidence": 0-100
                }}
            ]
            """
            
            # Get AI analysis
            response = await self.llm_service.generate_content(
                prompt=analysis_prompt,
                provider=LLMProvider.OPENAI,
                model="gpt-4",
                temperature=0.1,
                max_tokens=4000
            )
            
            # Parse JSON response
            try:
                requirements_data = json.loads(response)
            except json.JSONDecodeError:
                # Fallback: extract JSON from response if wrapped in text
                json_match = re.search(r'\[.*\]', response, re.DOTALL)
                if json_match:
                    requirements_data = json.loads(json_match.group())
                else:
                    raise ValueError("Could not parse requirements JSON from AI response")
            
            # Convert to Pydantic models
            requirements = []
            for req_data in requirements_data:
                # Map content type based on requirement type
                content_type = self._map_requirement_to_content_type(
                    req_data.get('requirement_type', 'technical')
                )
                
                requirement = RFPRequirementAnalysisCreate(
                    project_id=project_context['project_id'],
                    requirement_text=req_data['requirement_text'],
                    requirement_type=RequirementType(req_data['requirement_type']),
                    section_title=req_data.get('section_title'),
                    page_number=req_data.get('page_number'),
                    priority_level=req_data.get('priority_level', 'Medium'),
                    complexity_score=req_data.get('complexity_score', 5),
                    word_count_estimate=req_data.get('word_count_estimate', 200),
                    assigned_content_type=content_type,
                    estimated_effort_hours=self._estimate_effort_hours(
                        req_data.get('complexity_score', 5),
                        req_data.get('word_count_estimate', 200)
                    ),
                    extraction_confidence=req_data.get('extraction_confidence', 85),
                    keywords=req_data.get('keywords', []),
                    related_requirements=[],  # Will be populated in post-processing
                )
                requirements.append(requirement)
            
            logger.info(f"Extracted {len(requirements)} requirements from RFP")
            return requirements
            
        except Exception as e:
            logger.error(f"Error analyzing RFP requirements: {e}")
            # Return basic fallback requirements
            return self._create_fallback_requirements(project_context['project_id'])
    
    async def generate_content_section(
        self,
        requirement: Dict[str, Any],
        content_type: ContentType,
        template_content: Optional[str] = None,
        generation_context: Dict[str, Any] = None
    ) -> GeneratedSectionCreate:
        """Generate content for a specific proposal section"""
        
        logger.info(f"Generating {content_type} content for requirement: {requirement.get('id')}")
        
        try:
            # Get content generation prompt
            prompt_config = self.content_prompts.get(content_type)
            if not prompt_config:
                raise ValueError(f"No prompt configuration for content type: {content_type}")
            
            # Prepare context variables
            context = generation_context or {}
            context.update({
                'requirements': requirement.get('requirement_text', ''),
                'project_name': context.get('project_name', 'Project'),
                'client_name': context.get('client_name', 'Client'),
            })
            
            # Format the generation prompt
            formatted_prompt = prompt_config['template'].format(**context)
            
            # Generate content using AI
            generated_content = await self.llm_service.generate_content(
                prompt=formatted_prompt,
                system_prompt=prompt_config['system'],
                provider=LLMProvider.OPENAI,
                model="gpt-4",
                temperature=0.3,
                max_tokens=2000
            )
            
            # Calculate metrics
            word_count = len(generated_content.split())
            reading_time = max(1, word_count // 200)  # ~200 words per minute
            
            # Assess content quality
            quality_scores = await self._assess_content_quality(
                generated_content, 
                requirement.get('requirement_text', ''),
                content_type
            )
            
            # Create generated section
            section = GeneratedSectionCreate(
                project_id=context.get('project_id'),
                requirement_id=requirement.get('id'),
                template_id=context.get('template_id'),
                section_title=f"{content_type.value.replace('_', ' ').title()}",
                content_type=content_type,
                section_order=self._get_section_order(content_type),
                generated_content=generated_content,
                original_prompt=formatted_prompt,
                ai_provider="openai"
            )
            
            logger.info(f"Generated {word_count} words for {content_type} section")
            return section
            
        except Exception as e:
            logger.error(f"Error generating content section: {e}")
            # Return fallback content
            return self._create_fallback_section(requirement, content_type, generation_context)
    
    async def assess_proposal_quality(
        self,
        proposal_content: str,
        requirements: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Assess overall proposal quality"""
        
        try:
            assessment_prompt = f"""
            Assess the quality of this proposal content against the given requirements.
            
            Requirements:
            {json.dumps([req.get('requirement_text', '') for req in requirements[:10]], indent=2)}
            
            Proposal Content:
            {proposal_content[:5000]}  # Limit for API efficiency
            
            Rate the proposal on these criteria (0-100 scale):
            1. Content Quality - writing quality, clarity, professionalism
            2. Completeness - how well it addresses all requirements
            3. Consistency - consistent tone, style, and messaging
            4. Relevance - how relevant content is to requirements
            
            Respond with JSON:
            {{
                "content_quality_score": 0-100,
                "completeness_score": 0-100,
                "consistency_score": 0-100,
                "relevance_score": 0-100,
                "overall_score": 0-100,
                "assessment_notes": "brief explanation"
            }}
            """
            
            response = await self.llm_service.generate_content(
                prompt=assessment_prompt,
                provider=LLMProvider.OPENAI,
                model="gpt-4",
                temperature=0.1,
                max_tokens=500
            )
            
            # Parse quality assessment
            try:
                quality_data = json.loads(response)
                return {
                    'content_quality_score': quality_data.get('content_quality_score', 75),
                    'completeness_score': quality_data.get('completeness_score', 75),
                    'consistency_score': quality_data.get('consistency_score', 75),
                    'relevance_score': quality_data.get('relevance_score', 75),
                    'overall_score': quality_data.get('overall_score', 75)
                }
            except json.JSONDecodeError:
                # Fallback scores
                return {
                    'content_quality_score': 75,
                    'completeness_score': 75,
                    'consistency_score': 75,
                    'relevance_score': 75,
                    'overall_score': 75
                }
                
        except Exception as e:
            logger.error(f"Error assessing proposal quality: {e}")
            return {
                'content_quality_score': 70,
                'completeness_score': 70,
                'consistency_score': 70,
                'relevance_score': 70,
                'overall_score': 70
            }
    
    def _map_requirement_to_content_type(self, requirement_type: str) -> ContentType:
        """Map requirement type to appropriate content type"""
        mapping = {
            'technical': ContentType.TECHNICAL_APPROACH,
            'functional': ContentType.METHODOLOGY,
            'commercial': ContentType.PRICING,
            'compliance': ContentType.QUALITY_ASSURANCE,
            'management': ContentType.PROJECT_TIMELINE,
            'delivery': ContentType.DELIVERABLES
        }
        return mapping.get(requirement_type, ContentType.TECHNICAL_APPROACH)
    
    def _estimate_effort_hours(self, complexity_score: int, word_count: int) -> int:
        """Estimate effort hours based on complexity and word count"""
        base_hours = word_count // 100  # ~100 words per hour
        complexity_multiplier = 1 + (complexity_score - 5) * 0.2
        return max(1, int(base_hours * complexity_multiplier))
    
    def _get_section_order(self, content_type: ContentType) -> int:
        """Get standard ordering for content sections"""
        order_map = {
            ContentType.EXECUTIVE_SUMMARY: 1,
            ContentType.TECHNICAL_APPROACH: 2,
            ContentType.METHODOLOGY: 3,
            ContentType.TEAM_QUALIFICATIONS: 4,
            ContentType.PROJECT_TIMELINE: 5,
            ContentType.RISK_MANAGEMENT: 6,
            ContentType.QUALITY_ASSURANCE: 7,
            ContentType.DELIVERABLES: 8,
            ContentType.PRICING: 9,
            ContentType.APPENDIX: 10
        }
        return order_map.get(content_type, 5)
    
    async def _assess_content_quality(
        self,
        content: str,
        requirement: str,
        content_type: ContentType
    ) -> Dict[str, int]:
        """Assess quality of generated content"""
        # Simplified quality assessment
        # In production, this would use more sophisticated AI analysis
        
        word_count = len(content.split())
        
        # Basic quality heuristics
        ai_confidence = 85 if word_count > 200 else 70
        content_quality = 80 if word_count > 300 else 75
        relevance = 85 if requirement.lower() in content.lower() else 70
        completeness = 80 if word_count > 400 else 70
        
        return {
            'ai_confidence_score': ai_confidence,
            'content_quality_score': content_quality,
            'relevance_score': relevance,
            'completeness_score': completeness
        }
    
    def _create_fallback_requirements(self, project_id: int) -> List[RFPRequirementAnalysisCreate]:
        """Create basic fallback requirements if AI analysis fails"""
        return [
            RFPRequirementAnalysisCreate(
                project_id=project_id,
                requirement_text="Technical solution architecture and implementation approach",
                requirement_type=RequirementType.TECHNICAL,
                section_title="Technical Requirements",
                priority_level="High",
                complexity_score=7,
                word_count_estimate=800,
                assigned_content_type=ContentType.TECHNICAL_APPROACH,
                estimated_effort_hours=8,
                extraction_confidence=70,
                keywords=["technical", "architecture", "implementation"]
            ),
            RFPRequirementAnalysisCreate(
                project_id=project_id,
                requirement_text="Project management methodology and delivery approach",
                requirement_type=RequirementType.MANAGEMENT,
                section_title="Management Requirements",
                priority_level="High",
                complexity_score=6,
                word_count_estimate=600,
                assigned_content_type=ContentType.METHODOLOGY,
                estimated_effort_hours=6,
                extraction_confidence=70,
                keywords=["project", "management", "methodology"]
            )
        ]
    
    def _create_fallback_section(
        self,
        requirement: Dict[str, Any],
        content_type: ContentType,
        context: Dict[str, Any] = None
    ) -> GeneratedSectionCreate:
        """Create fallback content section if generation fails"""
        
        fallback_content = {
            ContentType.EXECUTIVE_SUMMARY: "We are pleased to submit our proposal for this important project. Our team brings extensive experience and proven methodologies to deliver exceptional results that meet your requirements and exceed expectations.",
            ContentType.TECHNICAL_APPROACH: "Our technical approach leverages industry best practices and proven technologies to deliver a robust, scalable solution that meets all specified requirements while ensuring optimal performance and maintainability.",
            ContentType.METHODOLOGY: "We employ a systematic, proven methodology that ensures successful project delivery through careful planning, risk management, and quality assurance processes aligned with industry standards.",
        }
        
        content = fallback_content.get(
            content_type,
            f"This section addresses the {content_type.value.replace('_', ' ')} requirements as specified in the RFP."
        )
        
        return GeneratedSectionCreate(
            project_id=context.get('project_id') if context else requirement.get('project_id'),
            requirement_id=requirement.get('id'),
            section_title=f"{content_type.value.replace('_', ' ').title()}",
            content_type=content_type,
            section_order=self._get_section_order(content_type),
            generated_content=content,
            original_prompt="Fallback content generation",
            ai_provider="fallback"
        )