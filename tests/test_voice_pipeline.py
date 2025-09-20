# tests/test_voice_pipeline.py
"""
Tests for voice processing pipeline endpoints
"""
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from io import BytesIO
from app.main import app

client = TestClient(app)


class TestVoicePipelineMocks:
    """Test voice pipeline with mocked dependencies"""

    @patch('app.routes.voice.GoogleSpeechService')
    @patch('app.routes.voice.GeminiService')
    def test_voice_pipeline_audio_success(self, mock_gemini, mock_speech):
        """Test successful voice pipeline processing"""
        # Mock speech service
        mock_speech_instance = AsyncMock()
        mock_speech_instance.transcribe_audio.return_value = {
            "transcript": "मुझे बहुत परेशानी हो रही है",
            "language": "hi-IN",
            "confidence": 0.95
        }
        mock_speech_instance.analyze_emotion.return_value = {
            "emotion": "stress",
            "confidence": 0.8,
            "stress_level": 0.7
        }
        mock_speech_instance.synthesize_speech.return_value = b"fake_audio_data"
        mock_speech.return_value = mock_speech_instance

        # Mock Gemini service  
        mock_gemini_instance = AsyncMock()
        mock_gemini_instance.process_cultural_conversation.return_value = {
            "response": "मैं समझ सकता हूं कि आप परेशान हैं।",
            "crisis_score": 0.6,
            "suggested_actions": ["Take deep breaths"],
            "cultural_adaptations": {"language": "hi-IN"}
        }
        mock_gemini.return_value = mock_gemini_instance

        # Create mock audio file
        audio_content = b"fake_audio_content"
        audio_file = BytesIO(audio_content)
        
        response = client.post(
            "/api/v1/voice/pipeline/audio",
            files={"audio": ("test.webm", audio_file, "audio/webm")},
            data={"duration": "5.0"}
        )

        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "transcription" in data
        assert "emotion" in data
        assert "aiResponse" in data
        assert "ttsAudio" in data
        
        # Check transcription
        assert data["transcription"]["transcript"] == "मुझे बहुत परेशानी हो रही है"
        assert data["transcription"]["language"] == "hi-IN"
        
        # Check emotion analysis
        assert data["emotion"]["emotion"] == "stress"
        assert data["emotion"]["stress_level"] == 0.7
        
        # Check AI response
        assert "परेशान" in data["aiResponse"]["response"]
        assert data["aiResponse"]["crisis_score"] == 0.6

    @patch('app.routes.voice.GoogleSpeechService')
    def test_voice_pipeline_transcription_failure(self, mock_speech):
        """Test voice pipeline with transcription failure"""
        # Mock speech service failure
        mock_speech_instance = AsyncMock()
        mock_speech_instance.transcribe_audio.side_effect = Exception("STT failed")
        mock_speech.return_value = mock_speech_instance

        audio_content = b"fake_corrupted_audio"
        audio_file = BytesIO(audio_content)
        
        response = client.post(
            "/api/v1/voice/pipeline/audio",
            files={"audio": ("test.webm", audio_file, "audio/webm")},
            data={"duration": "3.0"}
        )

        assert response.status_code == 500
        data = response.json()
        assert "error" in data["detail"].lower()

    def test_voice_pipeline_missing_audio(self):
        """Test voice pipeline without audio file"""
        response = client.post(
            "/api/v1/voice/pipeline/audio",
            data={"duration": "5.0"}
        )

        assert response.status_code == 422  # Validation error

    def test_voice_pipeline_invalid_duration(self):
        """Test voice pipeline with invalid duration"""
        audio_content = b"fake_audio_content"
        audio_file = BytesIO(audio_content)
        
        response = client.post(
            "/api/v1/voice/pipeline/audio",
            files={"audio": ("test.webm", audio_file, "audio/webm")},
            data={"duration": "invalid_duration"}
        )

        assert response.status_code == 422  # Validation error

    @patch('app.routes.voice.GoogleSpeechService')
    @patch('app.routes.voice.GeminiService')
    def test_voice_pipeline_crisis_detection(self, mock_gemini, mock_speech):
        """Test voice pipeline crisis detection"""
        # Mock high crisis score
        mock_speech_instance = AsyncMock()
        mock_speech_instance.transcribe_audio.return_value = {
            "transcript": "I want to hurt myself, life is meaningless",
            "language": "en-US",
            "confidence": 0.98
        }
        mock_speech_instance.analyze_emotion.return_value = {
            "emotion": "severe_distress",
            "confidence": 0.95,
            "stress_level": 0.95
        }
        mock_speech_instance.synthesize_speech.return_value = b"crisis_audio"
        mock_speech.return_value = mock_speech_instance

        mock_gemini_instance = AsyncMock()
        mock_gemini_instance.process_cultural_conversation.return_value = {
            "response": "I'm very concerned about you. Please call Tele MANAS.",
            "crisis_score": 0.9,  # High crisis score
            "suggested_actions": ["Call Tele MANAS 14416", "Seek immediate help"],
            "cultural_adaptations": {"language": "en-US"}
        }
        mock_gemini.return_value = mock_gemini_instance

        audio_content = b"crisis_audio_content"
        audio_file = BytesIO(audio_content)
        
        response = client.post(
            "/api/v1/voice/pipeline/audio",
            files={"audio": ("crisis.webm", audio_file, "audio/webm")},
            data={"duration": "8.0"}
        )

        assert response.status_code == 200
        data = response.json()
        
        # Check crisis indicators
        assert data["aiResponse"]["crisis_score"] >= 0.8
        assert "Tele MANAS" in data["aiResponse"]["response"]
        assert len(data["aiResponse"]["suggested_actions"]) > 0

    @patch('app.routes.voice.GoogleSpeechService')
    @patch('app.routes.voice.GeminiService')
    def test_voice_pipeline_cultural_context(self, mock_gemini, mock_speech):
        """Test voice pipeline with cultural context"""
        # Mock Hindi input with cultural response
        mock_speech_instance = AsyncMock()
        mock_speech_instance.transcribe_audio.return_value = {
            "transcript": "घर में पढ़ाई के लिए दबाव बहुत है",
            "language": "hi-IN",
            "confidence": 0.92
        }
        mock_speech_instance.analyze_emotion.return_value = {
            "emotion": "pressure",
            "confidence": 0.85,
            "stress_level": 0.6
        }
        mock_speech_instance.synthesize_speech.return_value = b"cultural_audio"
        mock_speech.return_value = mock_speech_instance

        mock_gemini_instance = AsyncMock()
        mock_gemini_instance.process_cultural_conversation.return_value = {
            "response": "पारिवारिक दबाव समझ आता है। आप अकेले नहीं हैं।",
            "crisis_score": 0.4,
            "suggested_actions": ["Take breaks", "Talk to family"],
            "cultural_adaptations": {
                "language": "hi-IN",
                "family_context": "respectful"
            }
        }
        mock_gemini.return_value = mock_gemini_instance

        audio_content = b"hindi_audio_content"  
        audio_file = BytesIO(audio_content)
        
        response = client.post(
            "/api/v1/voice/pipeline/audio",
            files={"audio": ("hindi.webm", audio_file, "audio/webm")},
            data={"duration": "6.0"}
        )

        assert response.status_code == 200
        data = response.json()
        
        # Check cultural adaptations
        assert data["transcription"]["language"] == "hi-IN"
        assert "पारिवारिक" in data["aiResponse"]["response"]
        cultural_ads = data["aiResponse"]["cultural_adaptations"]
        assert cultural_ads["language"] == "hi-IN"


class TestVoiceUtilities:
    """Test voice processing utility functions"""

    def test_audio_file_validation(self):
        """Test audio file format validation"""
        # Valid formats
        valid_formats = ["audio/webm", "audio/mp3", "audio/wav", "audio/ogg"]
        
        for format_type in valid_formats:
            audio_file = BytesIO(b"fake_audio")
            response = client.post(
                "/api/v1/voice/pipeline/audio",
                files={"audio": ("test.ext", audio_file, format_type)},
                data={"duration": "5.0"}
            )
            # Should not fail due to format (might fail for other reasons)
            assert response.status_code != 415  # Unsupported Media Type

    @patch('app.routes.voice.GoogleSpeechService')
    def test_empty_audio_handling(self, mock_speech):
        """Test handling of empty audio files"""
        mock_speech_instance = AsyncMock()
        mock_speech_instance.transcribe_audio.return_value = {
            "transcript": "",
            "language": "en-US", 
            "confidence": 0.0
        }
        mock_speech.return_value = mock_speech_instance

        # Empty audio content
        audio_file = BytesIO(b"")
        
        response = client.post(
            "/api/v1/voice/pipeline/audio",
            files={"audio": ("empty.webm", audio_file, "audio/webm")},
            data={"duration": "0.1"}
        )

        # Should handle gracefully
        assert response.status_code in [200, 400, 422]
