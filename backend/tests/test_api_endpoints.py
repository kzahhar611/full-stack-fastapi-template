"""
Test suite for TenderWise AI API endpoints
Release 3: Complete Backend Testing
"""
import pytest
import requests
import json
from datetime import datetime, timedelta


class TestAPI:
    """API test suite"""
    
    BASE_URL = "http://localhost:8000"
    
    def setup_method(self):
        """Setup for each test"""
        # Login and get access token
        login_response = requests.post(
            f"{self.BASE_URL}/api/v1/auth/login",
            json={"email": "rfp@kzahhar.com", "password": "password123"}
        )
        assert login_response.status_code == 200
        
        token_data = login_response.json()
        self.access_token = token_data["access_token"]
        self.headers = {"Authorization": f"Bearer {self.access_token}"}
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = requests.get(f"{self.BASE_URL}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
    
    def test_authentication_flow(self):
        """Test authentication endpoints"""
        # Test login
        login_response = requests.post(
            f"{self.BASE_URL}/api/v1/auth/login",
            json={"email": "rfp@kzahhar.com", "password": "password123"}
        )
        assert login_response.status_code == 200
        
        token_data = login_response.json()
        assert "access_token" in token_data
        assert "refresh_token" in token_data
        assert token_data["token_type"] == "bearer"
        
        # Test /me endpoint
        me_response = requests.get(
            f"{self.BASE_URL}/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token_data['access_token']}"}
        )
        assert me_response.status_code == 200
        
        user_data = me_response.json()
        assert user_data["email"] == "rfp@kzahhar.com"
        assert user_data["role"] == "super_admin"
        assert user_data["is_active"] is True
    
    def test_organizations_crud(self):
        """Test organization CRUD operations"""
        # List organizations
        list_response = requests.get(
            f"{self.BASE_URL}/api/v1/organizations/",
            headers=self.headers
        )
        assert list_response.status_code == 200
        
        orgs = list_response.json()
        assert len(orgs) >= 1
        assert orgs[0]["name"] == "TenderWise AI"
        assert orgs[0]["organization_type"] == "technology"
        
        # Get specific organization
        org_id = orgs[0]["id"]
        get_response = requests.get(
            f"{self.BASE_URL}/api/v1/organizations/{org_id}",
            headers=self.headers
        )
        assert get_response.status_code == 200
        
        org_data = get_response.json()
        assert org_data["id"] == org_id
        assert org_data["name"] == "TenderWise AI"
        assert "uuid" in org_data
    
    def test_rfp_lifecycle(self):
        """Test complete RFP lifecycle"""
        # Create RFP
        today = datetime.now().strftime("%Y-%m-%d")
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        rfp_data = {
            "title": "Test RFP for API Testing",
            "description": "Automated test RFP creation",
            "rfp_number": f"RFP-TEST-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "rfp_type": "consulting",
            "issue_date": today,
            "submission_deadline": future_date,
            "estimated_budget": 50000.00,
            "currency": "SAR",
            "organization_id": 1
        }
        
        create_response = requests.post(
            f"{self.BASE_URL}/api/v1/rfps/",
            json=rfp_data,
            headers=self.headers
        )
        assert create_response.status_code == 200
        
        created_rfp = create_response.json()
        assert created_rfp["title"] == rfp_data["title"]
        assert created_rfp["rfp_type"] == "consulting"
        assert created_rfp["status"] == "draft"
        assert created_rfp["estimated_budget"] == 50000.0
        
        rfp_id = created_rfp["id"]
        
        # List RFPs
        list_response = requests.get(
            f"{self.BASE_URL}/api/v1/rfps/",
            headers=self.headers
        )
        assert list_response.status_code == 200
        
        rfps = list_response.json()
        assert len(rfps) >= 1
        
        # Find our created RFP
        test_rfp = next((rfp for rfp in rfps if rfp["id"] == rfp_id), None)
        assert test_rfp is not None
        assert test_rfp["title"] == rfp_data["title"]
        
        # Get specific RFP
        get_response = requests.get(
            f"{self.BASE_URL}/api/v1/rfps/{rfp_id}",
            headers=self.headers
        )
        assert get_response.status_code == 200
        
        rfp_details = get_response.json()
        assert rfp_details["id"] == rfp_id
        assert rfp_details["organization"]["name"] == "TenderWise AI"
        assert rfp_details["creator"]["email"] == "rfp@kzahhar.com"
        
        # Update RFP
        update_data = {
            "title": "Updated Test RFP Title",
            "estimated_budget": 75000.00
        }
        
        update_response = requests.put(
            f"{self.BASE_URL}/api/v1/rfps/{rfp_id}",
            json=update_data,
            headers=self.headers
        )
        assert update_response.status_code == 200
        
        updated_rfp = update_response.json()
        assert updated_rfp["title"] == "Updated Test RFP Title"
        assert updated_rfp["estimated_budget"] == 75000.0
        
    def test_rfp_statistics(self):
        """Test RFP statistics endpoint"""
        stats_response = requests.get(
            f"{self.BASE_URL}/api/v1/rfps/stats/summary",
            headers=self.headers
        )
        assert stats_response.status_code == 200
        
        stats = stats_response.json()
        assert "total_rfps" in stats
        assert "draft_rfps" in stats
        assert "published_rfps" in stats
        assert "closed_rfps" in stats
        assert "average_budget" in stats
        assert stats["total_rfps"] >= 0
    
    def test_error_handling(self):
        """Test error handling"""
        # Test invalid login
        invalid_login = requests.post(
            f"{self.BASE_URL}/api/v1/auth/login",
            json={"email": "invalid@email.com", "password": "wrongpassword"}
        )
        assert invalid_login.status_code == 401
        
        # Test unauthorized access
        unauthorized_response = requests.get(
            f"{self.BASE_URL}/api/v1/organizations/"
        )
        assert unauthorized_response.status_code == 403
        
        # Test invalid RFP creation
        invalid_rfp = requests.post(
            f"{self.BASE_URL}/api/v1/rfps/",
            json={"title": ""},  # Missing required fields
            headers=self.headers
        )
        assert invalid_rfp.status_code == 422
    
    def test_enum_validation(self):
        """Test enum field validation"""
        # Test invalid RFP type
        today = datetime.now().strftime("%Y-%m-%d")
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        invalid_rfp_data = {
            "title": "Test Invalid Enum",
            "rfp_number": "RFP-INVALID-001",
            "rfp_type": "invalid_type",  # Invalid enum value
            "issue_date": today,
            "submission_deadline": future_date,
            "organization_id": 1
        }
        
        invalid_response = requests.post(
            f"{self.BASE_URL}/api/v1/rfps/",
            json=invalid_rfp_data,
            headers=self.headers
        )
        assert invalid_response.status_code == 422
        
        error_data = invalid_response.json()
        # Just check that we got an error response, message format may vary
        assert error_data["success"] is False
        assert "message" in error_data


if __name__ == "__main__":
    # Run tests manually if needed
    test_api = TestAPI()
    
    try:
        test_api.setup_method()
        print("✅ Authentication setup successful")
        
        test_api.test_health_check()
        print("✅ Health check test passed")
        
        test_api.test_authentication_flow()
        print("✅ Authentication flow test passed")
        
        test_api.test_organizations_crud()
        print("✅ Organizations CRUD test passed")
        
        test_api.test_rfp_lifecycle()
        print("✅ RFP lifecycle test passed")
        
        test_api.test_rfp_statistics()
        print("✅ RFP statistics test passed")
        
        test_api.test_error_handling()
        print("✅ Error handling test passed")
        
        test_api.test_enum_validation()
        print("✅ Enum validation test passed")
        
        print("\n🎉 All tests passed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()