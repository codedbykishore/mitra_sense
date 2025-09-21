# google_speech.py - Voice Processing Service for MITRA
import asyncio
import logging
import json
from typing import Optional, Dict, Tuple
from google.cloud import speech, texttospeech, translate_v2 as translate
# google.api_core may not be visible to static analyzers; provide a fallback
try:
    from google.api_core.exceptions import GoogleAPIError  # type: ignore[import-not-found,attr-defined]
except Exception:  # pragma: no cover - fallback for type-checkers
    class GoogleAPIError(Exception):
        pass
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

    def _is_opus_container(self, encoding: speech.RecognitionConfig.AudioEncoding) -> bool:
        """Return True if encoding is an OPUS-in-container format (WebM/Ogg)."""
        return encoding in (
            speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
        )

    def _build_recognition_config(
        self,
        *,
        encoding: speech.RecognitionConfig.AudioEncoding,
        language_code: str,
        sample_rate_hz: Optional[int] = None,
        alt_language_codes: Optional[list[str]] = None,
        model: Optional[str] = "latest_long",
        enable_automatic_punctuation: bool = True,
        audio_channel_count: Optional[int] = None,
    ) -> speech.RecognitionConfig:
        """Build a RecognitionConfig, omitting fields not supported for Opus containers.

        Google STT determines sample rate and channels from encoded Opus in WebM/Ogg.
        Passing sample_rate_hertz or audio_channel_count can cause INVALID_ARGUMENT (400).
        """
        alt_language_codes = alt_language_codes or []

        if self._is_opus_container(encoding):
            # Do NOT set sample_rate_hertz or audio_channel_count for OPUS containers
            return speech.RecognitionConfig(
                encoding=encoding,
                language_code=language_code,
                alternative_language_codes=alt_language_codes,
                enable_automatic_punctuation=enable_automatic_punctuation,
                model=model,
            )

        # For PCM/FLAC etc., include sample rate and (optionally) channels
        kwargs: Dict = dict(
            encoding=encoding,
            language_code=language_code,
            alternative_language_codes=alt_language_codes,
            enable_automatic_punctuation=enable_automatic_punctuation,
            model=model,
        )
        if sample_rate_hz:
            kwargs["sample_rate_hertz"] = sample_rate_hz
        if audio_channel_count:
            kwargs["audio_channel_count"] = audio_channel_count
        return speech.RecognitionConfig(**kwargs)

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
        try:
            encoding, detected_sample_rate = self._detect_audio_format(audio_data)
            actual_sample_rate = sample_rate or detected_sample_rate
            # Build config with correct handling for OPUS
            config = self._build_recognition_config(
                encoding=encoding,
                language_code=self.supported_languages[0],
                sample_rate_hz=actual_sample_rate,
                alt_language_codes=self.supported_languages[1:] if len(self.supported_languages) > 1 else [],
                enable_automatic_punctuation=True,
                audio_channel_count=2 if encoding == speech.RecognitionConfig.AudioEncoding.LINEAR16 else None,
            )
            audio = speech.RecognitionAudio(content=audio_data)

            response = await asyncio.to_thread(
                self.speech_client.recognize, config=config, audio=audio
            )
            
            if response.results and len(response.results) > 0:
                # Try to get detected language from response
                result = response.results[0]
                if hasattr(result, "language_code") and result.language_code:
                    return result.language_code
                
                # Fallback: check if we have alternative language results
                if hasattr(result, 'alternatives') and len(result.alternatives) > 0:
                    alternative = result.alternatives[0]
                    if hasattr(alternative, 'language_code') and alternative.language_code:
                        return alternative.language_code
            
            # No language detected, return default
            logger.warning("No language detected from audio, using default")
            return settings.DEFAULT_LANGUAGE  # fallback
            
        except GoogleAPIError as e:
            logger.error(f"Google API language detection failed: {e}")
            # Don't raise HTTP exception, return default language instead
            return settings.DEFAULT_LANGUAGE
        except Exception as e:
            logger.error(f"Unexpected error in language detection: {e}")
            # Return default language for any other errors
            return settings.DEFAULT_LANGUAGE

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
            logger.info(f"Language detection: Detected '{language}' from audio")

        # Build config with correct handling for OPUS
        config = self._build_recognition_config(
            encoding=encoding,
            language_code=language,
            sample_rate_hz=actual_sample_rate,
            alt_language_codes=[],
            enable_automatic_punctuation=True,
            model="latest_long",
            audio_channel_count=2 if encoding == speech.RecognitionConfig.AudioEncoding.LINEAR16 else None,
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
            # Retry with minimal config for OPUS containers in case of invalid argument errors
            if self._is_opus_container(encoding):
                try:
                    minimal_config = speech.RecognitionConfig(
                        encoding=encoding,
                        language_code=language,
                        enable_automatic_punctuation=True,
                    )
                    minimal_response = await asyncio.to_thread(
                        self.speech_client.recognize, config=minimal_config, audio=audio
                    )
                    if minimal_response.results and minimal_response.results[0].alternatives:
                        transcript = " ".join(
                            [
                                result.alternatives[0].transcript
                                for result in minimal_response.results
                                if result.alternatives
                            ]
                        )
                        confidence = minimal_response.results[0].alternatives[0].confidence
                        return transcript, confidence
                except Exception as retry_e:
                    logger.error(f"STT retry with minimal config also failed: {retry_e}")
            raise HTTPException(status_code=500, detail=f"Speech recognition error: {e}")

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
            "en-GB": {
                "name": "en-GB-Neural2-B",
                "language_code": "en-GB", 
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
            "es-ES": {
                "name": "es-ES-Neural2-A",
                "language_code": "es-ES",
                "speaking_rate": 0.9,
            },
            "fr-FR": {
                "name": "fr-FR-Neural2-A",
                "language_code": "fr-FR",
                "speaking_rate": 0.9,
            },
            # Base language codes (without region)
            "en": {
                "name": "en-US-Neural2-C",
                "language_code": "en-US",
                "speaking_rate": 0.9,
            },
            "hi": {
                "name": "hi-IN-Neural2-A",
                "language_code": "hi-IN",
                "speaking_rate": 0.9,
            },
            "es": {
                "name": "es-ES-Neural2-A",
                "language_code": "es-ES",
                "speaking_rate": 0.9,
            },
            "fr": {
                "name": "fr-FR-Neural2-A",
                "language_code": "fr-FR",
                "speaking_rate": 0.9,
            },
            "default": {
                "name": "en-US-Neural2-C",
                "language_code": "en-US",
                "speaking_rate": 0.9,
            },
        }

        voice_key = language.replace("_", "-")  # normalize language code (keep original case)
        voice_config = voice_map.get(voice_key, voice_map["default"])
        
        logger.info(f"TTS: Input language='{language}', Voice key='{voice_key}', Using voice='{voice_config['name']}')")

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

    async def process_voice_pipeline_optimized(self, audio_data: bytes, conversation_context: str = "", pipeline_options: Dict = None) -> Dict:
        """
        Voice-optimized pipeline: Shorter responses, TTS-friendly, no asterisks.
        Uses voice-specific Gemini processing for 15-second responses with conversation context.
        """
        pipeline_options = pipeline_options or {}
        logger.info(f"Voice-optimized pipeline received audio_data. Length: {len(audio_data)} bytes")
        
        # Use forced language if provided, otherwise detect from audio
        force_language = pipeline_options.get("force_language")
        
        if force_language:
            language = force_language
            logger.info(f"Using forced language: {language}")
        else:
            language = await self.detect_language(audio_data)
            logger.info(f"Detected language from audio: {language}")
        
        # Transcribe with the determined language
        transcript, _ = await self.transcribe_audio(audio_data, language)
        logger.info(f"Transcript: {transcript}")

        # Use voice-optimized Gemini processing with conversation context
        # Pass the STT detected language to help Gemini avoid incorrect language detection
        gemini_options = {
            "language": language,  # STT detected language for context
            "conversation_context": conversation_context,
            # Enforce response language: explicit forceLanguage wins, otherwise stick to STT-detected language
            "force_response_language": force_language or language,
            "stt_language": language  # Pass STT language to override Gemini's detection
        }
        if conversation_context:
            logger.info(f"Voice context: Including {len(conversation_context)} chars of conversation history")
            # Debug: Print context to console
            print(f"\n🔍 VOICE CONTEXT DEBUG:")
            print(f"Context length: {len(conversation_context)} characters")
            print(f"Context preview: '{conversation_context[:300]}...'")
        else:
            print(f"\n⚠️  NO VOICE CONTEXT - conversation_context is empty")
        
        gemini_response = await self.gemini_service.process_voice_conversation(
            transcript, gemini_options
        )
        logger.info(f"Voice-optimized Gemini response: {gemini_response}")
        logger.info(f"Voice pipeline: Input language='{language}', Response will be synthesized in same language")

        # Synthesize audio with cleaned response
        audio_output = await self.synthesize_response(
            gemini_response["response"], language
        )
        logger.info(f"Voice-optimized audio output length: {len(audio_output)} bytes")

        # Detect emotions
        emotions = await self.detect_emotional_tone(audio_data, language)
        logger.info(f"Detected emotions: {emotions}")

        return {
            "transcript": transcript,
            "gemini_response": gemini_response,
            "audio_output": audio_output,  # Bytes for response
            "emotions": emotions,
            "detected_language": language,  # Include detected language in result
        }

    # NEW: Audio Validation (Recommended Addition)
    def validate_audio(self, audio_data: bytes) -> bool:
        """Validate audio input before processing."""
        # Fixed channel count issue 14:32 - Force reload
        if len(audio_data) < 1024:  # Too short
            raise ValueError("Audio too short")
        if len(audio_data) > 10 * 1024 * 1024:  # >10MB
            raise ValueError("Audio file too large")
        return True
