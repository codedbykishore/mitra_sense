# google_speech.py - Voice Processing Service for MITRA
import asyncio
import logging
import json
from typing import Optional, Dict, Tuple
from google.cloud import speech, texttospeech, translate_v2 as translate
from google.api_core.exceptions import GoogleAPIError
from app.config import settings  # Import project settings
from app.services.gemini_ai import GeminiService  # For emotion integration if needed
from fastapi import HTTPException

# Setup logging
logger = logging.getLogger(__name__)


class SpeechService:
    def __init__(self, rag_corpus_name: Optional[str] = None):
        try:
            self.speech_client = (
                speech.SpeechClient()
            )  # Automatically fetches the $GOOGLE_APPLICATON_CREDENTIAL
            self.tts_client = (
                texttospeech.TextToSpeechClient()
            )  # Automatically fetches the $GOOGLE_APPLICATON_CREDENTIAL
            self.translate_client = translate.Client()
            self.supported_languages = settings.SUPPORTED_LANGUAGES
            self.rag_corpus_name = rag_corpus_name
            self.gemini_service = GeminiService(rag_corpus_name=self.rag_corpus_name) # Instantiate GeminiService once
            logger.info("Google Speech services initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Speech services: {e}")
            raise

    def _detect_audio_format(self, audio_data: bytes) -> Tuple[speech.RecognitionConfig.AudioEncoding, int]:
        """Detect audio format from header and return appropriate encoding and sample rate."""
        # Check for common audio format headers
        if audio_data.startswith(b'RIFF'):
            # WAV file
            logger.info("Detected WAV format")
            return speech.RecognitionConfig.AudioEncoding.LINEAR16, 16000
        elif audio_data.startswith(b'\x1a\x45\xdf\xa3'):
            # WebM/Matroska container (common from browsers)
            logger.info("Detected WebM format")
            return speech.RecognitionConfig.AudioEncoding.WEBM_OPUS, 48000
        elif audio_data.startswith(b'OggS'):
            # Ogg container
            logger.info("Detected OGG format") 
            return speech.RecognitionConfig.AudioEncoding.OGG_OPUS, 48000
        elif audio_data.startswith(b'fLaC'):
            # FLAC format
            logger.info("Detected FLAC format")
            return speech.RecognitionConfig.AudioEncoding.FLAC, 16000
        else:
            # Default to LINEAR16 for unknown formats
            logger.warning("Unknown audio format, defaulting to LINEAR16")
            return speech.RecognitionConfig.AudioEncoding.LINEAR16, 16000

    # NEW: Language Detection (Missed Function)

    async def detect_language(self, audio_data: bytes, sample_rate: Optional[int] = None) -> str:
        """Automatically detect spoken language from audio."""
        encoding, detected_sample_rate = self._detect_audio_format(audio_data)
        actual_sample_rate = sample_rate or detected_sample_rate
        
        config = speech.RecognitionConfig(
            encoding=encoding,
            sample_rate_hertz=actual_sample_rate,
            language_code=self.supported_languages[0],  # Primary language
            alternative_language_codes=self.supported_languages[
                1:
            ],  # Fallback/alternate
            enable_automatic_punctuation=True,
        )
        audio = speech.RecognitionAudio(content=audio_data)

        try:
            response = await asyncio.to_thread(
                self.speech_client.recognize, config=config, audio=audio
            )
            if response.results:
                transcript = response.results[0].alternatives[0].transcript
                detected_language = (
                    response.results[0].language_code
                    if hasattr(response.results[0], "language_code")
                    else "en"
                )
                return detected_language
            return settings.DEFAULT_LANGUAGE  # fallback
        except GoogleAPIError as e:
            logger.error(f"Language detection failed: {e}")
            raise HTTPException(status_code=500, detail="Language detection error")

    # 1. Speech-to-Text (Multilingual) - Your Core Function
    async def transcribe_audio(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        sample_rate: Optional[int] = None,
    ) -> Tuple[str, float]:
        """Convert multilingual voice to text with confidence score."""
        encoding, detected_sample_rate = self._detect_audio_format(audio_data)
        actual_sample_rate = sample_rate or detected_sample_rate
        
        if not language:
            language = await self.detect_language(
                audio_data, actual_sample_rate
            )  # Auto-detect if not provided

        config = speech.RecognitionConfig(
            encoding=encoding,
            sample_rate_hertz=actual_sample_rate,
            language_code=language,
            enable_automatic_punctuation=True,
            model="latest_long",  # For longer conversations
        )

        audio = speech.RecognitionAudio(content=audio_data)

        try:
            response = await asyncio.to_thread(
                self.speech_client.recognize, config=config, audio=audio
            )
            transcript = ""
            confidence = 0.0

            if response.results and response.results[0].alternatives:
                transcript = " ".join(
                    [
                        result.alternatives[0].transcript
                        for result in response.results
                        if result.alternatives
                    ]
                )
                confidence = response.results[0].alternatives[0].confidence
                return transcript, confidence
            else:
                return "", 0.0
        except GoogleAPIError as e:
            logger.error(f"STT failed: {e}")
            raise HTTPException(status_code=500, detail="Speech recognition error")

    # 2. Synthesize Response - Your Function with Cultural Enhancements
    async def synthesize_response(
        self, text: str, language: str, cultural_tone: str = "empathetic_calm"
    ) -> bytes:
        """Convert Gemini response to culturally-appropriate voice audio."""
        # Map cultural tone to voice parameters (e.g., slower for calm, regional accents)
        voice_map = {
            "en-US": {
                "name": "en-US-Neural2-C",
                "language_code": "en-US",
                "speaking_rate": 0.9,
            },
            "en-IN": {
                "name": "en-IN-Neural2-B",
                "language_code": "en-IN",
                "speaking_rate": 0.9,
            },
            "hi-IN": {
                "name": "hi-IN-Neural2-A",
                "language_code": "hi-IN",
                "speaking_rate": 0.9,
            },
            "default": {
                "name": "en-US-Neural2-C",
                "language_code": "en-US",
                "speaking_rate": 0.9,
            },
        }

        voice_key = language.upper().replace("_", "-")  # normalize language code
        voice_config = voice_map.get(voice_key, voice_map["default"])

        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=voice_config["language_code"], name=voice_config["name"]
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=voice_config["speaking_rate"],
            pitch=-2.0
            if cultural_tone == "empathetic"
            else 0.0,  # Lower pitch for empathy
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
            logger.error(f"TTS failed: {e}")
            raise HTTPException(status_code=500, detail="Speech synthesis error")

    # 3. Detect Emotional Tone - Your Function
    async def detect_emotional_tone(
        self, audio_data: bytes, language: str
    ) -> Dict[str, float]:
        """Analyze emotional state from voice patterns."""
        transcript, _ = await self.transcribe_audio(audio_data, language)

        try:
            # Try Gemini integration
            emotion_prompt = (
                f"Analyze emotional tone from this transcript: '{transcript}'. "
                f'Return ONLY JSON like this: {{"anxiety": 0.0, "sadness": 0.0, "calmness": 0.0, "anger": 0.0}}'
            )

            gemini_response = await self.gemini_service.process_cultural_conversation(
                emotion_prompt, {"analysis_mode": "emotion"}
            )

            raw_text = gemini_response.get("response", "{}")
            logger.debug(f"Gemini raw response: {raw_text}")

            emotions = json.loads(raw_text)  # Proper JSON parsing

            # # Parse Gemini response (implement proper JSON parsing)
            # emotions = gemini_response.get("emotions", {
            #     "anxiety": 0.0,
            #     "sadness": 0.0,
            #     "calmness": 0.0,
            #     "anger": 0.0
            # })

        except Exception as e:
            logger.warning(f"Gemini emotion detection failed, using fallback: {e}")
            # Fallback: basic keyword analysis
            emotions = self._basic_emotion_detection(transcript)

        return emotions

    def _basic_emotion_detection(self, transcript: str) -> Dict[str, float]:
        """Fallback emotion detection using keywords."""
        anxiety_words = ["worried", "scared", "nervous", "anxious", "ghabrahat"]
        sadness_words = ["sad", "depressed", "down", "upset", "dukhi"]

        text_lower = transcript.lower()
        return {
            "anxiety": min(
                1.0, sum(0.3 for word in anxiety_words if word in text_lower)
            ),
            "sadness": min(
                1.0, sum(0.3 for word in sadness_words if word in text_lower)
            ),
            "calmness": 0.5,  # Default neutral
            "anger": 0.0,
        }

    # Full Pipeline Wrapper
    async def process_voice_pipeline(self, audio_data: bytes) -> Dict:
        """End-to-end: Detect lang → STT → Translate → Gemini → TTS → Emotion analysis."""
        logger.info(f"process_voice_pipeline received audio_data. Length: {len(audio_data)} bytes. First 50 bytes: {audio_data[:50]}")
        language = await self.detect_language(audio_data)
        logger.info(f"Detected language: {language}")
        transcript, _ = await self.transcribe_audio(audio_data, language)
        logger.info(f"Transcript: {transcript}")

        # Feed to Gemini (from gemini_ai.py)
        gemini_response = await self.gemini_service.process_cultural_conversation(
            transcript, {"language": language}
        )
        logger.info(f"Gemini response: {gemini_response}")

        # Synthesize audio
        audio_output = await self.synthesize_response(
            gemini_response["response"], language
        )
        logger.info(f"Audio output length: {len(audio_output)} bytes")

        # Detect emotions
        emotions = await self.detect_emotional_tone(audio_data, language)
        logger.info(f"Detected emotions: {emotions}")

        return {
            "transcript": transcript,
            "gemini_response": gemini_response,
            "audio_output": audio_output,  # Bytes for response
            "emotions": emotions,
        }

    # NEW: Audio Validation (Recommended Addition)
    def validate_audio(self, audio_data: bytes) -> bool:
        """Validate audio input before processing."""
        if len(audio_data) < 1024:  # Too short
            raise ValueError("Audio too short")
        if len(audio_data) > 10 * 1024 * 1024:  # >10MB
            raise ValueError("Audio file too large")
        return True
