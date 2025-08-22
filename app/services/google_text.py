import asyncio
from pathlib import Path
from google.cloud import texttospeech
from google.api_core.exceptions import GoogleAPIError


class TTSService:
    def __init__(self):
        self.tts_client = texttospeech.TextToSpeechClient()

    async def synthesize(
        self, text: str, language: str = "hi-IN", tone: str = "calm"
    ) -> bytes:
        """
        Convert text to speech using Google Cloud TTS.

        Args:
            text (str): The input text to synthesize.
            language (str): Target language code ("hi-IN" for Hindi, "en-US" for English).
            tone (str): Speaking style ("calm", "empathetic", or "default").

        Returns:
            bytes: The synthesized audio content in MP3 format.
        """

        # Pick default voices for Hindi & English
        default_voices = {"hi-IN": "hi-IN-Neural2-A", "en-US": "en-US-Neural2-C"}

        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=language,
            name=default_voices.get(language, "en-US-Neural2-C"),  # fallback to English
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.9 if tone == "calm" else 1.0,
            pitch=-2.0 if tone == "empathetic" else 0.0,
        )

        try:
            response = await asyncio.to_thread(
                self.tts_client.synthesize_speech,
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config,
            )
            return response.audio_content
        except GoogleAPIError as e:
            raise RuntimeError(f"TTS failed for {language}: {e}")
