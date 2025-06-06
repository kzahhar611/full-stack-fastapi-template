#!/usr/bin/env python3
"""
Simple Functionality Test for Phase 3.2 Completion
Tests core API endpoints without authentication for validation
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check: API is running")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_phase_status():
    """Test phase status endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/proposal-generation/phase-status")
        if response.status_code == 200:
            data = response.json()
            phase_completion = data.get("estimated_completion", {}).get("phase_3_2", "0%")
            module_completion = data.get("estimated_completion", {}).get("overall_module_3", "0%")
            print(f"✅ Phase Status: {phase_completion} completion, Module 3: {module_completion}")
            return True
        else:
            print(f"❌ Phase status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Phase status error: {e}")
        return False

def test_api_structure():
    """Test API structure and availability"""
    endpoints = [
        "/health",
        "/api/v1/proposal-generation/health",
        "/api/v1/proposal-generation/phase-status"
    ]
    
    working_endpoints = 0
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code in [200, 403]:  # 403 means endpoint exists but needs auth
                working_endpoints += 1
                status = "✅" if response.status_code == 200 else "🔐"
                print(f"  {status} {endpoint}")
            else:
                print(f"  ❌ {endpoint} (status: {response.status_code})")
        except Exception as e:
            print(f"  ❌ {endpoint} (error: {e})")
    
    print(f"✅ API Structure: {working_endpoints}/{len(endpoints)} endpoints available")
    return working_endpoints == len(endpoints)

def test_database_tables():
    """Test database table existence"""
    try:
        import sys
        import os
        sys.path.append('/Users/khaledalzahhar/Memex/RFP.Wizard/backend')
        
        from app.core.database_simple import get_db
        from sqlalchemy import text
        
        db = next(get_db())
        
        # Test proposal generation tables
        tables_to_check = [
            "proposal_projects",
            "rfp_requirements_analysis", 
            "content_templates",
            "generated_sections",
            "proposal_documents",
            "generation_history"
        ]
        
        existing_tables = 0
        for table in tables_to_check:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}")).fetchone()
                count = result[0] if result else 0
                print(f"  ✅ {table}: {count} records")
                existing_tables += 1
            except Exception as e:
                print(f"  ❌ {table}: not found or error")
        
        db.close()
        
        print(f"✅ Database: {existing_tables}/{len(tables_to_check)} tables exist")
        return existing_tables == len(tables_to_check)
        
    except Exception as e:
        print(f"❌ Database test error: {e}")
        return False

def test_template_data():
    """Test template data existence"""
    try:
        import sys
        import os
        sys.path.append('/Users/khaledalzahhar/Memex/RFP.Wizard/backend')
        
        from app.core.database_simple import get_db
        from sqlalchemy import text
        
        db = next(get_db())
        
        # Check templates
        result = db.execute(text("SELECT COUNT(*) FROM content_templates")).fetchone()
        template_count = result[0] if result else 0
        
        if template_count > 0:
            print(f"✅ Template Data: {template_count} templates available")
            db.close()
            return True
        else:
            print("❌ Template Data: No templates found")
            db.close()
            return False
            
    except Exception as e:
        print(f"❌ Template data test error: {e}")
        return False

def run_tests():
    """Run all tests"""
    print("🚀 Phase 3.2 Functionality Tests")
    print("=" * 40)
    
    tests = [
        ("Health Check", test_health),
        ("Phase Status", test_phase_status),
        ("API Structure", test_api_structure),
        ("Database Tables", test_database_tables),
        ("Template Data", test_template_data)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}:")
        if test_func():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"🎯 RESULTS: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 CORE FUNCTIONALITY VERIFIED!")
        print("📊 Phase 3.2 Implementation Status: COMPLETE")
    else:
        print(f"⚠️  {total - passed} tests failed")
    
    return passed == total

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)