# tests/test_auth_real.py
"""
Real authentication tests that hit actual endpoints
These tests require the server to be running and Google OAuth configured
"""
import pytest
import requests
import json


BASE_URL = "http://localhost:8000"


@pytest.mark.integration
class TestAuthEndpointsReal:
    """Test authentication endpoints with real HTTP requests"""

    def test_google_oauth_endpoints_exist_real(self):
        """Test Google OAuth endpoints exist"""
        try:
            # Test Google login redirect
            response = requests.get(f"{BASE_URL}/google/login",
                                    allow_redirects=False)
            # Should redirect to Google OAuth
            assert response.status_code in [302, 307, 308]
            
            # Test OAuth callback endpoint exists
            response = requests.get(f"{BASE_URL}/auth/google/callback")
            # Should return error without proper OAuth flow
            assert response.status_code != 404  # Endpoint exists
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping real endpoint test")

    def test_me_endpoint_unauthenticated_real(self):
        """Test /me endpoint without authentication"""
        try:
            response = requests.get(f"{BASE_URL}/me")
            assert response.status_code == 401
            
            data = response.json()
            assert data["authenticated"] is False
            assert data["user"] is None
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping real endpoint test")

    def test_google_login_redirect_real(self):
        """Test Google OAuth redirect endpoint"""
        try:
            response = requests.get(f"{BASE_URL}/google/login",
                                    allow_redirects=False)
            # Should redirect to Google OAuth
            assert response.status_code in [302, 307, 308]
            
            if "location" in response.headers:
                location = response.headers["location"]
                assert "accounts.google.com" in location
                assert "oauth2" in location
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping real endpoint test")

    def test_logout_endpoint_real(self):
        """Test logout endpoint"""
        try:
            response = requests.get(f"{BASE_URL}/logout")
            assert response.status_code == 200
            
            data = response.json()
            assert data["message"] == "Logged out"
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping real endpoint test")

    def test_auth_callback_endpoint_real(self):
        """Test OAuth callback endpoint (fails without proper OAuth flow)"""
        try:
            response = requests.get(f"{BASE_URL}/auth/google/callback")
            # Should fail without proper OAuth state/code
            assert response.status_code in [400, 401, 422, 500]
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping real endpoint test")


@pytest.mark.integration
class TestAuthFlowReal:
    """Test authentication flow integration"""

    def test_auth_session_flow_real(self):
        """Test complete auth session flow"""
        try:
            session = requests.Session()
            
            # 1. Check unauthenticated state
            response = session.get(f"{BASE_URL}/me")
            assert response.status_code == 401
            
            # 2. Try logout (should work even without session)
            response = session.get(f"{BASE_URL}/logout")
            assert response.status_code == 200
            
            # 3. Check still unauthenticated
            response = session.get(f"{BASE_URL}/me")
            assert response.status_code == 401
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping real endpoint test")

    def test_google_oauth_flow_real(self):
        """Test Google OAuth flow components"""
        try:
            session = requests.Session()
            
            # 1. Check Google login redirect
            response = session.get(f"{BASE_URL}/google/login",
                                   allow_redirects=False)
            if response.status_code in [302, 307, 308]:
                redirect_url = response.headers.get("location", "")
                assert "accounts.google.com" in redirect_url
                assert "oauth2" in redirect_url
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping real endpoint test")


def main():
    """Run real auth tests manually"""
    print("🔐 Testing MITRA Authentication Endpoints")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/me", timeout=5)
    except requests.exceptions.ConnectionError:
        print("❌ Server not running on localhost:8000")
        print("Please start the server with: uvicorn app.main:app --reload")
        return
    
    print("✅ Server is running, testing auth endpoints...")
    
    # Test /me endpoint (unauthenticated)
    print("\n📍 Testing /me (unauthenticated)")
    response = requests.get(f"{BASE_URL}/me")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test Google login redirect
    print("\n📍 Testing /google/login")
    response = requests.get(f"{BASE_URL}/google/login", allow_redirects=False)
    print(f"Status: {response.status_code}")
    if "location" in response.headers:
        print(f"Redirect URL: {response.headers['location'][:100]}...")
    
    # Test logout
    print("\n📍 Testing /logout")
    response = requests.get(f"{BASE_URL}/logout")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test OAuth callback (should fail without proper auth flow)
    print("\n📍 Testing /auth/google/callback (without OAuth flow)")
    response = requests.get(f"{BASE_URL}/auth/google/callback")
    print(f"Status: {response.status_code}")
    if response.status_code != 404:
        try:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except (json.JSONDecodeError, ValueError):
            print(f"Response: {response.text[:200]}...")
    
    print("\n✅ Authentication endpoint testing completed!")


if __name__ == "__main__":
    main()
