# tests/test_onboarding_real.py
"""
Real onboarding tests that hit actual endpoints
These tests require the server to be running and authentication setup
"""
import pytest
import requests
import json


BASE_URL = "http://localhost:8000"


@pytest.mark.integration
class TestOnboardingEndpointsReal:
    """Test onboarding endpoints with real HTTP requests"""

    def test_institutions_list_real(self):
        """Test getting institutions list"""
        try:
            response = requests.get(f"{BASE_URL}/api/v1/users/institutions")
            assert response.status_code == 200
            
            data = response.json()
            assert "institutions" in data
            assert isinstance(data["institutions"], list)
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping real endpoint test")

    def test_onboarding_unauthenticated_real(self):
        """Test onboarding endpoint without authentication"""
        try:
            payload = {
                "role": "student",
                "profile": {
                    "name": "Test Student",
                    "age": "20",
                    "region": "North India",
                    "language_preference": "en-US"
                }
            }
            
            response = requests.post(f"{BASE_URL}/api/v1/users/onboarding", 
                                   json=payload)
            # Should require authentication
            assert response.status_code == 401
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping real endpoint test")

    def test_profile_unauthenticated_real(self):
        """Test profile endpoint without authentication"""
        try:
            response = requests.get(f"{BASE_URL}/api/v1/users/profile")
            # Should require authentication
            assert response.status_code == 401
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping real endpoint test")

    def test_onboarding_validation_real(self):
        """Test onboarding validation with invalid data"""
        try:
            # Invalid role
            payload = {
                "role": "invalid_role",
                "profile": {"name": "Test"}
            }
            
            response = requests.post(f"{BASE_URL}/api/v1/users/onboarding",
                                   json=payload)
            # Should return validation error
            assert response.status_code == 422
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping real endpoint test")


@pytest.mark.integration
class TestInstitutionManagementReal:
    """Test institution management with real requests"""

    def test_institutions_structure_real(self):
        """Test institutions response structure"""
        try:
            response = requests.get(f"{BASE_URL}/api/v1/users/institutions")
            assert response.status_code == 200
            
            data = response.json()
            institutions = data["institutions"]
            
            if institutions:  # If there are institutions
                first_inst = institutions[0]
                required_fields = [
                    "institution_id", "institution_name", 
                    "region", "student_count", "active"
                ]
                for field in required_fields:
                    assert field in first_inst
                    
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping real endpoint test")

    def test_institutions_content_types_real(self):
        """Test institutions field types"""
        try:
            response = requests.get(f"{BASE_URL}/api/v1/users/institutions")
            assert response.status_code == 200
            
            data = response.json()
            institutions = data["institutions"]
            
            if institutions:
                inst = institutions[0]
                assert isinstance(inst["institution_name"], str)
                assert isinstance(inst["region"], str)
                assert isinstance(inst["student_count"], int)
                assert isinstance(inst["active"], bool)
                    
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping real endpoint test")


def main():
    """Run real onboarding tests manually"""
    print("🎯 Testing MITRA Onboarding Endpoints")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/v1/users/institutions", 
                              timeout=5)
    except requests.exceptions.ConnectionError:
        print("❌ Server not running on localhost:8000")
        print("Please start the server with: uvicorn app.main:app --reload")
        return
    
    print("✅ Server is running, testing onboarding endpoints...")
    
    # Test institutions list
    print("\n📍 Testing /api/v1/users/institutions")
    response = requests.get(f"{BASE_URL}/api/v1/users/institutions")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data['institutions'])} institutions")
        if data['institutions']:
            print(f"Sample: {data['institutions'][0]['institution_name']}")
    
    # Test unauthenticated onboarding
    print("\n📍 Testing /api/v1/users/onboarding (unauthenticated)")
    response = requests.post(f"{BASE_URL}/api/v1/users/onboarding", json={
        "role": "student",
        "profile": {"name": "Test Student"}
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test unauthenticated profile
    print("\n📍 Testing /api/v1/users/profile (unauthenticated)")
    response = requests.get(f"{BASE_URL}/api/v1/users/profile")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test invalid onboarding data
    print("\n📍 Testing onboarding validation")
    response = requests.post(f"{BASE_URL}/api/v1/users/onboarding", json={
        "role": "invalid_role",
        "profile": {}
    })
    print(f"Status: {response.status_code}")
    if response.status_code == 422:
        print("✅ Validation working correctly")
    
    print("\n✅ Onboarding endpoint testing completed!")


if __name__ == "__main__":
    main()
