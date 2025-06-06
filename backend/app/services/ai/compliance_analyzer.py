"""
Compliance Analysis Service for TenderWise AI Platform
Module 2: Proposal Compliance & Vendor Assessment

AI-powered service for analyzing vendor proposal compliance against RFP requirements.
Provides requirement extraction, compliance scoring, gap analysis, and vendor ranking.
"""

import re
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

from ..document.document_extractor import DocumentExtractor
from ...models.compliance_analysis import (
    ComplianceAnalysis, RFPRequirement, VendorProposal, ComplianceMatrix, ComplianceScore,
    AnalysisStatus, RequirementType, PriorityLevel, ComplianceStatus
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RequirementMatch:
    """Data class for requirement-proposal matching results"""
    requirement_id: str
    proposal_id: str
    compliance_status: ComplianceStatus
    compliance_score: float
    confidence_level: float
    evidence_text: str
    gap_description: str
    recommendations: str
    keywords_matched: List[str]


@dataclass
class VendorRanking:
    """Data class for vendor ranking results"""
    proposal_id: str
    vendor_name: str
    overall_score: float
    rank_position: int
    category_scores: Dict[str, float]
    compliance_distribution: Dict[str, int]
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]


class ComplianceAnalyzerService:
    """
    AI-powered compliance analysis service for vendor proposal assessment
    """
    
    def __init__(self):
        self.document_extractor = DocumentExtractor()
        
        # AI Analysis Configuration
        self.min_requirement_length = 20  # Minimum characters for valid requirement
        self.max_requirements_per_section = 50  # Limit requirements per section
        self.compliance_thresholds = {
            'compliant': 80.0,     # 80-100%: Fully compliant
            'partial': 40.0,       # 40-79%: Partially compliant
            'non_compliant': 1.0   # 1-39%: Non-compliant, 0%: Not addressed
        }
        
        # Requirement extraction patterns
        self.requirement_patterns = [
            r'(?:shall|must|will|should|requires?|needs?)\s+(.{20,200})',
            r'(?:requirement|mandatory|essential|critical):\s*(.{20,200})',
            r'(?:vendor|supplier|contractor)\s+(?:shall|must|will)\s+(.{20,200})',
            r'(?:system|solution|platform)\s+(?:shall|must|will)\s+(.{20,200})',
            r'(?:provide|deliver|implement|support)\s+(.{20,200})',
        ]
        
        # Category keywords for requirement classification
        self.category_keywords = {
            RequirementType.TECHNICAL: [
                'technical', 'technology', 'system', 'software', 'hardware', 'architecture',
                'integration', 'api', 'database', 'security', 'performance', 'scalability',
                'infrastructure', 'platform', 'framework', 'protocol', 'standard'
            ],
            RequirementType.FUNCTIONAL: [
                'function', 'feature', 'capability', 'workflow', 'process', 'user',
                'interface', 'ui', 'ux', 'dashboard', 'report', 'notification',
                'automation', 'configuration', 'customization', 'operation'
            ],
            RequirementType.COMMERCIAL: [
                'cost', 'price', 'pricing', 'budget', 'commercial', 'financial',
                'payment', 'license', 'subscription', 'maintenance', 'support',
                'warranty', 'sla', 'contract', 'terms', 'conditions'
            ],
            RequirementType.LEGAL: [
                'legal', 'compliance', 'regulation', 'law', 'gdpr', 'privacy',
                'confidentiality', 'intellectual property', 'liability', 'indemnity',
                'insurance', 'audit', 'certification', 'standard', 'policy'
            ],
            RequirementType.OPERATIONAL: [
                'operational', 'operation', 'deployment', 'implementation', 'training',
                'documentation', 'manual', 'guide', 'procedure', 'process',
                'timeline', 'schedule', 'milestone', 'deliverable', 'resource'
            ]
        }
        
        # Priority keywords for requirement prioritization
        self.priority_keywords = {
            PriorityLevel.HIGH: [
                'critical', 'essential', 'mandatory', 'required', 'must have',
                'crucial', 'vital', 'key', 'primary', 'core', 'fundamental'
            ],
            PriorityLevel.MEDIUM: [
                'important', 'significant', 'should have', 'preferred', 'desired',
                'recommended', 'advised', 'suggested', 'beneficial', 'useful'
            ],
            PriorityLevel.LOW: [
                'optional', 'nice to have', 'could have', 'may have', 'if possible',
                'additional', 'extra', 'supplementary', 'enhancement', 'future'
            ]
        }

    async def extract_requirements_from_rfp(self, rfp_content: str) -> List[Dict[str, Any]]:
        """
        Extract structured requirements from RFP document content
        
        Args:
            rfp_content: Raw text content from RFP document
            
        Returns:
            List of extracted requirements with metadata
        """
        logger.info("Starting requirement extraction from RFP content")
        
        requirements = []
        
        # Split content into sections for better analysis
        sections = self._split_into_sections(rfp_content)
        
        for section_name, section_content in sections.items():
            # Extract requirements from this section
            section_requirements = self._extract_requirements_from_section(
                section_content, section_name
            )
            requirements.extend(section_requirements)
        
        logger.info(f"Extracted {len(requirements)} requirements from RFP")
        return requirements

    def _split_into_sections(self, content: str) -> Dict[str, str]:
        """Split RFP content into logical sections"""
        sections = {}
        
        # Common RFP section patterns
        section_patterns = [
            r'(?i)(technical\s+requirements?|technical\s+specifications?)',
            r'(?i)(functional\s+requirements?|functional\s+specifications?)',
            r'(?i)(commercial\s+requirements?|commercial\s+terms?)',
            r'(?i)(legal\s+requirements?|legal\s+terms?)',
            r'(?i)(operational\s+requirements?|operational\s+terms?)',
            r'(?i)(scope\s+of\s+work|project\s+scope)',
            r'(?i)(deliverables?|outputs?)',
            r'(?i)(timeline|schedule|milestones?)',
            r'(?i)(evaluation\s+criteria|assessment\s+criteria)',
        ]
        
        # Try to split by headers/sections
        lines = content.split('\n')
        current_section = 'general'
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line is a section header
            is_header = False
            for pattern in section_patterns:
                if re.search(pattern, line):
                    # Save previous section
                    if current_content:
                        sections[current_section] = '\n'.join(current_content)
                    
                    # Start new section
                    current_section = line.lower()
                    current_content = []
                    is_header = True
                    break
            
            if not is_header:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        # If no sections found, use entire content as general
        if not sections:
            sections['general'] = content
            
        return sections

    def _extract_requirements_from_section(self, section_content: str, section_name: str) -> List[Dict[str, Any]]:
        """Extract requirements from a specific section"""
        requirements = []
        
        # Use multiple extraction strategies
        for pattern in self.requirement_patterns:
            matches = re.findall(pattern, section_content, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                requirement_text = match.strip()
                
                # Filter out short or invalid requirements
                if len(requirement_text) < self.min_requirement_length:
                    continue
                    
                # Clean up the requirement text
                requirement_text = self._clean_requirement_text(requirement_text)
                
                # Skip if already found similar requirement
                if self._is_duplicate_requirement(requirement_text, requirements):
                    continue
                
                # Classify the requirement
                req_type = self._classify_requirement_type(requirement_text, section_name)
                priority = self._classify_requirement_priority(requirement_text)
                
                # Extract keywords
                keywords = self._extract_keywords(requirement_text)
                
                requirement = {
                    'text': requirement_text,
                    'summary': requirement_text[:200] + '...' if len(requirement_text) > 200 else requirement_text,
                    'category': section_name,
                    'type': req_type,
                    'priority': priority,
                    'section_reference': section_name,
                    'keywords': keywords,
                    'weight': self._calculate_requirement_weight(req_type, priority),
                    'extraction_confidence': 0.85  # Base confidence score
                }
                
                requirements.append(requirement)
                
                # Limit requirements per section
                if len(requirements) >= self.max_requirements_per_section:
                    break
        
        return requirements

    def _clean_requirement_text(self, text: str) -> str:
        """Clean and normalize requirement text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove leading/trailing punctuation
        text = text.strip('.,;:!?')
        
        # Ensure proper capitalization
        if text and not text[0].isupper():
            text = text[0].upper() + text[1:]
            
        return text

    def _is_duplicate_requirement(self, new_req: str, existing_reqs: List[Dict[str, Any]]) -> bool:
        """Check if requirement is duplicate or very similar to existing ones"""
        new_words = set(new_req.lower().split())
        
        for existing in existing_reqs:
            existing_words = set(existing['text'].lower().split())
            
            # Calculate Jaccard similarity
            intersection = len(new_words.intersection(existing_words))
            union = len(new_words.union(existing_words))
            
            if union > 0:
                similarity = intersection / union
                if similarity > 0.7:  # 70% similarity threshold
                    return True
                    
        return False

    def _classify_requirement_type(self, text: str, section: str) -> RequirementType:
        """Classify requirement into type categories"""
        text_lower = text.lower()
        section_lower = section.lower()
        
        # Count keyword matches for each category
        scores = {}
        for req_type, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            
            # Boost score if section name matches category
            if req_type.value.lower() in section_lower:
                score += 3
                
            scores[req_type] = score
        
        # Return type with highest score, default to FUNCTIONAL
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        else:
            return RequirementType.FUNCTIONAL

    def _classify_requirement_priority(self, text: str) -> PriorityLevel:
        """Classify requirement priority level"""
        text_lower = text.lower()
        
        # Count keyword matches for each priority
        scores = {}
        for priority, keywords in self.priority_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[priority] = score
        
        # Return priority with highest score, default to MEDIUM
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        else:
            return PriorityLevel.MEDIUM

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract key terms from requirement text"""
        # Simple keyword extraction - can be enhanced with NLP
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter out common words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        keywords = [word for word in words if word not in stop_words]
        
        # Return top 10 most relevant keywords
        return list(set(keywords))[:10]

    def _calculate_requirement_weight(self, req_type: RequirementType, priority: PriorityLevel) -> float:
        """Calculate importance weight for requirement"""
        type_weights = {
            RequirementType.TECHNICAL: 1.0,
            RequirementType.FUNCTIONAL: 0.9,
            RequirementType.COMMERCIAL: 0.8,
            RequirementType.LEGAL: 0.7,
            RequirementType.OPERATIONAL: 0.6
        }
        
        priority_weights = {
            PriorityLevel.HIGH: 1.0,
            PriorityLevel.MEDIUM: 0.7,
            PriorityLevel.LOW: 0.4
        }
        
        return type_weights.get(req_type, 0.5) * priority_weights.get(priority, 0.5)

    async def analyze_proposal_compliance(
        self, 
        requirements: List[RFPRequirement], 
        proposal: VendorProposal
    ) -> List[RequirementMatch]:
        """
        Analyze how well a vendor proposal addresses RFP requirements
        
        Args:
            requirements: List of RFP requirements to check
            proposal: Vendor proposal to analyze
            
        Returns:
            List of requirement matches with compliance scores
        """
        logger.info(f"Analyzing compliance for proposal {proposal.vendor_name}")
        
        matches = []
        proposal_content = proposal.proposal_content.lower()
        
        for requirement in requirements:
            match = await self._analyze_requirement_compliance(
                requirement, proposal, proposal_content
            )
            matches.append(match)
        
        logger.info(f"Completed compliance analysis: {len(matches)} requirement matches")
        return matches

    async def _analyze_requirement_compliance(
        self, 
        requirement: RFPRequirement, 
        proposal: VendorProposal,
        proposal_content_lower: str
    ) -> RequirementMatch:
        """Analyze compliance for a single requirement"""
        
        # Extract relevant text from proposal
        evidence_text = self._find_evidence_text(requirement, proposal_content_lower)
        
        # Calculate compliance score
        compliance_score = self._calculate_compliance_score(requirement, evidence_text)
        
        # Determine compliance status
        compliance_status = self._determine_compliance_status(compliance_score)
        
        # Identify gaps and recommendations
        gap_description = self._identify_gaps(requirement, evidence_text, compliance_score)
        recommendations = self._generate_recommendations(requirement, compliance_status, gap_description)
        
        # Find matched keywords
        keywords_matched = self._find_matched_keywords(requirement.keywords or [], evidence_text)
        
        return RequirementMatch(
            requirement_id=requirement.id,
            proposal_id=proposal.id,
            compliance_status=compliance_status,
            compliance_score=compliance_score,
            confidence_level=0.8,  # Base confidence level
            evidence_text=evidence_text[:500],  # Limit evidence text length
            gap_description=gap_description,
            recommendations=recommendations,
            keywords_matched=keywords_matched
        )

    def _find_evidence_text(self, requirement: RFPRequirement, proposal_content: str) -> str:
        """Find text in proposal that addresses the requirement"""
        keywords = requirement.keywords or []
        requirement_text = requirement.requirement_text.lower()
        
        # Extract key terms from requirement
        req_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', requirement_text))
        
        # Find sentences in proposal that contain requirement keywords
        sentences = re.split(r'[.!?]+', proposal_content)
        relevant_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:  # Skip very short sentences
                continue
                
            # Count matching words
            sentence_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', sentence))
            matches = len(req_words.intersection(sentence_words))
            
            # Also check for keyword matches
            keyword_matches = sum(1 for keyword in keywords if keyword in sentence)
            
            total_relevance = matches + (keyword_matches * 2)  # Weight keywords higher
            
            if total_relevance >= 2:  # Minimum relevance threshold
                relevant_sentences.append((sentence, total_relevance))
        
        # Sort by relevance and return top sentences
        relevant_sentences.sort(key=lambda x: x[1], reverse=True)
        top_sentences = [sent[0] for sent in relevant_sentences[:3]]
        
        return '. '.join(top_sentences) if top_sentences else ""

    def _calculate_compliance_score(self, requirement: RFPRequirement, evidence_text: str) -> float:
        """Calculate compliance score (0-100) based on evidence"""
        if not evidence_text:
            return 0.0
        
        # Basic scoring factors
        score = 0.0
        
        # 1. Evidence length factor (more text = potentially better coverage)
        length_factor = min(len(evidence_text) / 200, 1.0) * 20  # Max 20 points
        score += length_factor
        
        # 2. Keyword matching factor
        req_keywords = set((requirement.keywords or [])[:10])  # Top 10 keywords
        evidence_lower = evidence_text.lower()
        
        if req_keywords:
            matched_keywords = sum(1 for keyword in req_keywords if keyword in evidence_lower)
            keyword_factor = (matched_keywords / len(req_keywords)) * 40  # Max 40 points
            score += keyword_factor
        
        # 3. Requirement text similarity factor
        req_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', requirement.requirement_text.lower()))
        evidence_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', evidence_lower))
        
        if req_words:
            word_overlap = len(req_words.intersection(evidence_words)) / len(req_words)
            similarity_factor = word_overlap * 30  # Max 30 points
            score += similarity_factor
        
        # 4. Action word presence (indicates implementation)
        action_words = ['provide', 'deliver', 'implement', 'support', 'ensure', 'include', 'offer']
        action_presence = any(word in evidence_lower for word in action_words)
        if action_presence:
            score += 10  # Bonus 10 points
        
        return min(score, 100.0)  # Cap at 100

    def _determine_compliance_status(self, score: float) -> ComplianceStatus:
        """Determine compliance status based on score"""
        if score >= self.compliance_thresholds['compliant']:
            return ComplianceStatus.COMPLIANT
        elif score >= self.compliance_thresholds['partial']:
            return ComplianceStatus.PARTIAL
        elif score >= self.compliance_thresholds['non_compliant']:
            return ComplianceStatus.NON_COMPLIANT
        else:
            return ComplianceStatus.NOT_ADDRESSED

    def _identify_gaps(self, requirement: RFPRequirement, evidence_text: str, score: float) -> str:
        """Identify gaps in requirement compliance"""
        if score >= 80:
            return "No significant gaps identified."
        elif score >= 40:
            return f"Partial compliance - some aspects of the requirement may not be fully addressed."
        elif score > 0:
            return f"Significant gaps - the proposal does not adequately address this {requirement.requirement_type.value.lower()} requirement."
        else:
            return f"Not addressed - no evidence found that this {requirement.requirement_type.value.lower()} requirement is addressed."

    def _generate_recommendations(self, requirement: RFPRequirement, status: ComplianceStatus, gap: str) -> str:
        """Generate recommendations for improvement"""
        if status == ComplianceStatus.COMPLIANT:
            return "Requirement is well addressed. No additional action needed."
        elif status == ComplianceStatus.PARTIAL:
            return f"Consider providing more detailed information about {requirement.requirement_type.value.lower()} capabilities and implementation approach."
        elif status == ComplianceStatus.NON_COMPLIANT:
            return f"Significant improvement needed. Provide comprehensive details on how this {requirement.requirement_type.value.lower()} requirement will be met."
        else:
            return f"This {requirement.requirement_type.value.lower()} requirement must be addressed. Please provide a detailed response."

    def _find_matched_keywords(self, req_keywords: List[str], evidence_text: str) -> List[str]:
        """Find which requirement keywords were matched in evidence"""
        evidence_lower = evidence_text.lower()
        return [keyword for keyword in req_keywords if keyword in evidence_lower]

    async def calculate_vendor_rankings(
        self, 
        compliance_matrix: List[ComplianceMatrix],
        proposals: List[VendorProposal],
        requirements: List[RFPRequirement]
    ) -> List[VendorRanking]:
        """
        Calculate overall vendor rankings based on compliance matrix
        
        Args:
            compliance_matrix: All compliance assessments
            proposals: All vendor proposals
            requirements: All RFP requirements
            
        Returns:
            List of vendor rankings sorted by overall score
        """
        logger.info("Calculating vendor rankings")
        
        rankings = []
        
        for proposal in proposals:
            # Get all compliance records for this proposal
            proposal_compliance = [
                matrix for matrix in compliance_matrix 
                if matrix.proposal_id == proposal.id
            ]
            
            if not proposal_compliance:
                continue
            
            # Calculate scores
            ranking = self._calculate_vendor_score(
                proposal, proposal_compliance, requirements
            )
            rankings.append(ranking)
        
        # Sort by overall score (descending)
        rankings.sort(key=lambda x: x.overall_score, reverse=True)
        
        # Assign rank positions
        for i, ranking in enumerate(rankings):
            ranking.rank_position = i + 1
        
        logger.info(f"Calculated rankings for {len(rankings)} vendors")
        return rankings

    def _calculate_vendor_score(
        self, 
        proposal: VendorProposal, 
        compliance_records: List[ComplianceMatrix],
        requirements: List[RFPRequirement]
    ) -> VendorRanking:
        """Calculate comprehensive score for a vendor"""
        
        # Overall scoring
        total_score = sum(record.compliance_score for record in compliance_records)
        overall_score = total_score / len(compliance_records) if compliance_records else 0
        
        # Category scores
        category_scores = {}
        req_by_type = {}
        
        # Group requirements by type
        for req in requirements:
            req_type = req.requirement_type.value
            if req_type not in req_by_type:
                req_by_type[req_type] = []
            req_by_type[req_type].append(req.id)
        
        # Calculate score per category
        for req_type, req_ids in req_by_type.items():
            category_records = [
                record for record in compliance_records 
                if record.requirement_id in req_ids
            ]
            
            if category_records:
                category_score = sum(record.compliance_score for record in category_records)
                category_scores[req_type.lower()] = category_score / len(category_records)
            else:
                category_scores[req_type.lower()] = 0
        
        # Compliance distribution
        compliance_dist = {
            'compliant': sum(1 for r in compliance_records if r.compliance_status == ComplianceStatus.COMPLIANT),
            'partial': sum(1 for r in compliance_records if r.compliance_status == ComplianceStatus.PARTIAL),
            'non_compliant': sum(1 for r in compliance_records if r.compliance_status == ComplianceStatus.NON_COMPLIANT),
            'not_addressed': sum(1 for r in compliance_records if r.compliance_status == ComplianceStatus.NOT_ADDRESSED)
        }
        
        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []
        
        for req_type, score in category_scores.items():
            if score >= 80:
                strengths.append(f"Strong {req_type} capabilities")
            elif score < 50:
                weaknesses.append(f"Weak {req_type} coverage")
        
        # Generate recommendations
        recommendations = []
        if compliance_dist['not_addressed'] > 0:
            recommendations.append(f"Address {compliance_dist['not_addressed']} unaddressed requirements")
        if compliance_dist['non_compliant'] > 0:
            recommendations.append(f"Improve response to {compliance_dist['non_compliant']} non-compliant requirements")
        if overall_score < 70:
            recommendations.append("Significant improvement needed in overall proposal quality")
        
        return VendorRanking(
            proposal_id=proposal.id,
            vendor_name=proposal.vendor_name,
            overall_score=overall_score,
            rank_position=0,  # Will be set later
            category_scores=category_scores,
            compliance_distribution=compliance_dist,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations
        )