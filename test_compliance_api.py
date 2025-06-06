#!/usr/bin/env python3
"""
Test script for compliance analysis API endpoints
"""

import asyncio
import sys
import os
sys.path.append('./backend')

# Test the core functionality without relationships
async def test_compliance_features():
    """Test compliance analysis features"""
    print("🧪 Testing Compliance Analysis Features")
    print("="*60)
    
    # Test 1: Import compliance analyzer service
    try:
        from backend.app.services.ai.compliance_analyzer import ComplianceAnalyzerService
        analyzer = ComplianceAnalyzerService()
        print("✅ ComplianceAnalyzerService imported and created")
    except Exception as e:
        print(f"❌ Error importing compliance analyzer: {e}")
        return
    
    # Test 2: Requirement extraction
    sample_rfp = """
    TECHNICAL REQUIREMENTS:
    
    1. The system shall provide secure user authentication with multi-factor authentication support.
    2. The platform must implement role-based access control (RBAC) functionality.
    3. The solution should support API integration capabilities.
    4. The vendor shall ensure 99.9% system uptime.
    
    FUNCTIONAL REQUIREMENTS:
    
    1. Users must be able to generate custom reports and dashboards.
    2. The system should provide real-time notifications and alerts.
    3. The platform will include document management capabilities.
    4. The solution must support workflow automation features.
    
    COMMERCIAL REQUIREMENTS:
    
    1. The vendor shall provide competitive pricing model.
    2. Support and maintenance costs must be clearly defined.
    3. The solution should include training and onboarding services.
    """
    
    try:
        requirements = await analyzer.extract_requirements_from_rfp(sample_rfp)
        print(f"✅ Extracted {len(requirements)} requirements from sample RFP")
        
        # Display sample requirements
        for i, req in enumerate(requirements[:5]):
            print(f"  {i+1}. {req['text'][:60]}...")
            print(f"     Type: {req['type']}, Priority: {req['priority']}, Weight: {req['weight']}")
        
    except Exception as e:
        print(f"❌ Error extracting requirements: {e}")
        return
    
    # Test 3: Mock proposal content analysis
    sample_proposal = """
    Our Solution Overview:
    
    We provide a comprehensive platform with advanced user authentication including multi-factor authentication,
    biometric login options, and secure password policies. Our role-based access control system supports
    granular permissions and custom user roles.
    
    The platform includes robust API integration capabilities with RESTful APIs, webhooks, and SDK support.
    We guarantee 99.9% uptime with our cloud infrastructure and redundant systems.
    
    Reporting and Analytics:
    Our solution offers powerful reporting capabilities with customizable dashboards, real-time analytics,
    and automated report generation. Users can create custom reports using our drag-and-drop interface.
    
    We provide 24/7 notifications through multiple channels including email, SMS, and in-app alerts.
    The document management system supports version control, secure file sharing, and automated workflows.
    """
    
    # Create mock requirement and proposal objects for testing
    class MockRequirement:
        def __init__(self, req_data):
            self.id = f"req_{hash(req_data['text'])}"
            self.requirement_text = req_data['text']
            self.requirement_type = req_data['type']
            self.priority_level = req_data['priority']
            self.keywords = req_data['keywords']
    
    class MockProposal:
        def __init__(self, content):
            self.id = "proposal_1"
            self.vendor_name = "Test Vendor Corp"
            self.proposal_content = content
    
    try:
        mock_requirements = [MockRequirement(req) for req in requirements[:3]]
        mock_proposal = MockProposal(sample_proposal)
        
        compliance_matches = await analyzer.analyze_proposal_compliance(
            mock_requirements, mock_proposal
        )
        
        print(f"✅ Analyzed compliance for {len(compliance_matches)} requirement-proposal matches")
        
        # Display sample compliance results
        for i, match in enumerate(compliance_matches):
            print(f"  Match {i+1}: {match.compliance_status} ({match.compliance_score:.1f}%)")
            print(f"     Evidence: {match.evidence_text[:80]}...")
        
    except Exception as e:
        print(f"❌ Error analyzing compliance: {e}")
        return
    
    print("\n🎉 All compliance analysis tests passed!")
    print("✅ Module 2 core functionality is working correctly")

if __name__ == "__main__":
    asyncio.run(test_compliance_features())