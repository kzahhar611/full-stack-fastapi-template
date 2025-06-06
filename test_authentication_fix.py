#!/usr/bin/env python3
"""
Test script to verify authentication fixes
"""
import asyncio
import aiohttp
import json

async def test_authentication():
    """Test the authentication flow"""
    print("🔍 Testing TenderWise AI Authentication Fix...")
    
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Health check
        print("\n1. Testing health endpoint...")
        try:
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    print("✅ Health endpoint working")
                else:
                    print(f"❌ Health endpoint failed: {response.status}")
                    return
        except Exception as e:
            print(f"❌ Health endpoint error: {e}")
            return
        
        # Test 2: Login
        print("\n2. Testing login...")
        login_data = {
            "email": "rfp@kzahhar.com",
            "password": "password123"
        }
        
        try:
            async with session.post(
                f"{base_url}/api/v1/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    login_result = await response.json()
                    token = login_result.get("access_token")
                    print("✅ Login successful")
                    print(f"   Token preview: {token[:50]}...")
                else:
                    print(f"❌ Login failed: {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
                    return
        except Exception as e:
            print(f"❌ Login error: {e}")
            return
        
        # Test 3: Get user profile
        print("\n3. Testing user profile...")
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            async with session.get(f"{base_url}/api/v1/auth/me", headers=headers) as response:
                if response.status == 200:
                    user_data = await response.json()
                    print("✅ User profile retrieved")
                    print(f"   User: {user_data.get('first_name')} {user_data.get('last_name')}")
                    print(f"   Role: {user_data.get('role')}")
                else:
                    print(f"❌ User profile failed: {response.status}")
                    return
        except Exception as e:
            print(f"❌ User profile error: {e}")
            return
        
        # Test 4: Get RFPs
        print("\n4. Testing RFPs endpoint...")
        try:
            async with session.get(f"{base_url}/api/v1/rfps/", headers=headers) as response:
                if response.status == 200:
                    rfps_data = await response.json()
                    print("✅ RFPs retrieved successfully")
                    print(f"   Found {len(rfps_data)} RFPs")
                else:
                    print(f"❌ RFPs failed: {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
                    return
        except Exception as e:
            print(f"❌ RFPs error: {e}")
            return
        
        # Test 5: Create RFP
        print("\n5. Testing RFP creation...")
        rfp_data = {
            "title": "Test RFP - Authentication Fix",
            "description": "Testing RFP creation after authentication fix",
            "rfp_type": "testing",
            "estimated_budget": 1000,
            "currency": "USD",
            "submission_deadline": "2025-07-01",
            "requirements": "Test requirements",
            "is_public": False
        }
        
        try:
            async with session.post(
                f"{base_url}/api/v1/rfps/",
                json=rfp_data,
                headers={**headers, "Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    created_rfp = await response.json()
                    print("✅ RFP created successfully")
                    print(f"   RFP ID: {created_rfp.get('id')}")
                    print(f"   RFP Number: {created_rfp.get('rfp_number')}")
                else:
                    print(f"❌ RFP creation failed: {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
        except Exception as e:
            print(f"❌ RFP creation error: {e}")
        
        # Test 6: Analytics endpoint
        print("\n6. Testing analytics endpoint...")
        try:
            async with session.get(f"{base_url}/api/v1/analytics/dashboard", headers=headers) as response:
                if response.status == 200:
                    analytics_data = await response.json()
                    print("✅ Analytics retrieved successfully")
                    print(f"   Analytics keys: {list(analytics_data.keys())}")
                else:
                    print(f"❌ Analytics failed: {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
        except Exception as e:
            print(f"❌ Analytics error: {e}")
    
    print("\n🎯 Authentication test completed!")
    print("\nNext steps:")
    print("1. Open http://localhost:5173 in your browser")
    print("2. Login with: rfp@kzahhar.com / password123")
    print("3. Test the fixed pages: RFPs, Analytics, Settings, Profile")

if __name__ == "__main__":
    asyncio.run(test_authentication())