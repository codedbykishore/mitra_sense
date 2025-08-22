
# test_google_speech.py
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.google_speech import SpeechService


@pytest.mark.asyncio
async def test_transcribe_audio_mocked():
    service = SpeechService()

    # Mock speech client recognize method
    fake_response = MagicMock()
    fake_result = MagicMock()
    fake_result.alternatives = [MagicMock(transcript="Hello World", confidence=0.95)]
    fake_response.results = [fake_result]

    with patch.object(service.speech_client, "recognize", return_value=fake_response):
        transcript, confidence = await service.transcribe_audio(b"fake audio", "en")

    assert transcript == "Hello World"
    assert confidence == 0.95


# @pytest.mark.asyncio
# async def test_translate_to_english_mocked():
#     service = SpeechService()
#     fake_result = {"translatedText": "Hello World"}
#
#     with patch.object(service.translate_client, "translate", return_value=fake_result):
#         translated = await service.translate_to_english("Hola", "es")
#
#     assert translated == "Hello World"
