#!/usr/bin/env python3
"""
Test script to verify authentication redirects are fixed
Tests that unauthenticated access redirects to /login, not /auth/login
"""

import requests
import sys
from urllib.parse import urlparse

def test_redirect_fix():
    """Test that redirects go to /login instead of /auth/login"""
    print("🔍 Testing Authentication Redirect Fix...")
    print("=" * 50)
    
    BASE_URL = "http://localhost:5173"
    
    # Test pages that should redirect when not authenticated
    protected_pages = [
        "/dashboard",
        "/rfps", 
        "/users",
        "/analytics",
        "/organizations"
    ]
    
    print("1. Testing protected page redirects...")
    
    redirect_results = {}
    
    for page in protected_pages:
        try:
            # Use allow_redirects=False to see the initial redirect
            response = requests.get(f"{BASE_URL}{page}", allow_redirects=False)
            
            if response.status_code in [301, 302, 303, 307, 308]:
                redirect_location = response.headers.get('Location', '')
                redirect_path = urlparse(redirect_location).path
                
                if redirect_path == '/login':
                    print(f"✅ {page} → /login (CORRECT)")
                    redirect_results[page] = "correct"
                elif '/auth/login' in redirect_path:
                    print(f"❌ {page} → {redirect_path} (STILL WRONG)")
                    redirect_results[page] = "wrong"
                else:
                    print(f"⚠️ {page} → {redirect_path} (UNEXPECTED)")
                    redirect_results[page] = "unexpected"
            else:
                print(f"⚠️ {page} → HTTP {response.status_code} (NO REDIRECT)")
                redirect_results[page] = "no_redirect"
                
        except Exception as e:
            print(f"❌ {page} → ERROR: {str(e)}")
            redirect_results[page] = "error"
    
    print("\n2. Testing login page accessibility...")
    
    try:
        login_response = requests.get(f"{BASE_URL}/login")
        if login_response.status_code == 200:
            print("✅ /login page loads correctly")
            login_accessible = True
        else:
            print(f"❌ /login page returns HTTP {login_response.status_code}")
            login_accessible = False
    except Exception as e:
        print(f"❌ /login page error: {str(e)}")
        login_accessible = False
    
    print("\n" + "=" * 50)
    print("📊 Redirect Fix Test Results:")
    print("=" * 50)
    
    correct_redirects = sum(1 for result in redirect_results.values() if result == "correct")
    total_tests = len(protected_pages)
    success_rate = (correct_redirects / total_tests) * 100 if total_tests > 0 else 0
    
    for page, result in redirect_results.items():
        if result == "correct":
            print(f"✅ {page}: Redirects to /login")
        elif result == "wrong":
            print(f"❌ {page}: Still redirects to /auth/login")
        else:
            print(f"⚠️ {page}: {result}")
    
    print(f"\n🎯 Success Rate: {correct_redirects}/{total_tests} ({success_rate:.1f}%)")
    print(f"🔐 Login Page: {'✅ Accessible' if login_accessible else '❌ Not Accessible'}")
    
    if success_rate == 100 and login_accessible:
        print("🎉 Authentication Redirect Fix: SUCCESSFUL")
        return True
    else:
        print("❌ Authentication Redirect Fix: NEEDS MORE WORK")
        return False

if __name__ == "__main__":
    success = test_redirect_fix()
    sys.exit(0 if success else 1)