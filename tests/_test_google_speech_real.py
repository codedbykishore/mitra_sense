# tests/test_google_speech_integration.py
import os
import json
import pytest
from unittest.mock import patch, AsyncMock
from pathlib import Path

from app.services.google_speech import SpeechService
from app.services.gemini_ai import GeminiService

# Paths & env checks
CRED_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
AUDIO_REL_PATH = Path(__file__).parent / "audio" / "hindi_audio_fixed.wav"


def _have_credentials():
    return bool(CRED_PATH and Path(CRED_PATH).is_file())


def _have_audio():
    return AUDIO_REL_PATH.exists()


def _get_project_id_from_creds():
    if not _have_credentials():
        return None
    with open(CRED_PATH, "r") as f:
        creds = json.load(f)
    return creds.get("project_id")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_detect_language_integration_skip_if_no_creds_or_audio():
    """Integration: detect_language should return a language code for real audio."""
    if not _have_credentials() or not _have_audio():
        pytest.skip("Skipping integration test: credentials or audio file missing")

    svc = SpeechService()

    with open(AUDIO_REL_PATH, "rb") as f:
        audio_bytes = f.read()

    lang = await svc.detect_language(audio_bytes, sample_rate=16000)
    assert isinstance(lang, str) and len(lang) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_transcribe_audio_integration_skip_if_no_creds_or_audio():
    """Integration: transcribe_audio should return a non-empty transcript and a confidence."""
    if not _have_credentials() or not _have_audio():
        pytest.skip("Skipping integration test: credentials or audio file missing")

    svc = SpeechService()
    with open(AUDIO_REL_PATH, "rb") as f:
        audio_bytes = f.read()

    transcript, confidence = await svc.transcribe_audio(audio_bytes)
    print("Transcript:", transcript)
    print("Confidence:", confidence)

    assert isinstance(transcript, str)
    assert len(transcript) > 0
    assert isinstance(confidence, float)
    assert 0.0 <= confidence <= 1.0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_synthesize_response_integration_skip_if_no_creds():
    """Integration: synthesize_response should return MP3 bytes for a simple text."""
    if not _have_credentials():
        pytest.skip("Skipping TTS integration test: credentials missing")

    svc = SpeechService()

    # Use a simple text in English
    out = await svc.synthesize_response("Hello from MITRA test", "en-US", cultural_tone="empathetic")
    # Expect raw bytes (mp3)
    assert isinstance(out, (bytes, bytearray))
    assert len(out) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_gemini_analyze_integration_skip_if_no_creds():
    """Integration: call GeminiService.analyze directly to verify LLM access."""
    project_id = _get_project_id_from_creds()
    if not project_id:
        pytest.skip("Skipping Gemini integration: project_id missing in credentials")

    svc = GeminiService(project_id=project_id)
    resp = await svc.analyze("Explain the benefits of mindfulness in 1 sentence.")
    # genai response objects vary; check for textual output
    # Common cases: response.text or dict/structured output
    text = getattr(resp, "text", None)
    if not text:
        # try dict-like
        if isinstance(resp, dict):
            # look for possible text keys
            candidate = resp.get("output") or resp.get("content") or resp.get("response")
            assert candidate, "Gemini returned dict but no textual content key found"
        else:
            pytest.fail("Gemini analyze returned unexpected type and no text attribute")
    else:
        assert isinstance(text, str) and len(text) > 0
        print("Gemini text:", text)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_process_voice_pipeline_integration_end_to_end():
    """
    Full integration: STT (real) -> Gemini (real via analyze) -> TTS (real).
    We patch app.services.google_speech.GeminiService.process_cultural_conversation to a wrapper
    that calls the real GeminiService.analyze and returns the expected dict shape:
        {"response": "<generated text>"}
    This lets the pipeline use the real LLM while matching the pipeline's expected key.
    """
    if not _have_credentials() or not _have_audio():
        pytest.skip("Skipping pipeline integration: credentials or audio file missing")

    project_id = _get_project_id_from_creds()
    if not project_id:
        pytest.skip("Skipping pipeline integration: project id missing")

    svc = SpeechService()
    with open(AUDIO_REL_PATH, "rb") as f:
        audio_bytes = f.read()

    # Prepare a real GeminiService to call analyze; we'll wrap its output
    real_gemini = GeminiService(project_id=project_id)

    async def _process_wrapper(prompt_text, options=None):
        # call the real analyze and convert the result to the pipeline format
        resp = await real_gemini.analyze(prompt_text)
        # try to extract text
        text = getattr(resp, "text", None)
        if not text and isinstance(resp, dict):
            text = resp.get("output") or resp.get("content") or resp.get("response")
        return {"response": text or str(resp)}

    # Patch the GeminiService looked up inside google_speech module
    patch_target = "app.services.google_speech.GeminiService.process_cultural_conversation"
    with patch(patch_target, AsyncMock(side_effect=_process_wrapper)):
        result = await svc.process_voice_pipeline(audio_bytes)

    # Basic structure assertions
    assert isinstance(result, dict)
    assert "transcript" in result
    assert "gemini_response" in result
    assert "audio_output" in result
    assert "emotions" in result

    # Check audio bytes present
    assert isinstance(result["audio_output"], (bytes, bytearray))
    assert len(result["audio_output"]) > 0

    # Check transcript non-empty
    assert isinstance(result["transcript"], str)
    assert len(result["transcript"]) > 0

    # Print for manual verification
    print("Transcript:", result["transcript"])
    print("Gemini Response:", result["gemini_response"]["response"])
    print("Emotions:", result["emotions"])

    # Save the audio to a file to listen
    with open("output.mp3", "wb") as f:
        f.write(result["audio_output"])
    print("Audio saved as output.mp3")
