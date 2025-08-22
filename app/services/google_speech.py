# google_speech.py - Voice Processing Service for MITRA
import asyncio
import logging
from typing import Optional, Dict, Tuple
from google.cloud import speech, texttospeech, translate_v2 as translate
from google.api_core.exceptions import GoogleAPIError
from app.config import settings  # Import project settings
from app.services.gemini_ai import GeminiService  # For emotion integration if needed
from fastapi import HTTPException

# Setup logging
logger = logging.getLogger(__name__)

class SpeechService:
    def __init__(self):
        self.speech_client = speech.SpeechClient() # Automatically fetches the $GOOGLE_APPLICATON_CREDENTIAL
        self.tts_client = texttospeech.TextToSpeechClient()
        self.translate_client = translate.Client()
        self.supported_languages = settings.SUPPORTED_LANGUAGES  # From config.py
    
    # NEW: Language Detection (Missed Function)

    async def detect_language(self, audio_data: bytes, sample_rate: int = 16000) -> str:
        """Automatically detect spoken language from audio."""
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=sample_rate,
            language_code="en-US",  # Primary language
            alternative_language_codes=["hi-IN"],  # Fallback/alternate
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
    async def transcribe_audio(self, audio_data: bytes, language: Optional[str] = None, sample_rate: int = 16000) -> Tuple[str, float]:
        """Convert multilingual voice to text with confidence score."""
        if not language:
            language = await self.detect_language(audio_data, sample_rate)  # Auto-detect if not provided
        
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=sample_rate,
            language_code=language,
            enable_automatic_punctuation=True,
            model="latest_long"  # For longer conversations
        )

        audio = speech.RecognitionAudio(content=audio_data)
        
        try:
            response = await asyncio.to_thread(self.speech_client.recognize, config=config, audio=audio)
            transcript = ""
            confidence = 0.0

            if response.results and response.results[0].alternatives:
                transcript = " ".join([result.alternatives[0].transcript for result in response.results if result.alternatives])
                confidence = response.results[0].alternatives[0].confidence 
                return transcript, confidence
        except GoogleAPIError as e:
            logger.error(f"STT failed: {e}")
            raise HTTPException(status_code=500, detail="Speech recognition error")
    
    # # 2. Text Translation to English - Your Function (Made Optional)
    # async def translate_to_english(self, text: str, source_language: Optional[str] = None) -> str:
    #     """Translate text to English for Gemini input (optional if Gemini handles native lang)."""
    #     if source_language and source_language == "en":
    #         return text  # Skip if already English
    #     
    #     try:
    #         result = await asyncio.to_thread(
    #             self.translate_client.translate,
    #             text,
    #             target_language="en",
    #             source_language=source_language
    #         )
    #         return result["translatedText"]
    #     except GoogleAPIError as e:
    #         logger.error(f"Translation failed: {e}")
    #         return text  # Fallback to original
    
    # 3. Synthesize Response - Your Function with Cultural Enhancements
    async def synthesize_response(self, text: str, language: str, cultural_tone: str = "empathetic_calm") -> bytes:
        """Convert Gemini response to culturally-appropriate voice audio."""
        # Map cultural tone to voice parameters (e.g., slower for calm, regional accents)
        voice_map = {
            "hi": {"name": "hi-IN-Neural2-A", "speaking_rate": 0.9 if cultural_tone == "calm" else 1.0},  # Hindi female neural voice
            "en": {"name": "en-IN-Neural2-B", "speaking_rate": 0.95},  # Indian English male
            # Add more for other languages
        }
        voice_config = voice_map.get(language, {"name": "en-IN-Neural2-A", "speaking_rate": 1.0})
        
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=language,
            name=voice_config["name"]
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=voice_config["speaking_rate"],
            pitch= -2.0 if cultural_tone == "empathetic" else 0.0  # Lower pitch for empathy
        )
        
        try:
            response = await asyncio.to_thread(self.tts_client.synthesize_speech, input=synthesis_input, voice=voice, audio_config=audio_config)
            return response.audio_content
        except GoogleAPIError as e:
            logger.error(f"TTS failed: {e}")
            raise HTTPException(status_code=500, detail="Speech synthesis error")
    
    # 4. Detect Emotional Tone - Your Function
    async def detect_emotional_tone(self, audio_data: bytes, language: str) -> Dict[str, float]:
        """Analyze emotional state from voice patterns (basic prosody + Gemini integration)."""
        # Step 1: Basic prosody analysis with Speech API
        transcript, _ = await self.transcribe_audio(audio_data, language)
        
        # Step 2: Use Gemini for advanced emotion detection (integrate with gemini_ai.py)
        gemini_service = GeminiService()
        emotion_prompt = f"Analyze emotional tone from this transcript: '{transcript}'. Detect anxiety, sadness, anger, calmness. Return scores 0-1."
        gemini_response = await gemini_service.process_cultural_conversation(emotion_prompt, {"analysis_mode": "emotion"})
        
        # Parse response (example; implement proper parsing)
        emotions = {
            "anxiety": 0.0,
            "sadness": 0.0,
            "calmness": 0.0,
            # Add more based on Gemini output
        }
        # Update emotions from gemini_response
        
        return emotions
    
    # NEW: Full Pipeline Wrapper (Recommended Addition)
    async def process_voice_pipeline(self, audio_data: bytes) -> Dict:
        """End-to-end: Detect lang → STT → Translate → Gemini → TTS → Emotion analysis."""
        language = await self.detect_language(audio_data)
        transcript, _ = await self.transcribe_audio(audio_data, language)
        english_text = await self.translate_to_english(transcript, language)
        
        # Feed to Gemini (from gemini_ai.py)
        gemini_service = GeminiService()
        gemini_response = await gemini_service.process_cultural_conversation(english_text, {"language": language})
        
        # Synthesize audio
        audio_output = await self.synthesize_response(gemini_response["response"], language)
        
        # Detect emotions
        emotions = await self.detect_emotional_tone(audio_data, language)
        
        return {
            "transcript": transcript,
            "english_text": english_text,
            "gemini_response": gemini_response,
            "audio_output": audio_output,  # Bytes for response
            "emotions": emotions
        }
    
    # NEW: Audio Validation (Recommended Addition)
    def validate_audio(self, audio_data: bytes) -> bool:
        """Validate audio input before processing."""
        if len(audio_data) < 1024:  # Too short
            raise ValueError("Audio too short")
        if len(audio_data) > 10 * 1024 * 1024:  # >10MB
            raise ValueError("Audio file too large")
        return True
