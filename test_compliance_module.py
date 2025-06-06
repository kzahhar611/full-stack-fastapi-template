#!/usr/bin/env python3
"""
Test script for compliance analysis module
"""

import sys
import os
sys.path.append('./backend')

from backend.app.services.ai.compliance_analyzer import ComplianceAnalyzerService

def test_compliance_analyzer():
    """Test the compliance analyzer service"""
    print("🧪 Testing Compliance Analyzer Service")
    print("="*60)
    
    # Create service instance
    analyzer = ComplianceAnalyzerService()
    print("✅ ComplianceAnalyzerService created successfully")
    
    # Test requirement extraction
    sample_rfp = """
    Technical Requirements:
    The system shall provide user authentication functionality.
    The vendor must implement multi-factor authentication.
    The solution should support role-based access control.
    
    Functional Requirements:
    The platform will include dashboard reporting capabilities.
    Users must be able to generate custom reports.
    The system should provide real-time notifications.
    """
    
    print("\n📋 Testing requirement extraction...")
    import asyncio
    
    async def test_extraction():
        requirements = await analyzer.extract_requirements_from_rfp(sample_rfp)
        print(f"✅ Extracted {len(requirements)} requirements")
        
        for i, req in enumerate(requirements[:3]):  # Show first 3
            print(f"  {i+1}. {req['text'][:50]}...")
            print(f"     Type: {req['type']}, Priority: {req['priority']}")
    
    asyncio.run(test_extraction())
    
    print("\n🎉 Compliance Analyzer test completed successfully!")

if __name__ == "__main__":
    test_compliance_analyzer()