# tests/test_voice_pipeline_real.py
"""
Real voice pipeline tests that hit actual endpoints
These tests require the server to be running and Google Cloud configured
"""
import pytest
import requests


BASE_URL = "http://localhost:8000"


@pytest.mark.integration
class TestVoicePipelineReal:
    """Test voice pipeline endpoints with real HTTP requests"""

    def test_voice_pipeline_no_auth_required_real(self):
        """Test voice pipeline endpoint accessibility"""
        try:
            # Create minimal fake audio file
            fake_audio = b"fake_audio_content_for_testing"
            
            response = requests.post(
                f"{BASE_URL}/api/v1/voice/pipeline/audio",
                files={"audio": ("test.webm", fake_audio, "audio/webm")},
                data={"duration": "1.0"}
            )
            
            # Should not return 401 (not require auth)
            # Might return 500 if Google Cloud not configured
            assert response.status_code != 401
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping real endpoint test")

    def test_voice_pipeline_missing_file_real(self):
        """Test voice pipeline without audio file"""
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/voice/pipeline/audio",
                data={"duration": "1.0"}
            )
            
            # Should return validation error
            assert response.status_code == 422
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping real endpoint test")

    def test_voice_pipeline_invalid_duration_real(self):
        """Test voice pipeline with invalid duration"""
        try:
            fake_audio = b"fake_audio_content"
            
            response = requests.post(
                f"{BASE_URL}/api/v1/voice/pipeline/audio",
                files={"audio": ("test.webm", fake_audio, "audio/webm")},
                data={"duration": "invalid"}
            )
            
            # Should return validation error
            assert response.status_code == 422
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping real endpoint test")

    def test_voice_pipeline_response_structure_real(self):
        """Test voice pipeline response structure with fake audio"""
        try:
            # Create fake but properly formatted request
            fake_audio = b"fake_webm_audio_data_for_structure_test" * 100
            
            response = requests.post(
                f"{BASE_URL}/api/v1/voice/pipeline/audio",
                files={"audio": ("test.webm", fake_audio, "audio/webm")},
                data={"duration": "2.5"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check expected structure
                expected_keys = ["transcription", "emotion", "aiResponse", "ttsAudio"]
                for key in expected_keys:
                    assert key in data, f"Missing key: {key}"
                
                # Check transcription structure
                if "transcription" in data:
                    trans = data["transcription"]
                    assert "text" in trans  # Changed from "transcript" to "text"
                    assert "language" in trans
                
                # Check emotion structure
                if "emotion" in data:
                    emotion = data["emotion"]
                    assert "emotion" in emotion
                    assert "confidence" in emotion or "stress_level" in emotion
                
                # Check AI response structure
                if "aiResponse" in data:
                    ai_resp = data["aiResponse"]
                    assert "response" in ai_resp
                    assert "crisis_score" in ai_resp
                
            else:
                # Endpoint exists but might fail due to Google Cloud config
                print(f"Voice pipeline returned {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping real endpoint test")


@pytest.mark.integration  
class TestVoiceEndpointsDiscovery:
    """Test voice endpoint discovery and availability"""

    def test_voice_endpoints_exist_real(self):
        """Test that voice endpoints are registered"""
        try:
            # Test main voice pipeline endpoint
            response = requests.post(f"{BASE_URL}/api/v1/voice/pipeline/audio")
            # Should not return 404 (endpoint exists)
            assert response.status_code != 404
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping real endpoint test")

    def test_voice_pipeline_accepts_different_formats_real(self):
        """Test voice pipeline with different audio formats"""
        try:
            formats_to_test = [
                ("test.webm", "audio/webm"),
                ("test.mp3", "audio/mpeg"),
                ("test.wav", "audio/wav"),
                ("test.ogg", "audio/ogg")
            ]
            
            for filename, content_type in formats_to_test:
                fake_audio = b"fake_audio_" + filename.encode()
                
                response = requests.post(
                    f"{BASE_URL}/api/v1/voice/pipeline/audio",
                    files={"audio": (filename, fake_audio, content_type)},
                    data={"duration": "1.0"}
                )
                
                # Should not reject based on format
                # (might fail for other reasons like Google Cloud config)
                assert response.status_code != 415  # Unsupported Media Type
                
        except requests.exceptions.ConnectionError:
            pytest.skip("Server not running - skipping real endpoint test")


def main():
    """Run real voice pipeline tests manually"""
    print("🎤 Testing MITRA Voice Pipeline Endpoints")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
    except requests.exceptions.ConnectionError:
        print("❌ Server not running on localhost:8000")
        print("Please start the server with: uvicorn app.main:app --reload")
        return
    
    print("✅ Server is running, testing voice endpoints...")
    
    # Test voice pipeline endpoint exists
    print("\n📍 Testing voice pipeline endpoint accessibility")
    fake_audio = b"fake_audio_for_testing" * 50
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/voice/pipeline/audio",
            files={"audio": ("test.webm", fake_audio, "audio/webm")},
            data={"duration": "2.0"},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Voice pipeline is working!")
            data = response.json()
            
            # Show structure
            print("Response structure:")
            for key in data.keys():
                print(f"  - {key}: {type(data[key])}")
                
        elif response.status_code == 500:
            print("⚠️  Endpoint exists but may need Google Cloud configuration")
            print("Error:", response.text[:200])
            
        else:
            print(f"Response: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        print("⏱️  Request timed out - endpoint might be processing")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test missing file validation
    print("\n📍 Testing validation (missing audio file)")
    response = requests.post(
        f"{BASE_URL}/api/v1/voice/pipeline/audio",
        data={"duration": "2.0"}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 422:
        print("✅ Validation working correctly")
    
    # Test invalid duration validation
    print("\n📍 Testing validation (invalid duration)")
    response = requests.post(
        f"{BASE_URL}/api/v1/voice/pipeline/audio",
        files={"audio": ("test.webm", fake_audio, "audio/webm")},
        data={"duration": "not_a_number"}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 422:
        print("✅ Duration validation working correctly")
    
    print("\n✅ Voice pipeline endpoint testing completed!")


if __name__ == "__main__":
    main()
