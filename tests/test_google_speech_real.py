import os
import pytest
from google.cloud import speech
from app.services.google_speech import SpeechService
import os

@pytest.mark.asyncio
async def test_transcribe_audio_real():
    # Ensure credentials are set
    assert "GOOGLE_APPLICATION_CREDENTIALS" in os.environ, "Google credentials not set!"

    # Path to test audio
    BASE_DIR = os.path.dirname(__file__)  # directory of this test file
    audio_file = os.path.join(BASE_DIR, "audio", "hindi_audio_fixed.wav")

    assert os.path.exists(audio_file), f"Test audio file not found at {audio_file}!"
    with open(audio_file, "rb") as f:
        audio_data = f.read()
    # Use real SpeechService
    service = SpeechService()
    transcript, confidence = await service.transcribe_audio(audio_data)

    print("\nTranscript:", transcript)
    print("Confidence:", confidence)

    # Basic assertions
    assert isinstance(transcript, str)
    assert len(transcript) > 0, "Transcript should not be empty"
    assert 0.0 <= confidence <= 1.0
