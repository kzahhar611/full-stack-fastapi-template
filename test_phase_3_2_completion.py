#!/usr/bin/env python3
"""
Test Phase 3.2 Completion - AI-Powered Technical Proposal Generation
Tests all new API endpoints and functionality for final 15% completion
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
TEST_EMAIL = "rfp@kzahhar.com"
TEST_PASSWORD = "password123"

class Phase32CompletionTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_project_id = None
        self.test_section_id = None
        self.test_document_id = None
        
    def authenticate(self) -> bool:
        """Authenticate with the API"""
        try:
            response = self.session.post(f"{BASE_URL}/api/v1/auth/login", data={
                "username": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                print("✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def test_phase_status(self) -> bool:
        """Test phase status endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/api/v1/proposal-generation/phase-status")
            
            if response.status_code == 200:
                data = response.json()
                phase_completion = data.get("estimated_completion", {}).get("phase_3_2", "0%")
                print(f"✅ Phase Status: {phase_completion} completion")
                return True
            else:
                print(f"❌ Phase status failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Phase status error: {e}")
            return False
    
    def test_project_creation(self) -> bool:
        """Test project creation"""
        try:
            response = self.session.post(f"{BASE_URL}/api/v1/proposal-generation/projects", data={
                "name": "Test Phase 3.2 Project",
                "client_name": "Test Client Corp",
                "description": "Testing final completion features",
                "deadline": "2025-07-01",
                "priority": "high"
            })
            
            if response.status_code == 201:
                data = response.json()
                self.test_project_id = data.get("project_id")
                print(f"✅ Project created: {self.test_project_id}")
                return True
            else:
                print(f"❌ Project creation failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Project creation error: {e}")
            return False
    
    def test_content_generation(self) -> bool:
        """Test content generation"""
        if not self.test_project_id:
            print("❌ No test project available")
            return False
            
        try:
            response = self.session.post(
                f"{BASE_URL}/api/v1/proposal-generation/projects/{self.test_project_id}/generate-content",
                data={
                    "content_type": "technical_approach",
                    "requirement_ids": "1,2",
                    "template_id": 1
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Content generation started: {data.get('message')}")
                return True
            else:
                print(f"❌ Content generation failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Content generation error: {e}")
            return False
    
    def test_get_project_sections(self) -> bool:
        """Test getting project sections"""
        if not self.test_project_id:
            print("❌ No test project available")
            return False
            
        try:
            # Wait a bit for content generation
            time.sleep(2)
            
            response = self.session.get(
                f"{BASE_URL}/api/v1/proposal-generation/projects/{self.test_project_id}/sections"
            )
            
            if response.status_code == 200:
                data = response.json()
                sections = data.get("sections", [])
                print(f"✅ Retrieved {len(sections)} sections")
                
                # Store first section ID for testing
                if sections:
                    self.test_section_id = sections[0]["id"]
                    
                return True
            else:
                print(f"❌ Get sections failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Get sections error: {e}")
            return False
    
    def test_section_editing(self) -> bool:
        """Test section editing"""
        if not self.test_project_id or not self.test_section_id:
            print("❌ No test project or section available")
            return False
            
        try:
            response = self.session.put(
                f"{BASE_URL}/api/v1/proposal-generation/projects/{self.test_project_id}/sections/{self.test_section_id}",
                data={
                    "section_title": "Updated Technical Approach",
                    "content": "This is updated content with rich text editing capabilities. The system now supports version control and collaborative editing."
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Section updated: {data.get('message')}")
                return True
            else:
                print(f"❌ Section editing failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Section editing error: {e}")
            return False
    
    def test_document_assembly(self) -> bool:
        """Test document assembly"""
        if not self.test_project_id or not self.test_section_id:
            print("❌ No test project or section available")
            return False
            
        try:
            response = self.session.post(
                f"{BASE_URL}/api/v1/proposal-generation/projects/{self.test_project_id}/assemble-document",
                data={
                    "document_title": "Complete Test Proposal",
                    "section_ids": self.test_section_id,
                    "export_format": "html"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.test_document_id = data.get("document_id")
                print(f"✅ Document assembled: {data.get('message')}")
                return True
            else:
                print(f"❌ Document assembly failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Document assembly error: {e}")
            return False
    
    def test_document_export(self) -> bool:
        """Test document export"""
        if not self.test_project_id or not self.test_document_id:
            print("❌ No test project or document available")
            return False
            
        try:
            response = self.session.get(
                f"{BASE_URL}/api/v1/proposal-generation/projects/{self.test_project_id}/documents/{self.test_document_id}/download"
            )
            
            if response.status_code == 200:
                # Check if it's HTML content
                if "<!DOCTYPE html>" in response.text:
                    print(f"✅ Document export successful (HTML format)")
                    return True
                else:
                    print(f"✅ Document export successful (JSON format)")
                    return True
            else:
                print(f"❌ Document export failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Document export error: {e}")
            return False
    
    def test_get_project_documents(self) -> bool:
        """Test getting project documents"""
        if not self.test_project_id:
            print("❌ No test project available")
            return False
            
        try:
            response = self.session.get(
                f"{BASE_URL}/api/v1/proposal-generation/projects/{self.test_project_id}/documents"
            )
            
            if response.status_code == 200:
                data = response.json()
                documents = data.get("documents", [])
                print(f"✅ Retrieved {len(documents)} documents")
                return True
            else:
                print(f"❌ Get documents failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Get documents error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all completion tests"""
        print("🚀 Starting Phase 3.2 Completion Tests")
        print("=" * 50)
        
        tests = [
            ("Authentication", self.authenticate),
            ("Phase Status", self.test_phase_status),
            ("Project Creation", self.test_project_creation),
            ("Content Generation", self.test_content_generation),
            ("Get Project Sections", self.test_get_project_sections),
            ("Section Editing", self.test_section_editing),
            ("Document Assembly", self.test_document_assembly),
            ("Document Export", self.test_document_export),
            ("Get Project Documents", self.test_get_project_documents)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 Testing: {test_name}")
            if test_func():
                passed += 1
            else:
                print(f"   Test failed for {test_name}")
        
        print("\n" + "=" * 50)
        print(f"🎯 RESULTS: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED - Phase 3.2 is 100% COMPLETE!")
        else:
            print(f"⚠️  {total - passed} tests failed - Additional work needed")
        
        return passed == total

if __name__ == "__main__":
    tester = Phase32CompletionTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)