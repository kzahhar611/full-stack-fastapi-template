#!/usr/bin/env python3
"""
Test Document Generation Service
"""
import sys
import os
import asyncio
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.document.document_generator import document_generator, DocumentFormat


async def test_document_generation():
    """Test document generation with sample data"""
    print("🧪 Testing Document Generation Service...")
    
    # Sample RFP analysis data
    test_data = {
        "rfp_title": "Test Enterprise Software Development Platform",
        "analysis_id": "test_analysis_20250103_120000",
        "generated_at": datetime.now(),
        "analysis_duration_seconds": 45,
        "analyst_name": "AI System",
        "company_name": "TenderWise AI",
        "contact_email": "test@tenderwise.ai",
        
        "decision": "go",
        "decision_color": "#10b981",
        "confidence_score": 0.85,
        "win_probability": 0.78,
        "primary_justification": "Strong strategic alignment with core capabilities and high win probability.",
        "detailed_reasoning": [
            "Excellent alignment with our AI/ML expertise",
            "Client requirements match our proven capabilities",
            "Competitive landscape favors our positioning"
        ],
        "success_factors": [
            "Proven track record in enterprise AI",
            "Strong technical team",
            "Existing vendor partnerships"
        ],
        "risk_factors": [
            "Aggressive timeline",
            "Integration complexity",
            "Scope creep potential"
        ],
        "conditions": [],
        
        "overall_risk_level": "medium",
        "risk_score": 5.2,
        "technical_risks": [
            {
                "description": "Integration with legacy systems",
                "probability": "medium",
                "impact": "high",
                "mitigation_strategy": "Develop integration layer with fallbacks"
            }
        ],
        "commercial_risks": [
            {
                "description": "Fixed-price contract uncertainties",
                "probability": "medium", 
                "impact": "high",
                "mitigation_strategy": "Negotiate change management provisions"
            }
        ],
        "operational_risks": [
            {
                "description": "Resource availability during peak",
                "probability": "high",
                "impact": "medium",
                "mitigation_strategy": "Cross-train team and identify backups"
            }
        ],
        "legal_risks": [
            {
                "description": "Data privacy compliance",
                "probability": "low",
                "impact": "high", 
                "mitigation_strategy": "Engage legal counsel and implement GDPR"
            }
        ],
        
        "project_complexity": "high",
        "estimated_duration_months": 8,
        "estimated_cost_range": {"min": 450000, "max": 650000},
        "technology_stack": ["React", "Node.js", "Python", "TensorFlow", "AWS", "PostgreSQL"],
        "required_team_size": 12,
        "key_success_factors": [
            "Strong project management",
            "Agile development methodology",
            "Continuous client engagement"
        ],
        "competitive_advantages": [
            "Unique AI/ML expertise",
            "Proven Fortune 500 track record",
            "Strong partnership ecosystem"
        ],
        "potential_challenges": [
            "Complex integration requirements",
            "Tight testing timeline",
            "Managing stakeholder expectations"
        ],
        
        "strategic_score": 0.82,
        "complexity_score": 0.75
    }
    
    try:
        # Test HTML generation
        print("📄 Testing HTML generation...")
        html_doc = await document_generator.generate_document(
            template_name="rfp_analysis_report",
            data=test_data,
            format=DocumentFormat.HTML,
            filename="test_analysis_report.html"
        )
        print(f"✅ HTML generated: {html_doc.filename} ({html_doc.size} bytes)")
        
        # Test PDF generation
        print("📑 Testing PDF generation...")
        pdf_doc = await document_generator.generate_document(
            template_name="rfp_analysis_report",
            data=test_data,
            format=DocumentFormat.PDF,
            filename="test_analysis_report.pdf"
        )
        print(f"✅ PDF generated: {pdf_doc.filename} ({pdf_doc.size} bytes)")
        
        # Test PowerPoint generation
        print("📊 Testing PowerPoint generation...")
        
        # Prepare PowerPoint-specific data
        pptx_data = {
            "title": "RFP Analysis Report",
            "subtitle": "Enterprise Software Development Platform",
            "slides": [
                {
                    "title": "Executive Summary",
                    "content": [
                        "Recommendation: GO",
                        "Confidence: 85%",
                        "Win Probability: 78%",
                        "Strategic Alignment: Strong"
                    ]
                },
                {
                    "title": "Key Success Factors",
                    "content": test_data["success_factors"]
                },
                {
                    "title": "Risk Assessment",
                    "content": [
                        "Overall Risk Level: Medium",
                        "Risk Score: 5.2/10",
                        "Primary Risks: Timeline, Integration",
                        "Mitigation: Phased approach"
                    ]
                },
                {
                    "title": "Project Insights",
                    "content": [
                        f"Duration: {test_data['estimated_duration_months']} months",
                        f"Team Size: {test_data['required_team_size']} people",
                        f"Complexity: {test_data['project_complexity'].title()}",
                        f"Budget: ${test_data['estimated_cost_range']['min']:,} - ${test_data['estimated_cost_range']['max']:,}"
                    ]
                }
            ]
        }
        
        pptx_doc = await document_generator.generate_document(
            template_name="rfp_analysis_report",
            data=pptx_data,
            format=DocumentFormat.PPTX,
            filename="test_analysis_report.pptx"
        )
        print(f"✅ PowerPoint generated: {pptx_doc.filename} ({pptx_doc.size} bytes)")
        
        # Save test files for inspection
        output_dir = "test_outputs"
        os.makedirs(output_dir, exist_ok=True)
        
        files = [html_doc, pdf_doc, pptx_doc]
        for doc in files:
            output_path = os.path.join(output_dir, doc.filename)
            with open(output_path, 'wb') as f:
                f.write(doc.content)
            print(f"💾 Saved: {output_path}")
        
        print(f"\n🎉 All document formats generated successfully!")
        print(f"📁 Files saved in: {os.path.abspath(output_dir)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during document generation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_template_listing():
    """Test template listing functionality"""
    print("\n📋 Testing template listing...")
    
    try:
        templates = document_generator.list_templates()
        print(f"✅ Found {len(templates)} templates:")
        
        for template in templates:
            print(f"  - {template.name} ({template.format.value}): {template.description}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error listing templates: {str(e)}")
        return False


async def main():
    """Main test function"""
    print("🧪 TenderWise AI - Document Generation Service Test")
    print("=" * 60)
    
    success = True
    
    # Test template listing
    success &= await test_template_listing()
    
    # Test document generation
    success &= await test_document_generation()
    
    if success:
        print("\n🎉 All tests passed! Document generation service is ready.")
        return 0
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)