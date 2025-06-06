#!/usr/bin/env python3
"""
Test script for Analytics Backend Integration
Tests all analytics endpoints and verifies functionality
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
LOGIN_DATA = {
    "email": "rfp@kzahhar.com",
    "password": "password123"
}

def test_analytics_integration():
    """Test analytics backend integration"""
    print("🔍 Testing Analytics Backend Integration...")
    print("=" * 50)
    
    # Step 1: Login and get token
    print("1. Authenticating...")
    login_response = requests.post(f"{BASE_URL}/auth/login", json=LOGIN_DATA)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Authentication successful")
    
    # Step 2: Test analytics endpoints
    endpoints_to_test = [
        {
            "name": "Dashboard Analytics (30d)",
            "url": f"{BASE_URL}/analytics/dashboard",
            "params": {"time_range": "30d"}
        },
        {
            "name": "Dashboard Analytics (7d)", 
            "url": f"{BASE_URL}/analytics/dashboard",
            "params": {"time_range": "7d"}
        },
        {
            "name": "Dashboard Analytics (24h)",
            "url": f"{BASE_URL}/analytics/dashboard", 
            "params": {"time_range": "24h"}
        }
    ]
    
    results = {}
    
    for endpoint in endpoints_to_test:
        print(f"\n2. Testing {endpoint['name']}...")
        
        try:
            response = requests.get(
                endpoint["url"], 
                headers=headers,
                params=endpoint.get("params", {})
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    print(f"✅ {endpoint['name']} working")
                    
                    # Verify data structure
                    analytics_data = data.get("data", {})
                    sections = ["ai_usage", "documents", "rfps", "performance"]
                    
                    for section in sections:
                        if section in analytics_data:
                            print(f"   ✓ {section} data present")
                        else:
                            print(f"   ⚠️ {section} data missing")
                    
                    results[endpoint["name"]] = {
                        "status": "success",
                        "time_range": analytics_data.get("time_range"),
                        "ai_requests": analytics_data.get("ai_usage", {}).get("total_requests"),
                        "documents_processed": analytics_data.get("documents", {}).get("total_processed"),
                        "rfp_count": analytics_data.get("rfps", {}).get("total")
                    }
                else:
                    print(f"❌ {endpoint['name']} returned failure")
                    results[endpoint["name"]] = {"status": "failed", "error": "API returned success=false"}
                    
            else:
                print(f"❌ {endpoint['name']} failed: HTTP {response.status_code}")
                print(f"   Response: {response.text[:100]}")
                results[endpoint["name"]] = {"status": "failed", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ {endpoint['name']} error: {str(e)}")
            results[endpoint["name"]] = {"status": "failed", "error": str(e)}
    
    # Step 3: Summary
    print("\n" + "=" * 50)
    print("📊 Analytics Integration Test Results:")
    print("=" * 50)
    
    successful_tests = 0
    total_tests = len(endpoints_to_test)
    
    for test_name, result in results.items():
        status_icon = "✅" if result["status"] == "success" else "❌"
        print(f"{status_icon} {test_name}: {result['status']}")
        
        if result["status"] == "success":
            successful_tests += 1
            print(f"   Time Range: {result.get('time_range', 'N/A')}")
            print(f"   AI Requests: {result.get('ai_requests', 'N/A')}")
            print(f"   Documents: {result.get('documents_processed', 'N/A')}")
        else:
            print(f"   Error: {result.get('error', 'Unknown')}")
    
    success_rate = (successful_tests / total_tests) * 100
    print(f"\n🎯 Success Rate: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate == 100:
        print("🎉 Analytics Backend Integration: FULLY WORKING")
        return True
    elif success_rate >= 50:
        print("⚠️ Analytics Backend Integration: PARTIALLY WORKING")
        return False
    else:
        print("❌ Analytics Backend Integration: FAILING")
        return False

if __name__ == "__main__":
    success = test_analytics_integration()
    sys.exit(0 if success else 1)