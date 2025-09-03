# tests/test_gemini_language.py
import pytest
import asyncio
from unittest.mock import MagicMock, patch
import os

from app.services.gemini_ai import GeminiService


@pytest.fixture
def patched_gemini_service():
    """Patch GeminiService so it won't need real Google Cloud setup."""
    with patch("app.services.gemini_ai.GeminiService.__init__", return_value=None):
        service = GeminiService()
        # manually set project_id if needed
        service.project_id = os.getenv("GOOGLE_PROJECT_ID", "test-project")
        # Patch detect_language and get_language_name for deterministic behavior
        service.detect_language = MagicMock(
            side_effect=lambda text: {
                "Hello, how are you?": ("en", 0.99),
                "नमस्ते, आप कैसे हैं?": ("hi", 0.98),
                "Hola, ¿cómo estás?": ("es", 0.97),
                "Bonjour, comment ça va?": ("fr", 0.96),
            }[text]
        )
        service.get_language_name = MagicMock(
            side_effect=lambda code: {
                "en": "English",
                "hi": "Hindi",
                "es": "Spanish",
                "fr": "French",
            }[code]
        )
        yield service


@pytest.mark.asyncio
async def test_language_detection(patched_gemini_service):
    service = patched_gemini_service

    test_cases = [
        ("Hello, how are you?", "English"),
        ("नमस्ते, आप कैसे हैं?", "Hindi"),
        ("Hola, ¿cómo estás?", "Spanish"),
        ("Bonjour, comment ça va?", "French"),
    ]

    for text, expected_lang in test_cases:
        lang_code, confidence = service.detect_language(text)
        lang_name = service.get_language_name(lang_code)

        assert lang_name == expected_lang
        assert 0.0 <= confidence <= 1.0
