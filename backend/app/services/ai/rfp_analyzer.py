"""
RFP Analysis Service - Module 1 Implementation
Provides Go/No-Go decision support and strategic analysis
"""
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
import json
import re
from datetime import datetime, date
from dataclasses import dataclass
from enum import Enum

from .llm_service import llm_service, LLMMessage

logger = logging.getLogger(__name__)


class DecisionType(Enum):
    """Go/No-Go decision types"""
    GO = "go"
    NO_GO = "no_go"
    CONDITIONAL = "conditional"
    NEEDS_REVIEW = "needs_review"


class RiskLevel(Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class GoNoGoDecision:
    """Go/No-Go decision result"""
    decision: DecisionType
    confidence_score: float  # 0.0 to 1.0
    primary_justification: str
    detailed_reasoning: List[str]
    risk_factors: List[str]
    success_factors: List[str]
    conditions: List[str]  # For conditional decisions
    estimated_win_probability: float  # 0.0 to 1.0


@dataclass
class RiskAssessment:
    """Risk assessment result"""
    overall_risk_level: RiskLevel
    technical_risks: List[Dict[str, Any]]
    commercial_risks: List[Dict[str, Any]]
    operational_risks: List[Dict[str, Any]]
    legal_risks: List[Dict[str, Any]]
    mitigation_strategies: List[Dict[str, Any]]
    risk_score: float  # 0.0 to 10.0


@dataclass
class ProjectInsights:
    """Project insights and KPIs"""
    project_complexity: str  # low, medium, high, very_high
    estimated_duration_months: Optional[int]
    estimated_cost_range: Optional[Dict[str, float]]
    technology_stack: List[str]
    required_team_size: Optional[int]
    key_success_factors: List[str]
    competitive_advantages: List[str]
    potential_challenges: List[str]


@dataclass
class AnalysisResult:
    """Complete RFP analysis result"""
    rfp_id: str
    analysis_id: str
    timestamp: datetime
    go_no_go_decision: GoNoGoDecision
    risk_assessment: RiskAssessment
    project_insights: ProjectInsights
    kpi_dashboard: Dict[str, Any]
    raw_analysis: Dict[str, Any]


class RFPAnalyzer:
    """Advanced RFP Analysis Service for Strategic Decision Support"""
    
    def __init__(self):
        self.analysis_prompts = {
            "strategic_analysis": """You are a senior business strategist and RFP expert. Analyze this RFP for strategic decision making.

            RFP Content:
            {rfp_content}

            Company Context:
            - Company Name: {company_name}
            - Industry: {industry}
            - Company Size: {company_size}
            - Core Capabilities: {capabilities}
            - Strategic Goals: {strategic_goals}

            Provide a comprehensive strategic analysis including:

            1. STRATEGIC ALIGNMENT
            - How well does this opportunity align with our strategic goals?
            - Does this leverage our core capabilities?
            - Market positioning implications

            2. COMPETITIVE LANDSCAPE
            - Expected competition level (high/medium/low)
            - Our competitive advantages/disadvantages
            - Unique value propositions we can offer

            3. RESOURCE REQUIREMENTS
            - Estimated team size and skill requirements
            - Technology infrastructure needs
            - Timeline feasibility assessment

            4. FINANCIAL ANALYSIS
            - Revenue potential assessment
            - Cost estimation (rough order of magnitude)
            - Profit margin expectations
            - ROI projections

            5. RISK ASSESSMENT
            - Technical delivery risks
            - Commercial/contractual risks
            - Operational risks
            - Legal/compliance risks
            - Client/relationship risks

            6. SUCCESS PROBABILITY
            - Win probability assessment (0-100%)
            - Key factors that could increase success
            - Potential deal breakers or red flags

            Return a detailed JSON response with structured analysis.""",

            "go_no_go_decision": """Based on the strategic analysis, make a Go/No-Go recommendation.

            Analysis Context:
            {analysis_context}

            Decision Criteria:
            - Strategic alignment (weight: 25%)
            - Win probability (weight: 25%) 
            - Resource availability (weight: 20%)
            - Risk level (weight: 15%)
            - Financial attractiveness (weight: 15%)

            Provide a clear recommendation:

            Return JSON response:
            {{
                "decision": "go|no_go|conditional|needs_review",
                "confidence_score": 0.85,
                "primary_justification": "Clear primary reason for decision",
                "detailed_reasoning": [
                    "Specific reason 1",
                    "Specific reason 2",
                    "Specific reason 3"
                ],
                "risk_factors": ["Risk 1", "Risk 2"],
                "success_factors": ["Success factor 1", "Success factor 2"],
                "conditions": ["Condition 1 for conditional decisions"],
                "estimated_win_probability": 0.75,
                "recommendation_summary": "Executive summary of recommendation"
            }}""",

            "risk_assessment": """Conduct a detailed risk assessment for this RFP opportunity.

            RFP Content: {rfp_content}
            Strategic Analysis: {strategic_analysis}

            Assess risks across all dimensions:

            1. TECHNICAL RISKS
            - Technology complexity and maturity
            - Integration challenges
            - Performance requirements feasibility
            - Technical skill gaps

            2. COMMERCIAL RISKS
            - Pricing pressures
            - Contract terms and conditions
            - Payment terms and cash flow
            - Scope creep potential

            3. OPERATIONAL RISKS
            - Resource availability
            - Timeline constraints
            - Delivery complexity
            - Quality assurance challenges

            4. LEGAL/COMPLIANCE RISKS
            - Regulatory requirements
            - Intellectual property concerns
            - Data privacy and security
            - Contractual obligations

            For each risk, provide:
            - Risk description
            - Probability (low/medium/high)
            - Impact (low/medium/high) 
            - Mitigation strategies

            Return detailed JSON response with risk matrix and mitigation plans.""",

            "project_insights": """Extract detailed project insights and KPIs from the RFP.

            RFP Content: {rfp_content}

            Extract and analyze:

            1. PROJECT CHARACTERISTICS
            - Complexity assessment (low/medium/high/very_high)
            - Project type and category
            - Estimated duration
            - Technology requirements

            2. RESOURCE REQUIREMENTS
            - Team size estimation
            - Required skill sets
            - Technology infrastructure needs
            - Third-party dependencies

            3. SUCCESS FACTORS
            - Critical success factors
            - Key performance indicators
            - Quality metrics
            - Delivery milestones

            4. MARKET CONTEXT
            - Industry trends relevance
            - Competitive landscape
            - Innovation opportunities
            - Strategic positioning

            Return comprehensive JSON with project insights and recommended KPIs."""
        }

    async def analyze_rfp_comprehensive(
        self,
        rfp_content: str,
        rfp_id: str,
        company_context: Optional[Dict[str, Any]] = None
    ) -> AnalysisResult:
        """
        Perform comprehensive RFP analysis with Go/No-Go decision
        
        Args:
            rfp_content: Full RFP document content
            rfp_id: Unique RFP identifier
            company_context: Company information for contextual analysis
            
        Returns:
            Complete analysis result with decision and insights
        """
        try:
            logger.info(f"Starting comprehensive RFP analysis for RFP {rfp_id}")
            
            # Default company context if not provided
            if not company_context:
                company_context = {
                    "company_name": "TenderWise Client",
                    "industry": "Technology Services",
                    "company_size": "Medium Enterprise",
                    "capabilities": ["Software Development", "AI/ML", "Cloud Solutions"],
                    "strategic_goals": ["Growth", "Innovation", "Market Expansion"]
                }

            # Step 1: Strategic Analysis
            strategic_analysis = await self._perform_strategic_analysis(
                rfp_content, company_context
            )

            # Step 2: Go/No-Go Decision
            go_no_go_decision = await self._make_go_no_go_decision(
                rfp_content, strategic_analysis
            )

            # Step 3: Risk Assessment
            risk_assessment = await self._assess_risks(
                rfp_content, strategic_analysis
            )

            # Step 4: Project Insights
            project_insights = await self._extract_project_insights(
                rfp_content
            )

            # Step 5: Generate KPI Dashboard
            kpi_dashboard = await self._generate_kpi_dashboard(
                strategic_analysis, risk_assessment, project_insights
            )

            # Compile complete analysis result
            analysis_result = AnalysisResult(
                rfp_id=rfp_id,
                analysis_id=f"analysis_{rfp_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                timestamp=datetime.now(),
                go_no_go_decision=go_no_go_decision,
                risk_assessment=risk_assessment,
                project_insights=project_insights,
                kpi_dashboard=kpi_dashboard,
                raw_analysis={
                    "strategic_analysis": strategic_analysis,
                    "company_context": company_context
                }
            )

            logger.info(f"Completed comprehensive RFP analysis for RFP {rfp_id}")
            return analysis_result

        except Exception as e:
            logger.error(f"Error in comprehensive RFP analysis: {str(e)}")
            raise

    async def _perform_strategic_analysis(
        self, 
        rfp_content: str, 
        company_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform strategic analysis of RFP"""
        
        prompt = self.analysis_prompts["strategic_analysis"].format(
            rfp_content=rfp_content[:8000],  # Limit content for prompt
            **company_context
        )

        messages = [
            LLMMessage(role="system", content="You are a strategic business analyst specializing in RFP evaluation."),
            LLMMessage(role="user", content=prompt)
        ]

        response = await llm_service.generate_response(
            messages=messages,
            max_tokens=2000,
            temperature=0.3
        )

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback analysis if JSON parsing fails
            return {
                "strategic_alignment": "medium",
                "competitive_position": "competitive",
                "resource_requirements": "moderate",
                "financial_attractiveness": "medium",
                "analysis_text": response
            }

    async def _make_go_no_go_decision(
        self, 
        rfp_content: str, 
        strategic_analysis: Dict[str, Any]
    ) -> GoNoGoDecision:
        """Make Go/No-Go decision based on analysis"""
        
        prompt = self.analysis_prompts["go_no_go_decision"].format(
            analysis_context=json.dumps(strategic_analysis, indent=2)
        )

        messages = [
            LLMMessage(role="system", content="You are a senior executive making strategic Go/No-Go decisions for RFP opportunities."),
            LLMMessage(role="user", content=prompt)
        ]

        response = await llm_service.generate_response(
            messages=messages,
            max_tokens=1000,
            temperature=0.2
        )

        try:
            decision_data = json.loads(response)
            
            return GoNoGoDecision(
                decision=DecisionType(decision_data.get("decision", "needs_review")),
                confidence_score=decision_data.get("confidence_score", 0.5),
                primary_justification=decision_data.get("primary_justification", ""),
                detailed_reasoning=decision_data.get("detailed_reasoning", []),
                risk_factors=decision_data.get("risk_factors", []),
                success_factors=decision_data.get("success_factors", []),
                conditions=decision_data.get("conditions", []),
                estimated_win_probability=decision_data.get("estimated_win_probability", 0.5)
            )
        except (json.JSONDecodeError, ValueError):
            # Fallback decision
            return GoNoGoDecision(
                decision=DecisionType.NEEDS_REVIEW,
                confidence_score=0.5,
                primary_justification="Analysis requires human review",
                detailed_reasoning=["Automated analysis inconclusive"],
                risk_factors=["Analysis uncertainty"],
                success_factors=["Manual review required"],
                conditions=[],
                estimated_win_probability=0.5
            )

    async def _assess_risks(
        self, 
        rfp_content: str, 
        strategic_analysis: Dict[str, Any]
    ) -> RiskAssessment:
        """Perform detailed risk assessment"""
        
        prompt = self.analysis_prompts["risk_assessment"].format(
            rfp_content=rfp_content[:6000],
            strategic_analysis=json.dumps(strategic_analysis, indent=2)
        )

        messages = [
            LLMMessage(role="system", content="You are a risk management expert analyzing RFP opportunities."),
            LLMMessage(role="user", content=prompt)
        ]

        response = await llm_service.generate_response(
            messages=messages,
            max_tokens=1500,
            temperature=0.3
        )

        try:
            risk_data = json.loads(response)
            
            # Calculate overall risk level
            risk_scores = []
            for category in ["technical_risks", "commercial_risks", "operational_risks", "legal_risks"]:
                category_risks = risk_data.get(category, [])
                if category_risks:
                    avg_score = sum(self._risk_to_score(risk.get("impact", "medium")) for risk in category_risks) / len(category_risks)
                    risk_scores.append(avg_score)
            
            overall_score = sum(risk_scores) / len(risk_scores) if risk_scores else 5.0
            overall_risk_level = self._score_to_risk_level(overall_score)
            
            return RiskAssessment(
                overall_risk_level=overall_risk_level,
                technical_risks=risk_data.get("technical_risks", []),
                commercial_risks=risk_data.get("commercial_risks", []),
                operational_risks=risk_data.get("operational_risks", []),
                legal_risks=risk_data.get("legal_risks", []),
                mitigation_strategies=risk_data.get("mitigation_strategies", []),
                risk_score=overall_score
            )
        except (json.JSONDecodeError, ValueError):
            # Fallback risk assessment
            return RiskAssessment(
                overall_risk_level=RiskLevel.MEDIUM,
                technical_risks=[{"description": "Technical complexity", "impact": "medium", "probability": "medium"}],
                commercial_risks=[{"description": "Commercial terms", "impact": "medium", "probability": "medium"}],
                operational_risks=[{"description": "Delivery timeline", "impact": "medium", "probability": "medium"}],
                legal_risks=[{"description": "Contract terms", "impact": "low", "probability": "low"}],
                mitigation_strategies=[{"strategy": "Detailed technical review", "effectiveness": "high"}],
                risk_score=5.0
            )

    async def _extract_project_insights(self, rfp_content: str) -> ProjectInsights:
        """Extract project insights and characteristics"""
        
        prompt = self.analysis_prompts["project_insights"].format(
            rfp_content=rfp_content[:6000]
        )

        messages = [
            LLMMessage(role="system", content="You are a project management expert analyzing RFP requirements."),
            LLMMessage(role="user", content=prompt)
        ]

        response = await llm_service.generate_response(
            messages=messages,
            max_tokens=1200,
            temperature=0.3
        )

        try:
            insights_data = json.loads(response)
            
            return ProjectInsights(
                project_complexity=insights_data.get("project_complexity", "medium"),
                estimated_duration_months=insights_data.get("estimated_duration_months"),
                estimated_cost_range=insights_data.get("estimated_cost_range"),
                technology_stack=insights_data.get("technology_stack", []),
                required_team_size=insights_data.get("required_team_size"),
                key_success_factors=insights_data.get("key_success_factors", []),
                competitive_advantages=insights_data.get("competitive_advantages", []),
                potential_challenges=insights_data.get("potential_challenges", [])
            )
        except (json.JSONDecodeError, ValueError):
            # Fallback insights
            return ProjectInsights(
                project_complexity="medium",
                estimated_duration_months=6,
                estimated_cost_range={"min": 100000, "max": 500000},
                technology_stack=["Modern Web Technologies"],
                required_team_size=5,
                key_success_factors=["Clear requirements", "Stakeholder engagement"],
                competitive_advantages=["Technical expertise", "Track record"],
                potential_challenges=["Timeline constraints", "Resource allocation"]
            )

    async def _generate_kpi_dashboard(
        self,
        strategic_analysis: Dict[str, Any],
        risk_assessment: RiskAssessment,
        project_insights: ProjectInsights
    ) -> Dict[str, Any]:
        """Generate KPI dashboard data"""
        
        return {
            "strategic_score": self._calculate_strategic_score(strategic_analysis),
            "risk_score": risk_assessment.risk_score,
            "complexity_score": self._calculate_complexity_score(project_insights),
            "win_probability": strategic_analysis.get("win_probability", 0.5),
            "financial_attractiveness": strategic_analysis.get("financial_score", 0.6),
            "resource_requirements": {
                "team_size": project_insights.required_team_size or 5,
                "duration_months": project_insights.estimated_duration_months or 6,
                "technology_complexity": project_insights.project_complexity
            },
            "key_metrics": {
                "alignment_score": strategic_analysis.get("alignment_score", 0.7),
                "competitive_position": strategic_analysis.get("competitive_score", 0.6),
                "delivery_confidence": 1.0 - (risk_assessment.risk_score / 10.0)
            },
            "risk_breakdown": {
                "technical": len(risk_assessment.technical_risks),
                "commercial": len(risk_assessment.commercial_risks),
                "operational": len(risk_assessment.operational_risks),
                "legal": len(risk_assessment.legal_risks)
            }
        }

    def _risk_to_score(self, impact: str) -> float:
        """Convert risk impact to numeric score"""
        mapping = {"low": 2.0, "medium": 5.0, "high": 8.0, "critical": 10.0}
        return mapping.get(impact.lower(), 5.0)

    def _score_to_risk_level(self, score: float) -> RiskLevel:
        """Convert numeric score to risk level"""
        if score <= 3.0:
            return RiskLevel.LOW
        elif score <= 6.0:
            return RiskLevel.MEDIUM
        elif score <= 8.5:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL

    def _calculate_strategic_score(self, strategic_analysis: Dict[str, Any]) -> float:
        """Calculate overall strategic score"""
        # Implement scoring logic based on strategic analysis
        factors = [
            strategic_analysis.get("alignment_score", 0.7),
            strategic_analysis.get("competitive_score", 0.6),
            strategic_analysis.get("financial_score", 0.6),
            strategic_analysis.get("capability_match", 0.7)
        ]
        return sum(factors) / len(factors)

    def _calculate_complexity_score(self, project_insights: ProjectInsights) -> float:
        """Calculate project complexity score"""
        complexity_mapping = {"low": 0.2, "medium": 0.5, "high": 0.8, "very_high": 1.0}
        return complexity_mapping.get(project_insights.project_complexity, 0.5)


# Global instance
rfp_analyzer = RFPAnalyzer()