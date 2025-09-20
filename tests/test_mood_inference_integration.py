# tests/test_mood_inference_integration.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json
from app.services.emotion_analysis import EmotionAnalysisService


@pytest.mark.asyncio
class TestMoodInferenceIntegration:
    """Integration tests for mood inference functionality."""

    async def test_emotion_analysis_with_real_gemini_mocked(self):
        """Test emotion analysis with mocked Gemini response."""
        service = EmotionAnalysisService()
        
        # Mock the Gemini response
        with patch.object(service.gemini_service, 'process_cultural_conversation') as mock_gemini:
            mock_response = {
                "response": '{"happiness": 0.9, "sadness": 0.0, "anxiety": 0.0, "anger": 0.0, "fear": 0.0, "neutral": 0.1, "excitement": 0.8, "frustration": 0.0}'
            }
            mock_gemini.return_value = mock_response
            
            # Test emotion analysis
            result = await service.analyze_text_emotion(
                "I'm absolutely thrilled and overjoyed today!", "en"
            )
            
            assert isinstance(result, dict)
            assert result["happiness"] > 0.8
            assert result["excitement"] > 0.7
            assert result["sadness"] < 0.1

    async def test_mood_inference_from_happy_text(self):
        """Test complete mood inference flow for happy text."""
        service = EmotionAnalysisService()
        
        with patch.object(service.gemini_service, 'process_cultural_conversation') as mock_gemini:
            mock_response = {
                "response": '{"happiness": 0.9, "sadness": 0.0, "anxiety": 0.0, "anger": 0.0, "fear": 0.0, "neutral": 0.1, "excitement": 0.8, "frustration": 0.0}'
            }
            mock_gemini.return_value = mock_response
            
            with patch.object(service, 'should_auto_update_mood') as mock_should_update:
                with patch.object(service.mood_service, 'update_mood') as mock_update:
                    mock_should_update.return_value = True
                    mock_update.return_value = {"success": True}
                    
                    # Test full message processing
                    result = await service.process_message_for_mood_inference(
                        user_id="test_user",
                        message_text="I am absolutely ecstatic and overjoyed today!",
                        language="en"
                    )
                    
                    assert result is not None
                    assert result["inferred_mood"] in ["very_happy", "happy", "excited"]
                    assert result["confidence"] > 0.7
                    assert result["auto_updated"] is True
                    assert "emotions" in result
                    
                    # Verify mood service was called
                    mock_update.assert_called_once()

    async def test_mood_inference_from_sad_text(self):
        """Test mood inference for sad/depressed text."""
        service = EmotionAnalysisService()
        
        with patch.object(service.gemini_service, 'process_cultural_conversation') as mock_gemini:
            mock_response = {
                "response": '{"happiness": 0.0, "sadness": 0.9, "anxiety": 0.3, "anger": 0.0, "fear": 0.1, "neutral": 0.0, "excitement": 0.0, "frustration": 0.1}'
            }
            mock_gemini.return_value = mock_response
            
            with patch.object(service, 'should_auto_update_mood') as mock_should_update:
                mock_should_update.return_value = True
                
                result = await service.process_message_for_mood_inference(
                    user_id="test_user",
                    message_text="I feel so down and depressed, nothing seems to go right",
                    language="en"
                )
                
                assert result is not None
                assert result["inferred_mood"] in ["very_sad", "sad", "depressed"]
                assert result["confidence"] > 0.6
                emotions = result["emotions"]
                assert emotions["sadness"] > 0.7

    async def test_mood_inference_from_hindi_anxious_text(self):
        """Test mood inference for Hindi anxious expressions."""
        service = EmotionAnalysisService()
        
        with patch.object(service.gemini_service, 'process_cultural_conversation') as mock_gemini:
            mock_response = {
                "response": '{"happiness": 0.0, "sadness": 0.2, "anxiety": 0.8, "anger": 0.0, "fear": 0.4, "neutral": 0.0, "excitement": 0.0, "frustration": 0.3}'
            }
            mock_gemini.return_value = mock_response
            
            result = await service.process_message_for_mood_inference(
                user_id="test_user",
                message_text="Bahut ghabrahat ho rahi hai, pareshaan hun main",
                language="hi"
            )
            
            assert result is not None
            assert result["inferred_mood"] in ["very_anxious", "anxious", "worried"]
            emotions = result["emotions"]
            assert emotions["anxiety"] > 0.6

    async def test_mood_inference_low_confidence_no_update(self):
        """Test that low confidence emotions don't trigger auto-update."""
        service = EmotionAnalysisService()
        
        with patch.object(service.gemini_service, 'process_cultural_conversation') as mock_gemini:
            # Mock low confidence emotions
            mock_response = {
                "response": '{"happiness": 0.3, "sadness": 0.2, "anxiety": 0.2, "anger": 0.0, "fear": 0.0, "neutral": 0.3, "excitement": 0.0, "frustration": 0.0}'
            }
            mock_gemini.return_value = mock_response
            
            result = await service.process_message_for_mood_inference(
                user_id="test_user",
                message_text="I'm okay, nothing special",
                language="en"
            )
            
            assert result is not None
            assert result["confidence"] < 0.6  # Should be low confidence
            assert result["auto_updated"] is False  # Should not auto-update

    async def test_fallback_emotion_analysis(self):
        """Test fallback emotion analysis when Gemini fails."""
        service = EmotionAnalysisService()
        
        with patch.object(service.gemini_service, 'process_cultural_conversation') as mock_gemini:
            # Simulate Gemini failure
            mock_gemini.side_effect = Exception("Gemini API error")
            
            result = await service.analyze_text_emotion(
                "I'm very happy and excited about this!", "en"
            )
            
            # Should fall back to keyword analysis
            assert isinstance(result, dict)
            assert result["happiness"] > 0.0  # Should detect "happy"
            assert result["excitement"] > 0.0  # Should detect "excited"

    def test_keyword_fallback_hindi_terms(self):
        """Test that fallback analysis recognizes Hindi emotional terms."""
        service = EmotionAnalysisService()
        
        result = service._fallback_emotion_analysis("Bahut ghabrahat ho rahi hai")
        
        assert result["anxiety"] > 0.0  # Should detect 'ghabrahat'
        
        result2 = service._fallback_emotion_analysis("Main bahut khushi mein hun")
        
        assert result2["happiness"] > 0.0  # Should detect 'khushi'

    async def test_privacy_check_integration(self):
        """Test that privacy checks work correctly."""
        service = EmotionAnalysisService()
        
        # Test privacy allowed
        with patch.object(service.privacy_service, 'check_flags') as mock_privacy:
            mock_privacy.return_value = {"allowed": True, "exists": True}
            
            result = await service.should_auto_update_mood("user123", 0.8)
            assert result is True
            
        # Test privacy denied
        with patch.object(service.privacy_service, 'check_flags') as mock_privacy:
            mock_privacy.return_value = {"allowed": False, "exists": True}
            
            result = await service.should_auto_update_mood("user123", 0.8)
            assert result is False

    async def test_short_message_skipped(self):
        """Test that very short messages are skipped."""
        service = EmotionAnalysisService()
        
        result = await service.process_message_for_mood_inference(
            user_id="test_user",
            message_text="ok",
            language="en"
        )
        
        assert result is None  # Short messages should be skipped

    def test_mood_inference_rules(self):
        """Test various mood inference rules."""
        service = EmotionAnalysisService()
        
        # Test very happy
        emotions = {"happiness": 0.8, "excitement": 0.6, "sadness": 0.0, "anxiety": 0.0, "anger": 0.0, "fear": 0.0, "neutral": 0.1, "frustration": 0.0}
        mood, intensity, confidence = service.infer_mood_from_emotions(emotions)
        assert mood == "very_happy"
        assert intensity >= 6
        
        # Test very sad
        emotions = {"happiness": 0.0, "excitement": 0.0, "sadness": 0.8, "anxiety": 0.1, "anger": 0.0, "fear": 0.0, "neutral": 0.0, "frustration": 0.0}
        mood, intensity, confidence = service.infer_mood_from_emotions(emotions)
        assert mood == "very_sad"
        
        # Test very anxious
        emotions = {"happiness": 0.0, "excitement": 0.0, "sadness": 0.1, "anxiety": 0.8, "anger": 0.0, "fear": 0.0, "neutral": 0.0, "frustration": 0.0}
        mood, intensity, confidence = service.infer_mood_from_emotions(emotions)
        assert mood == "very_anxious"
        
        # Test mixed emotions
        emotions = {"happiness": 0.5, "excitement": 0.0, "sadness": 0.5, "anxiety": 0.45, "anger": 0.0, "fear": 0.0, "neutral": 0.0, "frustration": 0.0}
        mood, intensity, confidence = service.infer_mood_from_emotions(emotions)
        assert mood == "mixed"
        
        # Test neutral
        emotions = {"happiness": 0.1, "excitement": 0.0, "sadness": 0.1, "anxiety": 0.0, "anger": 0.0, "fear": 0.0, "neutral": 0.8, "frustration": 0.0}
        mood, intensity, confidence = service.infer_mood_from_emotions(emotions)
        assert mood == "neutral"
