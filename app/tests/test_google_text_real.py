import os
import pytest
from pathlib import Path
from app.services.google_text import TTSService  # updated class name


@pytest.mark.asyncio
async def test_tts_real_multilingual():
    # Ensure credentials are set
    assert "GOOGLE_APPLICATION_CREDENTIALS" in os.environ, "Google credentials not set!"

    service = TTSService()

    test_cases = [
        ("नमस्ते! यह हिंदी परीक्षण है।", "hi-IN", "hindi_tts_test.mp3"),  # Hindi
        ("Hello! This is an English test.", "en-US", "english_tts_test.mp3"),  # English
    ]

    for text, language, filename in test_cases:
        audio_content = await service.synthesize(text, language=language)

        # Assertions
        assert isinstance(audio_content, (bytes, bytearray)), (
            "Audio content must be bytes"
        )
        assert len(audio_content) > 1000, (
            f"Generated audio is too small for text: {text}"
        )

        # Save output for manual listening
        out_path = Path(__file__).parent / "audio" / filename
        out_path.parent.mkdir(exist_ok=True)
        with open(out_path, "wb") as f:
            f.write(audio_content)

        print(f"\n✅ TTS test audio saved at {out_path.absolute()} for text: {text}")
