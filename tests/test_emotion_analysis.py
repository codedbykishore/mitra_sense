# tests/test_emotion_analysis.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.emotion_analysis import EmotionAnalysisService
import json


@pytest.fixture
def emotion_service():
    """Create EmotionAnalysisService instance for testing."""
    return EmotionAnalysisService()


@pytest.mark.asyncio
class TestEmotionAnalysisService:
    """Test cases for EmotionAnalysisService."""

    async def test_analyze_text_emotion_happy_message(self, emotion_service):
        """Test emotion analysis for happy message."""
        with patch.object(emotion_service.gemini_service, 'process_cultural_conversation') as mock_gemini:
            # Mock Gemini response
            mock_response = {
                "response": '{"happiness": 0.8, "sadness": 0.1, "anxiety": 0.0, "anger": 0.0, "fear": 0.0, "neutral": 0.1, "excitement": 0.6, "frustration": 0.0}'
            }
            mock_gemini.return_value = mock_response
            
            result = await emotion_service.analyze_text_emotion(
                "I'm so happy today! Everything is going great!", "en"
            )
            
            assert isinstance(result, dict)
            assert result["happiness"] > 0.5
            assert result["excitement"] > 0.4
            assert result["sadness"] < 0.2
            assert all(0.0 <= score <= 1.0 for score in result.values())

    async def test_analyze_text_emotion_sad_message(self, emotion_service):
        """Test emotion analysis for sad message."""
        with patch.object(emotion_service.gemini_service, 'process_cultural_conversation') as mock_gemini:
            mock_response = {
                "response": '{"happiness": 0.0, "sadness": 0.9, "anxiety": 0.2, "anger": 0.0, "fear": 0.1, "neutral": 0.0, "excitement": 0.0, "frustration": 0.1}'
            }
            mock_gemini.return_value = mock_response
            
            result = await emotion_service.analyze_text_emotion(
                "I'm feeling very sad and down today", "en"
            )
            
            assert result["sadness"] > 0.7
            assert result["happiness"] < 0.2

    async def test_analyze_text_emotion_hindi_expression(self, emotion_service):
        """Test emotion analysis for Hindi emotional expressions."""
        with patch.object(emotion_service.gemini_service, 'process_cultural_conversation') as mock_gemini:
            mock_response = {
                "response": '{"happiness": 0.1, "sadness": 0.1, "anxiety": 0.8, "anger": 0.0, "fear": 0.3, "neutral": 0.0, "excitement": 0.0, "frustration": 0.2}'
            }
            mock_gemini.return_value = mock_response
            
            result = await emotion_service.analyze_text_emotion(
                "Bahut ghabrahat ho rahi hai, pareshaan hun", "hi"
            )
            
            assert result["anxiety"] > 0.6
            assert result["fear"] > 0.2

    async def test_fallback_emotion_analysis(self, emotion_service):
        """Test fallback emotion analysis when Gemini fails."""
        with patch.object(emotion_service.gemini_service, 'process_cultural_conversation') as mock_gemini:
            # Simulate Gemini failure
            mock_gemini.side_effect = Exception("Gemini API error")
            
            result = await emotion_service.analyze_text_emotion(
                "I'm very happy and excited!", "en"
            )
            
            # Should fall back to keyword analysis
            assert isinstance(result, dict)
            assert "happiness" in result
            assert result["happiness"] > 0.0  # Should detect "happy"

    def test_infer_mood_from_emotions_happy(self, emotion_service):
        """Test mood inference for happy emotions."""
        emotions = {
            "happiness": 0.8,
            "excitement": 0.6,
            "sadness": 0.1,
            "anxiety": 0.0,
            "anger": 0.0,
            "fear": 0.0,
            "neutral": 0.1,
            "frustration": 0.0
        }
        
        mood, intensity, confidence = emotion_service.infer_mood_from_emotions(emotions)
        
        assert mood in ["very_happy", "happy", "excited"]
        assert 6 <= intensity <= 10  # Should be high intensity
        assert confidence > 0.6

    def test_infer_mood_from_emotions_sad(self, emotion_service):
        """Test mood inference for sad emotions."""
        emotions = {
            "happiness": 0.0,
            "excitement": 0.0,
            "sadness": 0.9,
            "anxiety": 0.2,
            "anger": 0.0,
            "fear": 0.1,
            "neutral": 0.0,
            "frustration": 0.0
        }
        
        mood, intensity, confidence = emotion_service.infer_mood_from_emotions(emotions)
        
        assert mood in ["very_sad", "sad", "depressed"]
        assert intensity >= 7  # High sadness should mean high intensity
        assert confidence > 0.7

    def test_infer_mood_from_emotions_anxious(self, emotion_service):
        """Test mood inference for anxious emotions."""
        emotions = {
            "happiness": 0.0,
            "excitement": 0.0,
            "sadness": 0.2,
            "anxiety": 0.8,
            "anger": 0.0,
            "fear": 0.4,
            "neutral": 0.0,
            "frustration": 0.1
        }
        
        mood, intensity, confidence = emotion_service.infer_mood_from_emotions(emotions)
        
        assert mood in ["very_anxious", "anxious", "worried"]
        assert intensity >= 6
        assert confidence > 0.6

    def test_infer_mood_from_emotions_mixed(self, emotion_service):
        """Test mood inference for mixed emotions."""
        emotions = {
            "happiness": 0.5,
            "excitement": 0.0,
            "sadness": 0.5,
            "anxiety": 0.4,
            "anger": 0.0,
            "fear": 0.0,
            "neutral": 0.0,
            "frustration": 0.0
        }
        
        mood, intensity, confidence = emotion_service.infer_mood_from_emotions(emotions)
        
        assert mood == "mixed"
        assert confidence < 0.6  # Mixed emotions should have lower confidence

    def test_infer_mood_from_emotions_neutral(self, emotion_service):
        """Test mood inference for neutral emotions."""
        emotions = {
            "happiness": 0.1,
            "excitement": 0.0,
            "sadness": 0.1,
            "anxiety": 0.0,
            "anger": 0.0,
            "fear": 0.0,
            "neutral": 0.8,
            "frustration": 0.0
        }
        
        mood, intensity, confidence = emotion_service.infer_mood_from_emotions(emotions)
        
        assert mood == "neutral"
        assert intensity <= 6
        assert confidence > 0.5

    @pytest.mark.asyncio
    async def test_should_auto_update_mood_high_confidence(self, emotion_service):
        """Test auto-update decision with high confidence."""
        with patch.object(emotion_service.privacy_service, 'check_access_permission') as mock_privacy:
            mock_privacy.return_value = True
            
            result = await emotion_service.should_auto_update_mood("user123", 0.8)
            
            assert result is True
            mock_privacy.assert_called_once_with("user123", "user123", "moods")

    @pytest.mark.asyncio
    async def test_should_auto_update_mood_low_confidence(self, emotion_service):
        """Test auto-update decision with low confidence."""
        result = await emotion_service.should_auto_update_mood("user123", 0.4)
        assert result is False  # Should not auto-update with low confidence

    @pytest.mark.asyncio
    async def test_should_auto_update_mood_privacy_denied(self, emotion_service):
        """Test auto-update decision when privacy denies access."""
        with patch.object(emotion_service.privacy_service, 'check_access_permission') as mock_privacy:
            mock_privacy.return_value = False
            
            result = await emotion_service.should_auto_update_mood("user123", 0.8)
            
            assert result is False

    @pytest.mark.asyncio
    async def test_process_message_for_mood_inference_success(self, emotion_service):
        """Test full message processing with successful mood inference."""
        with patch.object(emotion_service, 'analyze_text_emotion') as mock_analyze:
            with patch.object(emotion_service, 'should_auto_update_mood') as mock_should_update:
                with patch.object(emotion_service.mood_service, 'update_mood') as mock_update:
                    
                    # Mock responses
                    mock_analyze.return_value = {"happiness": 0.8, "sadness": 0.1, "anxiety": 0.0}
                    mock_should_update.return_value = True
                    mock_update.return_value = {"success": True}
                    
                    result = await emotion_service.process_message_for_mood_inference(
                        user_id="user123",
                        message_text="I'm feeling fantastic today!",
                        language="en"
                    )
                    
                    assert result is not None
                    assert result["auto_updated"] is True
                    assert result["inferred_mood"] in ["very_happy", "happy"]
                    assert result["confidence"] > 0.6
                    assert "emotions" in result
                    assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_process_message_for_mood_inference_short_message(self, emotion_service):
        """Test processing very short messages (should be skipped)."""
        result = await emotion_service.process_message_for_mood_inference(
            user_id="user123",
            message_text="ok",
            language="en"
        )
        
        assert result is None  # Short messages should be skipped

    @pytest.mark.asyncio
    async def test_process_message_for_mood_inference_no_auto_update(self, emotion_service):
        """Test processing with no auto-update."""
        with patch.object(emotion_service, 'analyze_text_emotion') as mock_analyze:
            with patch.object(emotion_service, 'should_auto_update_mood') as mock_should_update:
                
                mock_analyze.return_value = {"happiness": 0.6, "sadness": 0.2, "anxiety": 0.1}
                mock_should_update.return_value = False
                
                result = await emotion_service.process_message_for_mood_inference(
                    user_id="user123",
                    message_text="I'm doing alright today, not bad",
                    language="en"
                )
                
                assert result is not None
                assert result["auto_updated"] is False
                assert "inferred_mood" in result

    def test_fallback_keyword_analysis_hindi_terms(self, emotion_service):
        """Test fallback analysis recognizes Hindi emotional terms."""
        result = emotion_service._fallback_emotion_analysis("Bahut ghabrahat ho rahi hai")
        
        assert result["anxiety"] > 0.0  # Should detect 'ghabrahat'
        
    def test_fallback_keyword_analysis_multiple_emotions(self, emotion_service):
        """Test fallback analysis with multiple emotional keywords."""
        result = emotion_service._fallback_emotion_analysis("I'm happy but also a bit worried and scared")
        
        assert result["happiness"] > 0.0
        assert result["anxiety"] > 0.0
        assert result["fear"] > 0.0
