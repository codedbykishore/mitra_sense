# test_mood_api_real.py
import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.models.db_models import User
from datetime import datetime, timezone


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def test_user_data():
    """Test user data for mood testing."""
    return {
        "user_id": "test_mood_user_123",
        "email": "mood_test@example.com",
        "name": "Mood Test User",
        "role": "student",
        "onboarding_completed": True,
        "profile": {
            "name": "Mood Test User",
            "age": "22",
            "region": "Test Region",
            "language_preference": "en-US"
        },
        "privacy_flags": {
            "share_moods": True,
            "share_conversations": True
        },
        "created_at": datetime.now(timezone.utc),
        "last_active": datetime.now(timezone.utc)
    }


@pytest.mark.integration
class TestMoodAPIEndpoints:
    """Integration tests for mood API endpoints."""
    
    @pytest.fixture(autouse=True)
    async def setup_test_user(self, test_user_data):
        """Set up test user in Firestore before each test."""
        from app.services.firestore import FirestoreService
        
        fs = FirestoreService()
        
        # Create test user
        user = User(**test_user_data)
        await fs.create_user(user)
        
        # Store user ID for cleanup
        self.test_user_id = test_user_data["user_id"]
        
        yield
        
        # Cleanup after test
        try:
            await fs.delete_user(self.test_user_id)
            
            # Also clean up any mood data
            moods_ref = fs.db.collection("moods").document(self.test_user_id)
            async for doc in moods_ref.collection("entries").stream():
                await doc.reference.delete()
            
        except Exception as e:
            print(f"Cleanup error: {e}")
    
    def test_update_mood_success(self, client):
        """Test successful mood update via API."""
        # Mock session to simulate logged-in user
        with client as c:
            # Simulate session
            with c.session_transaction() as session:
                session["user_id"] = self.test_user_id
                session["user_email"] = "mood_test@example.com"
            
            # Update mood
            response = c.post(
                f"/api/v1/students/{self.test_user_id}/mood",
                json={
                    "mood": "happy",
                    "intensity": 8,
                    "notes": "Feeling great today!"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["mood_entry"]["mood"] == "happy"
            assert data["mood_entry"]["intensity"] == 8
            assert data["mood_entry"]["notes"] == "Feeling great today!"
    
    def test_get_current_mood_success(self, client):
        """Test getting current mood via API."""
        with client as c:
            # Simulate session
            with c.session_transaction() as session:
                session["user_id"] = self.test_user_id
                session["user_email"] = "mood_test@example.com"
            
            # First, add a mood
            c.post(
                f"/api/v1/students/{self.test_user_id}/mood",
                json={
                    "mood": "anxious",
                    "intensity": 6,
                    "notes": "Bit worried about exams"
                }
            )
            
            # Then get current mood
            response = c.get(f"/api/v1/students/{self.test_user_id}/mood")
            
            assert response.status_code == 200
            data = response.json()
            assert data["mood"] == "anxious"
            assert data["intensity"] == 6
            assert data["notes"] == "Bit worried about exams"
    
    def test_get_current_mood_no_data(self, client):
        """Test getting current mood when no data exists."""
        with client as c:
            # Simulate session
            with c.session_transaction() as session:
                session["user_id"] = self.test_user_id
                session["user_email"] = "mood_test@example.com"
            
            # Get current mood without adding any
            response = c.get(f"/api/v1/students/{self.test_user_id}/mood")
            
            assert response.status_code == 200
            data = response.json()
            # Should return empty response when no mood exists
            assert data.get("mood") is None
    
    def test_update_mood_permission_denied(self, client):
        """Test mood update permission denial for other users."""
        with client as c:
            # Simulate session with different user
            with c.session_transaction() as session:
                session["user_id"] = "other_user_456"
                session["user_email"] = "other@example.com"
            
            # Try to update mood for test user
            response = c.post(
                f"/api/v1/students/{self.test_user_id}/mood",
                json={
                    "mood": "happy",
                    "intensity": 8
                }
            )
            
            assert response.status_code == 403
            data = response.json()
            assert "Students can only update their own mood" in data["detail"]
    
    def test_update_mood_invalid_intensity(self, client):
        """Test mood update with invalid intensity."""
        with client as c:
            # Simulate session
            with c.session_transaction() as session:
                session["user_id"] = self.test_user_id
                session["user_email"] = "mood_test@example.com"
            
            # Try to update mood with invalid intensity
            response = c.post(
                f"/api/v1/students/{self.test_user_id}/mood",
                json={
                    "mood": "happy",
                    "intensity": 15  # Invalid - should be 1-10
                }
            )
            
            assert response.status_code == 400
            data = response.json()
            assert "Mood intensity must be between 1 and 10" in data["detail"]
    
    def test_mood_stream_success(self, client):
        """Test mood stream endpoint."""
        with client as c:
            # Simulate session
            with c.session_transaction() as session:
                session["user_id"] = self.test_user_id
                session["user_email"] = "mood_test@example.com"
            
            # Add a mood first
            c.post(
                f"/api/v1/students/{self.test_user_id}/mood",
                json={
                    "mood": "excited",
                    "intensity": 9
                }
            )
            
            # Get mood stream
            response = c.get("/api/v1/students/mood/stream?limit=10")
            
            assert response.status_code == 200
            data = response.json()
            assert "mood_entries" in data
            assert "total_count" in data
            assert isinstance(data["mood_entries"], list)
    
    def test_mood_analytics_success(self, client):
        """Test mood analytics endpoint."""
        with client as c:
            # Simulate session
            with c.session_transaction() as session:
                session["user_id"] = self.test_user_id
                session["user_email"] = "mood_test@example.com"
            
            # Add some mood data
            moods_to_add = [
                {"mood": "happy", "intensity": 8},
                {"mood": "sad", "intensity": 4},
                {"mood": "anxious", "intensity": 7}
            ]
            
            for mood_data in moods_to_add:
                c.post(
                    f"/api/v1/students/{self.test_user_id}/mood",
                    json=mood_data
                )
            
            # Get analytics
            response = c.get("/api/v1/students/mood/analytics")
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify analytics structure
            expected_keys = [
                "total_students",
                "students_with_mood_sharing",
                "total_mood_entries",
                "recent_mood_entries_24h",
                "mood_distribution",
                "mood_percentages",
                "average_moods_per_student"
            ]
            
            for key in expected_keys:
                assert key in data
    
    def test_unauthenticated_access_denied(self, client):
        """Test that unauthenticated requests are denied."""
        # Try to update mood without session
        response = client.post(
            f"/api/v1/students/{self.test_user_id}/mood",
            json={"mood": "happy"}
        )
        
        assert response.status_code == 401  # Unauthorized
        
        # Try to get mood without session
        response = client.get(f"/api/v1/students/{self.test_user_id}/mood")
        
        assert response.status_code == 401  # Unauthorized
        
        # Try to get stream without session
        response = client.get("/api/v1/students/mood/stream")
        
        assert response.status_code == 401  # Unauthorized
        
        # Try to get analytics without session
        response = client.get("/api/v1/students/mood/analytics")
        
        assert response.status_code == 401  # Unauthorized


@pytest.mark.integration
class TestMoodPrivacyEnforcement:
    """Test privacy enforcement for mood features."""
    
    @pytest.fixture(autouse=True)
    async def setup_privacy_test_users(self):
        """Set up users with different privacy settings."""
        from app.services.firestore import FirestoreService
        
        fs = FirestoreService()
        
        # User with mood sharing enabled
        self.public_user_id = "public_mood_user_123"
        public_user = User(
            user_id=self.public_user_id,
            email="public@example.com",
            name="Public User",
            role="student",
            onboarding_completed=True,
            privacy_flags={"share_moods": True, "share_conversations": True},
            created_at=datetime.now(timezone.utc),
            last_active=datetime.now(timezone.utc)
        )
        await fs.create_user(public_user)
        
        # User with mood sharing disabled
        self.private_user_id = "private_mood_user_456"
        private_user = User(
            user_id=self.private_user_id,
            email="private@example.com",
            name="Private User",
            role="student",
            onboarding_completed=True,
            privacy_flags={"share_moods": False, "share_conversations": True},
            created_at=datetime.now(timezone.utc),
            last_active=datetime.now(timezone.utc)
        )
        await fs.create_user(private_user)
        
        yield
        
        # Cleanup
        try:
            await fs.delete_user(self.public_user_id)
            await fs.delete_user(self.private_user_id)
        except Exception as e:
            print(f"Privacy test cleanup error: {e}")
    
    def test_privacy_mood_access_denied(self, client):
        """Test that private mood data is not accessible to others."""
        with client as c:
            # Login as public user
            with c.session_transaction() as session:
                session["user_id"] = self.public_user_id
                session["user_email"] = "public@example.com"
            
            # Try to access private user's mood
            response = c.get(f"/api/v1/students/{self.private_user_id}/mood")
            
            assert response.status_code == 403
            data = response.json()
            assert "Student has disabled mood sharing" in data["detail"]
    
    def test_privacy_self_access_allowed(self, client):
        """Test that users can access their own private mood data."""
        with client as c:
            # Login as private user
            with c.session_transaction() as session:
                session["user_id"] = self.private_user_id
                session["user_email"] = "private@example.com"
            
            # Should be able to access own mood data even if sharing is disabled
            response = c.get(f"/api/v1/students/{self.private_user_id}/mood")
            
            # Should succeed (even if no data exists)
            assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
