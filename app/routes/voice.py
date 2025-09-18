# app/routes/voice.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from app.services.google_speech import SpeechService
from app.services.gemini_ai import GeminiService
from fastapi.responses import StreamingResponse, JSONResponse
import io
import base64
import logging
import json
import time
from app.config import settings # Import settings

logger = logging.getLogger(__name__)

router = APIRouter()
speech_service = SpeechService(rag_corpus_name=settings.CORPUS_NAME) # Pass RAG corpus name
gemini_service = GeminiService()


@router.post("/voice/transcribe")
async def transcribe_voice(audio: UploadFile = File(...)):
    try:
        audio_bytes = await audio.read()
        transcript, confidence = await speech_service.transcribe_audio(audio_bytes)
        return {"transcript": transcript, "confidence": confidence}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT error: {e}")


@router.post("/voice/emotion")
async def detect_emotion(audio: UploadFile = File(...)):
    try:
        audio_bytes = await audio.read()
        language = await speech_service.detect_language(audio_bytes)
        emotions = await speech_service.detect_emotional_tone(audio_bytes, language)
        return {"emotions": emotions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Emotion analysis error: {e}")


@router.get("/voice/synthesize")
@router.post("/voice/synthesize")
async def synthesize_voice(
    text: str, language: str = "en-IN", cultural_tone: str = "empathetic_calm"
):
    try:
        speech_bytes = await speech_service.synthesize_response(
            text, language, cultural_tone
        )
        return StreamingResponse(io.BytesIO(speech_bytes), media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS error: {e}")


@router.post("/voice/pipeline")
async def full_voice_pipeline(audio: UploadFile = File(...)):
    try:
        logger.info(f"Received audio file: {audio.filename}, Content-Type: {audio.content_type}")
        audio_bytes = await audio.read()
        result = await speech_service.process_voice_pipeline(audio_bytes)
        return {
            "transcript": result["transcript"],
            "response": result["gemini_response"],
            "audio_output": result["audio_output"],
            "emotions": result["emotions"],
        }
    except Exception as e:
        logger.error(f"Pipeline error in full_voice_pipeline: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Pipeline error: {e}")


@router.post("/voice/pipeline/audio")
async def voice_pipeline_json(
    audio: UploadFile = File(...),
    duration: str = Query(default="0"),
    sessionId: str = Query(default=""),
    conversationId: str = Query(default=""),
    culturalContext: str = Query(default="{}")
):
    """
    Complete voice pipeline endpoint that returns JSON response for VoiceCompanion.
    """
    try:
        import json
        import time
        
        logger.info(f"Voice pipeline request - File: {audio.filename}, Duration: {duration}s, Session: {sessionId}")
        
        # Parse cultural context
        try:
            cultural_data = json.loads(culturalContext) if culturalContext else {}
        except json.JSONDecodeError:
            cultural_data = {}
        
        # Read audio data
        audio_bytes = await audio.read()
        logger.info(f"Audio data size: {len(audio_bytes)} bytes")
        
        # Process through speech service
        result = await speech_service.process_voice_pipeline(audio_bytes)
        
        # Format response to match VoiceCompanion expectations
        response = {
            "transcription": {
                "text": result.get("transcript", ""),
                "language": cultural_data.get("language", "en-US"),
                "confidence": 0.9
            },
            "emotion": result.get("emotions", {
                "primaryEmotion": "neutral",
                "confidence": 0.5,
                "stressLevel": 0.3,
                "characteristics": {
                    "pitch": 50,
                    "volume": 50,
                    "speed": 50,
                    "clarity": 90
                }
            }),
            "aiResponse": {
                "text": result.get("gemini_response", {}).get("response", "I understand. How can I help you today?"),
                "crisisScore": result.get("gemini_response", {}).get("crisis_score", 0.1),
                "culturalAdaptations": cultural_data,
                "suggestedActions": ["Take a deep breath", "Stay calm"],
                "ragSources": result.get("gemini_response", {}).get("rag_sources", [])
            },
            "ttsAudio": {
                "url": f"data:audio/mpeg;base64,{base64.b64encode(result.get('audio_output', b'')).decode('utf-8')}" if result.get("audio_output") else None,
                "blob": None,  # Frontend will handle blob conversion if needed
                "format": "audio/mpeg",
                "duration": float(duration) if duration else 2.0
            },
            "session": {
                "sessionId": sessionId or f"session_{hash(audio_bytes) % 10000}",
                "conversationId": conversationId or f"conv_{hash(audio_bytes) % 10000}",
                "timestamp": str(int(time.time()))
            }
        }
        
        logger.info(f"Pipeline successful - Transcript: '{response['transcription']['text'][:50]}...'")
        return response
        
    except Exception as e:
        logger.error(f"Voice pipeline error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Voice pipeline error: {str(e)}")


@router.get("/voice/pipeline/audio")
async def voice_pipeline_info():
    """Get information about the voice pipeline endpoint"""
    return {
        "endpoint": "/voice/pipeline/audio",
        "method": "POST",
        "description": "Complete voice processing pipeline",
        "parameters": {
            "audio": "Audio file (WAV, WebM, MP3, etc.)",
            "duration": "Audio duration in seconds",
            "sessionId": "Session identifier",
            "conversationId": "Conversation identifier",
            "culturalContext": "JSON string with language and cultural settings"
        }
    }
