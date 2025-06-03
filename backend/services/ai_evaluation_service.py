"""
TenderWise AI - AI Evaluation Service
Advanced proposal evaluation using AI algorithms
"""

from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime
import json
import re
from dataclasses import dataclass

from models.proposal import Proposal
from models.rfp import RFP
from schemas.proposal import ProposalEvaluationRequest, ProposalEvaluationResponse


@dataclass
class EvaluationCriteria:
    """Evaluation criteria configuration"""
    technical_weight: float = 0.4
    financial_weight: float = 0.3
    compliance_weight: float = 0.3
    max_score: float = 100.0


class AIEvaluationService:
    """Advanced AI-powered proposal evaluation service"""
    
    def __init__(self):
        self.criteria = EvaluationCriteria()
        
    def evaluate_proposal(
        self, 
        db: Session, 
        proposal: Proposal, 
        rfp: RFP,
        evaluation_request: ProposalEvaluationRequest
    ) -> ProposalEvaluationResponse:
        """
        Comprehensive AI evaluation of a proposal
        """
        
        # Initialize scores
        technical_score = None
        financial_score = None
        compliance_score = None
        
        # Evaluate different aspects based on request
        if evaluation_request.evaluate_technical:
            technical_score = self._evaluate_technical_approach(proposal, rfp)
            
        if evaluation_request.evaluate_financial:
            financial_score = self._evaluate_financial_proposal(proposal, rfp)
            
        if evaluation_request.evaluate_compliance:
            compliance_score = self._evaluate_compliance(proposal, rfp)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(
            technical_score, financial_score, compliance_score,
            evaluation_request
        )
        
        # Generate insights
        strengths = self._identify_strengths(proposal, rfp, technical_score, financial_score, compliance_score)
        weaknesses = self._identify_weaknesses(proposal, rfp, technical_score, financial_score, compliance_score)
        risk_factors = self._assess_risk_factors(proposal, rfp)
        recommendation = self._generate_recommendation(overall_score, strengths, weaknesses, risk_factors)
        evaluation_summary = self._generate_evaluation_summary(
            proposal, overall_score, strengths, weaknesses, recommendation
        )
        
        # Apply custom criteria if provided
        if evaluation_request.custom_criteria:
            custom_scores = self._evaluate_custom_criteria(proposal, evaluation_request.custom_criteria)
            overall_score = self._incorporate_custom_scores(overall_score, custom_scores)
        
        return ProposalEvaluationResponse(
            proposal_id=proposal.id,
            overall_score=round(overall_score, 1),
            technical_score=round(technical_score, 1) if technical_score else None,
            financial_score=round(financial_score, 1) if financial_score else None,
            compliance_score=round(compliance_score, 1) if compliance_score else None,
            strengths=strengths,
            weaknesses=weaknesses,
            risk_factors=risk_factors,
            recommendation=recommendation,
            evaluation_summary=evaluation_summary,
            created_at=datetime.utcnow()
        )
    
    def _evaluate_technical_approach(self, proposal: Proposal, rfp: RFP) -> float:
        """Evaluate technical aspects of the proposal"""
        score = 50.0  # Base score
        
        # Check if technical approach is provided
        if proposal.technical_approach:
            score += 20.0
            
            # Analyze technical content depth
            technical_content = proposal.technical_approach.lower()
            
            # Keywords indicating strong technical approach
            positive_keywords = [
                'methodology', 'architecture', 'framework', 'implementation',
                'testing', 'quality', 'standards', 'best practices',
                'scalable', 'secure', 'performance', 'optimization',
                'agile', 'devops', 'automation', 'monitoring'
            ]
            
            keyword_matches = sum(1 for keyword in positive_keywords if keyword in technical_content)
            score += min(keyword_matches * 2, 20)  # Max 20 points for keywords
            
            # Length-based quality assessment
            if len(technical_content) > 500:  # Detailed approach
                score += 10
            elif len(technical_content) > 200:  # Moderate detail
                score += 5
        
        # Check alignment with RFP technical requirements
        if rfp.technical_requirements and proposal.technical_approach:
            alignment_score = self._assess_requirement_alignment(
                proposal.technical_approach,
                rfp.technical_requirements
            )
            score += alignment_score
        
        return min(score, 100.0)
    
    def _evaluate_financial_proposal(self, proposal: Proposal, rfp: RFP) -> float:
        """Evaluate financial aspects of the proposal"""
        score = 50.0  # Base score
        
        # Check if cost information is provided
        if proposal.total_cost:
            score += 15.0
            
            # Compare with RFP estimated budget
            if rfp.estimated_budget:
                cost_ratio = proposal.total_cost / rfp.estimated_budget
                
                if 0.7 <= cost_ratio <= 1.0:  # Within optimal range
                    score += 25.0
                elif 0.5 <= cost_ratio < 0.7:  # Very competitive
                    score += 20.0
                elif 1.0 < cost_ratio <= 1.2:  # Slightly over budget
                    score += 15.0
                elif cost_ratio > 1.5:  # Significantly over budget
                    score -= 10.0
        
        # Check for cost breakdown detail
        if proposal.cost_breakdown:
            score += 10.0
            
            # Analyze cost breakdown completeness
            try:
                if isinstance(proposal.cost_breakdown, dict):
                    breakdown_items = len(proposal.cost_breakdown)
                    if breakdown_items >= 5:  # Detailed breakdown
                        score += 10.0
                    elif breakdown_items >= 3:  # Moderate breakdown
                        score += 5.0
            except:
                pass
        
        return min(score, 100.0)
    
    def _evaluate_compliance(self, proposal: Proposal, rfp: RFP) -> float:
        """Evaluate compliance with RFP requirements"""
        score = 50.0  # Base score
        
        # Check compliance matrix
        if proposal.compliance_matrix:
            score += 20.0
            
            try:
                if isinstance(proposal.compliance_matrix, dict):
                    compliance_items = len(proposal.compliance_matrix)
                    
                    # Analyze compliance responses
                    compliant_items = 0
                    for key, value in proposal.compliance_matrix.items():
                        if isinstance(value, str):
                            value_lower = value.lower()
                            if any(term in value_lower for term in ['compliant', 'yes', 'meets', 'satisfies']):
                                compliant_items += 1
                    
                    if compliance_items > 0:
                        compliance_ratio = compliant_items / compliance_items
                        score += compliance_ratio * 30.0  # Max 30 points for full compliance
            except:
                pass
        
        # Check delivery date alignment
        if proposal.delivery_date and rfp.project_end_date:
            try:
                proposal_date = datetime.fromisoformat(proposal.delivery_date.replace('Z', '+00:00'))
                rfp_end_date = datetime.fromisoformat(rfp.project_end_date.replace('Z', '+00:00'))
                
                if proposal_date <= rfp_end_date:
                    score += 15.0  # Meets deadline
                elif (proposal_date - rfp_end_date).days <= 30:
                    score += 10.0  # Slightly delayed
                else:
                    score -= 5.0   # Significantly delayed
            except:
                pass
        
        return min(score, 100.0)
    
    def _assess_requirement_alignment(self, proposal_text: str, requirements_text: str) -> float:
        """Assess how well proposal aligns with requirements"""
        if not proposal_text or not requirements_text:
            return 0.0
        
        # Extract key terms from requirements
        req_words = set(re.findall(r'\b\w+\b', requirements_text.lower()))
        prop_words = set(re.findall(r'\b\w+\b', proposal_text.lower()))
        
        # Calculate overlap
        if req_words:
            overlap = len(req_words.intersection(prop_words)) / len(req_words)
            return min(overlap * 15.0, 15.0)  # Max 15 points for alignment
        
        return 0.0
    
    def _calculate_overall_score(
        self, 
        technical_score: Optional[float], 
        financial_score: Optional[float], 
        compliance_score: Optional[float],
        evaluation_request: ProposalEvaluationRequest
    ) -> float:
        """Calculate weighted overall score"""
        
        total_weight = 0.0
        weighted_score = 0.0
        
        if technical_score is not None and evaluation_request.evaluate_technical:
            weighted_score += technical_score * self.criteria.technical_weight
            total_weight += self.criteria.technical_weight
        
        if financial_score is not None and evaluation_request.evaluate_financial:
            weighted_score += financial_score * self.criteria.financial_weight
            total_weight += self.criteria.financial_weight
        
        if compliance_score is not None and evaluation_request.evaluate_compliance:
            weighted_score += compliance_score * self.criteria.compliance_weight
            total_weight += self.criteria.compliance_weight
        
        if total_weight > 0:
            return weighted_score / total_weight
        
        return 0.0
    
    def _identify_strengths(
        self, 
        proposal: Proposal, 
        rfp: RFP, 
        technical_score: Optional[float],
        financial_score: Optional[float], 
        compliance_score: Optional[float]
    ) -> List[str]:
        """Identify proposal strengths"""
        strengths = []
        
        # Technical strengths
        if technical_score and technical_score >= 80:
            strengths.append("Strong technical approach with comprehensive methodology")
        if proposal.technical_approach and len(proposal.technical_approach) > 500:
            strengths.append("Detailed technical documentation and planning")
        
        # Financial strengths
        if financial_score and financial_score >= 80:
            strengths.append("Competitive and well-structured pricing")
        if proposal.cost_breakdown and isinstance(proposal.cost_breakdown, dict) and len(proposal.cost_breakdown) >= 5:
            strengths.append("Comprehensive cost breakdown with transparency")
        
        # Compliance strengths
        if compliance_score and compliance_score >= 85:
            strengths.append("Excellent compliance with RFP requirements")
        if proposal.delivery_date and rfp.project_end_date:
            try:
                proposal_date = datetime.fromisoformat(proposal.delivery_date.replace('Z', '+00:00'))
                rfp_end_date = datetime.fromisoformat(rfp.project_end_date.replace('Z', '+00:00'))
                if proposal_date <= rfp_end_date:
                    strengths.append("Realistic delivery timeline that meets project requirements")
            except:
                pass
        
        # Executive summary strength
        if proposal.executive_summary and len(proposal.executive_summary) > 200:
            strengths.append("Clear and comprehensive executive summary")
        
        # Default strengths if none identified
        if not strengths:
            strengths.append("Proposal addresses basic requirements")
        
        return strengths[:5]  # Limit to top 5 strengths
    
    def _identify_weaknesses(
        self, 
        proposal: Proposal, 
        rfp: RFP,
        technical_score: Optional[float],
        financial_score: Optional[float], 
        compliance_score: Optional[float]
    ) -> List[str]:
        """Identify proposal weaknesses"""
        weaknesses = []
        
        # Technical weaknesses
        if technical_score and technical_score < 60:
            weaknesses.append("Technical approach lacks detail or clarity")
        if not proposal.technical_approach:
            weaknesses.append("Missing technical approach documentation")
        
        # Financial weaknesses
        if not proposal.total_cost:
            weaknesses.append("Missing cost information")
        elif financial_score and financial_score < 60:
            weaknesses.append("Pricing may not be competitive or well-justified")
        if not proposal.cost_breakdown:
            weaknesses.append("No detailed cost breakdown provided")
        
        # Compliance weaknesses
        if compliance_score and compliance_score < 70:
            weaknesses.append("Compliance with RFP requirements needs improvement")
        if not proposal.compliance_matrix:
            weaknesses.append("Missing compliance matrix or requirement mapping")
        
        # Timeline weaknesses
        if proposal.delivery_date and rfp.project_end_date:
            try:
                proposal_date = datetime.fromisoformat(proposal.delivery_date.replace('Z', '+00:00'))
                rfp_end_date = datetime.fromisoformat(rfp.project_end_date.replace('Z', '+00:00'))
                if (proposal_date - rfp_end_date).days > 30:
                    weaknesses.append("Delivery timeline extends significantly beyond required date")
            except:
                pass
        
        return weaknesses[:5]  # Limit to top 5 weaknesses
    
    def _assess_risk_factors(self, proposal: Proposal, rfp: RFP) -> List[str]:
        """Assess potential risk factors"""
        risks = []
        
        # Timeline risks
        if proposal.delivery_date and rfp.project_end_date:
            try:
                proposal_date = datetime.fromisoformat(proposal.delivery_date.replace('Z', '+00:00'))
                rfp_end_date = datetime.fromisoformat(rfp.project_end_date.replace('Z', '+00:00'))
                if proposal_date == rfp_end_date:
                    risks.append("Tight delivery timeline with no buffer for delays")
            except:
                pass
        
        # Financial risks
        if proposal.total_cost and rfp.estimated_budget:
            cost_ratio = proposal.total_cost / rfp.estimated_budget
            if cost_ratio < 0.6:
                risks.append("Unusually low pricing may indicate underestimation or quality concerns")
            elif cost_ratio > 1.3:
                risks.append("High cost may exceed available budget")
        
        # Technical risks
        if proposal.technical_approach:
            technical_content = proposal.technical_approach.lower()
            risk_indicators = ['untested', 'experimental', 'new technology', 'cutting edge', 'beta']
            if any(indicator in technical_content for indicator in risk_indicators):
                risks.append("Technical approach includes unproven or experimental elements")
        
        # Compliance risks
        if proposal.compliance_matrix:
            try:
                if isinstance(proposal.compliance_matrix, dict):
                    for key, value in proposal.compliance_matrix.items():
                        if isinstance(value, str) and any(term in value.lower() for term in ['partial', 'limited', 'exception']):
                            risks.append("Some compliance requirements may not be fully met")
                            break
            except:
                pass
        
        return risks[:4]  # Limit to top 4 risk factors
    
    def _generate_recommendation(
        self, 
        overall_score: float, 
        strengths: List[str], 
        weaknesses: List[str], 
        risk_factors: List[str]
    ) -> str:
        """Generate overall recommendation"""
        
        if overall_score >= 85:
            return "STRONGLY RECOMMEND"
        elif overall_score >= 75:
            return "RECOMMEND"
        elif overall_score >= 65:
            return "CONSIDER WITH RESERVATIONS"
        elif overall_score >= 50:
            return "NOT RECOMMENDED"
        else:
            return "REJECT"
    
    def _generate_evaluation_summary(
        self, 
        proposal: Proposal, 
        overall_score: float, 
        strengths: List[str], 
        weaknesses: List[str], 
        recommendation: str
    ) -> str:
        """Generate comprehensive evaluation summary"""
        
        summary_parts = []
        
        # Overall assessment
        if overall_score >= 80:
            summary_parts.append("This proposal demonstrates strong capabilities and alignment with requirements.")
        elif overall_score >= 65:
            summary_parts.append("This proposal shows good potential with some areas for improvement.")
        else:
            summary_parts.append("This proposal has significant gaps that need to be addressed.")
        
        # Key strengths
        if strengths:
            summary_parts.append(f"Key strengths include: {'; '.join(strengths[:3])}.")
        
        # Main concerns
        if weaknesses:
            summary_parts.append(f"Primary concerns are: {'; '.join(weaknesses[:2])}.")
        
        # Final recommendation context
        rec_context = {
            "STRONGLY RECOMMEND": "This proposal represents excellent value and capability.",
            "RECOMMEND": "This proposal meets requirements with acceptable risk levels.",
            "CONSIDER WITH RESERVATIONS": "This proposal requires careful evaluation of identified risks.",
            "NOT RECOMMENDED": "This proposal does not meet minimum requirements.",
            "REJECT": "This proposal has significant deficiencies."
        }
        
        summary_parts.append(rec_context.get(recommendation, "Further evaluation recommended."))
        
        return " ".join(summary_parts)
    
    def _evaluate_custom_criteria(self, proposal: Proposal, custom_criteria: Dict[str, float]) -> Dict[str, float]:
        """Evaluate proposal against custom criteria"""
        # This is a simplified implementation
        # In a real system, this would involve more sophisticated AI analysis
        
        scores = {}
        for criterion, weight in custom_criteria.items():
            # Mock evaluation based on criterion name
            if 'innovation' in criterion.lower():
                scores[criterion] = 75.0
            elif 'experience' in criterion.lower():
                scores[criterion] = 85.0
            elif 'team' in criterion.lower():
                scores[criterion] = 80.0
            else:
                scores[criterion] = 70.0
        
        return scores
    
    def _incorporate_custom_scores(self, base_score: float, custom_scores: Dict[str, float]) -> float:
        """Incorporate custom criteria scores into overall score"""
        if not custom_scores:
            return base_score
        
        # Weight custom scores at 20% of total
        custom_weight = 0.2
        base_weight = 0.8
        
        avg_custom_score = sum(custom_scores.values()) / len(custom_scores)
        
        return (base_score * base_weight) + (avg_custom_score * custom_weight)