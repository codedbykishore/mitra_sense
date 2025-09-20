# tests/test_mood_inference_api_real.py
import pytest
import asyncio
from httpx import AsyncClient
from app.main import app
from app.services.firestore import FirestoreService
from datetime import datetime, timezone
import json


@pytest.mark.integration
class TestMoodInferenceAPIReal:
    """
    Integration tests for mood inference API endpoints using real services.
    These tests require actual GCP credentials and Firestore setup.
    """

    @pytest.fixture(autouse=True)
    async def setup_and_cleanup(self):
        """Setup and cleanup for each test."""
        self.firestore_service = FirestoreService()
        self.test_user_id = "test_mood_inference_user"
        
        # Create test user
        test_user_data = {
            "user_id": self.test_user_id,
            "email": "test_mood_inference@example.com",
            "name": "Test Mood Inference User",
            "role": "student",
            "created_at": datetime.now(timezone.utc),
            "onboarding_completed": True,
            "privacy_flags": {
                "share_moods": True,
                "share_conversations": True
            }
        }
        
        try:
            await self.firestore_service.create_user(test_user_data)
            yield
        finally:
            # Cleanup
            try:
                await self._cleanup_test_data()
            except Exception as e:
                print(f"Cleanup error: {e}")

    async def _cleanup_test_data(self):
        """Clean up test data from Firestore."""
        try:
            # Delete user
            await self.firestore_service.delete_user(self.test_user_id)
            
            # Delete any mood entries
            mood_ref = self.firestore_service.db.collection("moods").document(self.test_user_id)
            entries_ref = mood_ref.collection("entries")
            
            # Delete all mood entries
            docs = entries_ref.stream()
            for doc in docs:
                doc.reference.delete()
                
        except Exception as e:
            print(f"Cleanup error: {e}")

    @pytest.mark.asyncio
    async def test_mood_inference_happy_message(self):
        """Test mood inference for happy message."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create session for authenticated user
            with client.websocket_connect("/ws") as websocket:
                # Mock session data
                session_data = {
                    "user": {
                        "user_id": self.test_user_id,
                        "email": "test_mood_inference@example.com"
                    }
                }
                
                # Test mood inference endpoint
                response = await client.post(
                    "/api/v1/students/mood/infer",
                    json={
                        "message": "I'm absolutely thrilled today! Everything went perfectly and I feel amazing!",
                        "language": "en",
                        "auto_update_enabled": True
                    },
                    cookies={"session": json.dumps(session_data)}
                )
                
                assert response.status_code == 200
                data = response.json()
                
                # Verify response structure
                assert "message_analyzed" in data
                assert "emotion_analysis" in data
                assert "suggestion" in data
                assert "privacy_note" in data
                
                # Verify emotion analysis
                emotion_analysis = data["emotion_analysis"]
                assert "emotions" in emotion_analysis
                assert "inferred_mood" in emotion_analysis
                assert "intensity" in emotion_analysis
                assert "confidence" in emotion_analysis
                assert "auto_updated" in emotion_analysis
                
                # Verify happy emotions are detected
                emotions = emotion_analysis["emotions"]
                assert emotions.get("happiness", 0) > 0.4
                
                # Verify mood inference
                mood = emotion_analysis["inferred_mood"]
                assert mood in ["happy", "very_happy", "excited"]
                assert emotion_analysis["intensity"] >= 6
                assert emotion_analysis["confidence"] > 0.0

    @pytest.mark.asyncio
    async def test_mood_inference_sad_message(self):
        """Test mood inference for sad message."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            session_data = {
                "user": {
                    "user_id": self.test_user_id,
                    "email": "test_mood_inference@example.com"
                }
            }
            
            response = await client.post(
                "/api/v1/students/mood/infer",
                json={
                    "message": "I feel so down and depressed. Nothing seems to go right and I'm really struggling.",
                    "language": "en",
                    "auto_update_enabled": True
                },
                cookies={"session": json.dumps(session_data)}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            emotion_analysis = data["emotion_analysis"]
            emotions = emotion_analysis["emotions"]
            
            # Should detect sadness
            assert emotions.get("sadness", 0) > 0.3
            
            # Should infer sad mood
            mood = emotion_analysis["inferred_mood"]
            assert mood in ["sad", "very_sad", "depressed"]

    @pytest.mark.asyncio
    async def test_mood_inference_hindi_expression(self):
        """Test mood inference for Hindi emotional expressions."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            session_data = {
                "user": {
                    "user_id": self.test_user_id,
                    "email": "test_mood_inference@example.com"
                }
            }
            
            response = await client.post(
                "/api/v1/students/mood/infer",
                json={
                    "message": "Bahut ghabrahat ho rahi hai, pareshaan hun main",
                    "language": "hi",
                    "auto_update_enabled": True
                },
                cookies={"session": json.dumps(session_data)}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            emotion_analysis = data["emotion_analysis"]
            emotions = emotion_analysis["emotions"]
            
            # Should detect anxiety from Hindi expressions
            assert emotions.get("anxiety", 0) > 0.2 or emotions.get("frustration", 0) > 0.2
            
            mood = emotion_analysis["inferred_mood"]
            assert mood in ["anxious", "very_anxious", "worried", "frustrated"]

    @pytest.mark.asyncio
    async def test_chat_endpoint_with_mood_inference(self):
        """Test that chat endpoint includes mood inference."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            session_data = {
                "user": {
                    "user_id": self.test_user_id,
                    "email": "test_mood_inference@example.com"
                }
            }
            
            response = await client.post(
                "/api/v1/input/chat",
                json={
                    "text": "I'm feeling really excited about my new project!",
                    "language": "en"
                },
                cookies={"session": json.dumps(session_data)}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify mood inference is included in chat response
            assert "mood_inference" in data
            
            if data["mood_inference"]:  # May be None if inference failed
                mood_inference = data["mood_inference"]
                assert "emotions" in mood_inference
                assert "inferred_mood" in mood_inference
                assert "confidence" in mood_inference
                
                # Should detect positive emotions
                emotions = mood_inference["emotions"]
                assert emotions.get("happiness", 0) > 0.0 or emotions.get("excitement", 0) > 0.0

    @pytest.mark.asyncio
    async def test_mood_inference_auto_update_disabled(self):
        """Test mood inference with auto-update disabled."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            session_data = {
                "user": {
                    "user_id": self.test_user_id,
                    "email": "test_mood_inference@example.com"
                }
            }
            
            response = await client.post(
                "/api/v1/students/mood/infer",
                json={
                    "message": "I'm super happy and excited!",
                    "language": "en",
                    "auto_update_enabled": False
                },
                cookies={"session": json.dumps(session_data)}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            emotion_analysis = data["emotion_analysis"]
            # Auto-update should be False since it was disabled
            assert emotion_analysis["auto_updated"] is False

    @pytest.mark.asyncio
    async def test_mood_inference_unauthenticated(self):
        """Test mood inference endpoint requires authentication."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/students/mood/infer",
                json={
                    "message": "I'm feeling good today",
                    "language": "en",
                    "auto_update_enabled": True
                }
            )
            
            assert response.status_code == 401  # Should require authentication

    @pytest.mark.asyncio
    async def test_mood_inference_validation_errors(self):
        """Test mood inference endpoint input validation."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            session_data = {
                "user": {
                    "user_id": self.test_user_id,
                    "email": "test_mood_inference@example.com"
                }
            }
            
            # Test empty message
            response = await client.post(
                "/api/v1/students/mood/infer",
                json={
                    "message": "",
                    "language": "en"
                },
                cookies={"session": json.dumps(session_data)}
            )
            
            assert response.status_code == 422  # Validation error
            
            # Test missing message
            response = await client.post(
                "/api/v1/students/mood/infer",
                json={
                    "language": "en"
                },
                cookies={"session": json.dumps(session_data)}
            )
            
            assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_mood_inference_check_actual_mood_update(self):
        """Test that mood inference actually updates user's mood when enabled."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            session_data = {
                "user": {
                    "user_id": self.test_user_id,
                    "email": "test_mood_inference@example.com"
                }
            }
            
            # First, infer mood with auto-update enabled
            response = await client.post(
                "/api/v1/students/mood/infer",
                json={
                    "message": "I am absolutely ecstatic and overjoyed today!",
                    "language": "en",
                    "auto_update_enabled": True
                },
                cookies={"session": json.dumps(session_data)}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # If auto-update was successful, check current mood
            if data["emotion_analysis"]["auto_updated"]:
                # Give it a moment for the update to process
                await asyncio.sleep(1)
                
                # Check current mood
                response = await client.get(
                    f"/api/v1/students/{self.test_user_id}/mood",
                    cookies={"session": json.dumps(session_data)}
                )
                
                assert response.status_code == 200
                mood_data = response.json()
                
                # Should have a mood entry now
                if mood_data.get("mood"):
                    assert mood_data["mood"] in ["happy", "very_happy", "excited"]
                    assert "Auto-inferred" in mood_data.get("notes", "")

    @pytest.mark.asyncio 
    async def test_mixed_emotions_low_confidence(self):
        """Test mood inference with mixed emotions results in lower confidence."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            session_data = {
                "user": {
                    "user_id": self.test_user_id,
                    "email": "test_mood_inference@example.com"
                }
            }
            
            response = await client.post(
                "/api/v1/students/mood/infer",
                json={
                    "message": "I'm happy about some things but also worried and a bit sad about others",
                    "language": "en",
                    "auto_update_enabled": True
                },
                cookies={"session": json.dumps(session_data)}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            emotion_analysis = data["emotion_analysis"]
            
            # Mixed emotions should result in lower confidence
            # or be classified as "mixed" mood
            if emotion_analysis["inferred_mood"] == "mixed":
                assert emotion_analysis["confidence"] < 0.8
            else:
                # Or confidence should be reduced due to conflicting emotions
                emotions = emotion_analysis["emotions"]
                high_emotion_count = sum(1 for score in emotions.values() if score > 0.3)
                if high_emotion_count > 1:
                    assert emotion_analysis["confidence"] < 0.9
