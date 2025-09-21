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


def _format_emotion_response(emotions_dict: dict) -> dict:
    """Format emotion dictionary from speech service to match frontend expectations."""
    if not emotions_dict:
        return {
            "primaryEmotion": "neutral",
            "confidence": 0.5,
            "stressLevel": 0.3,
            "characteristics": {
                "pitch": 50,
                "volume": 50,
                "speed": 50,
                "clarity": 90
            }
        }
    
    # Find the emotion with highest score as primary emotion
    primary_emotion = "neutral"
    max_score = 0.0
    total_stress = 0.0
    
    stress_emotions = ["anxiety", "anger", "sadness", "worried", "frustrated"]
    
    for emotion, score in emotions_dict.items():
        if score > max_score:
            max_score = score
            primary_emotion = emotion
        
        # Calculate stress level from negative emotions
        if emotion.lower() in stress_emotions:
            total_stress += score
    
    return {
        "primaryEmotion": primary_emotion,
        "confidence": max_score,
        "stressLevel": min(total_stress, 1.0),  # Cap at 1.0
        "characteristics": {
            "pitch": 50,
            "volume": 50,
            "speed": 50,
            "clarity": 90
        }
    }


@router.post("/voice/transcribe")
async def transcribe_voice(audio: UploadFile = File(...)):
    try:
        audio_bytes = await audio.read()
        if not audio_bytes or len(audio_bytes) == 0:
            raise HTTPException(status_code=400, detail="No audio data received")
        try:
            speech_service.validate_audio(audio_bytes)
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))
        transcript, confidence = await speech_service.transcribe_audio(audio_bytes)
        return {"transcript": transcript, "confidence": confidence}
    except HTTPException as e:
        # Preserve original status/detail
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT error: {e}")


@router.post("/voice/emotion")
async def detect_emotion(audio: UploadFile = File(...)):
    try:
        audio_bytes = await audio.read()
        if not audio_bytes or len(audio_bytes) == 0:
            raise HTTPException(status_code=400, detail="No audio data received")
        language = await speech_service.detect_language(audio_bytes)
        emotions = await speech_service.detect_emotional_tone(audio_bytes, language)
        return {"emotions": emotions}
    except HTTPException as e:
        raise e
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
        if not audio_bytes or len(audio_bytes) == 0:
            raise HTTPException(status_code=400, detail="No audio data received")
        try:
            speech_service.validate_audio(audio_bytes)
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))
        result = await speech_service.process_voice_pipeline(audio_bytes)
        return {
            "transcript": result["transcript"],
            "response": result["gemini_response"],
            "audio_output": result["audio_output"],
            "emotions": result["emotions"],
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Pipeline error in full_voice_pipeline: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Pipeline error: {e}")


@router.post("/voice/pipeline/audio")
async def voice_pipeline_json(
    audio: UploadFile = File(...),
    duration: str = Query(default="0"),
    sessionId: str = Query(default=""),
    conversationId: str = Query(default=""),
    culturalContext: str = Query(default="{}"),
    forceLanguage: str = Query(default="", description="Force specific language (e.g., 'en-US', 'hi-IN')")
):
    """
    Complete voice pipeline endpoint that returns JSON response for VoiceCompanion.
    Uses voice-optimized responses (shorter, TTS-friendly).
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
        
        # Override language if specified
        if forceLanguage:
            cultural_data["language"] = forceLanguage
            logger.info(f"Language override: Using forced language '{forceLanguage}'")
        
        # Read audio data
        audio_bytes = await audio.read()
        if not audio_bytes or len(audio_bytes) == 0:
            raise HTTPException(status_code=400, detail="No audio data received")
        try:
            speech_service.validate_audio(audio_bytes)
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))
        logger.info(f"Audio data size: {len(audio_bytes)} bytes")
        
        # Get conversation context if conversationId is provided
        conversation_context = ""
        print(f"\n🔍 VOICE CONTEXT RETRIEVAL DEBUG:")
        print(f"Provided conversationId: '{conversationId}'")
        print(f"sessionId: '{sessionId}'")
        
        if conversationId:
            try:
                from app.services.conversation_service import ConversationService
                conversation_service = ConversationService()
                
                print(f"Attempting to fetch context for conversation: {conversationId}")
                
                # Fetch recent messages for context (limit to 5 for voice)
                recent_messages = await conversation_service.get_recent_context(
                    conversationId, limit=5
                )
                
                print(f"Retrieved {len(recent_messages) if recent_messages else 0} messages")
                
                if recent_messages:
                    conversation_context = await conversation_service.format_context_for_rag(
                        recent_messages, include_metadata=False
                    )
                    print(f"Formatted context length: {len(conversation_context)} chars")
                    print(f"Context preview: '{conversation_context[:200]}...'")
                else:
                    print("No recent messages found for context")
                    
                logger.info(f"Voice context: Found {len(recent_messages) if recent_messages else 0} recent messages")
            except Exception as e:
                print(f"ERROR fetching context: {e}")
                logger.warning(f"Could not fetch voice conversation context: {e}")
        else:
            print("No conversationId provided - no context will be used")
        
        # Process through speech service with voice-optimized responses
        # Pass language preference to the pipeline
        pipeline_options = {
            "conversation_context": conversation_context,
            "force_language": forceLanguage,
        }
        result = await speech_service.process_voice_pipeline_optimized(audio_bytes, conversation_context, pipeline_options)
        
        # Format response to match VoiceCompanion expectations
        # Get the detected language from the result
        detected_language = result.get("detected_language", "en-US")
        # Prefer explicit forceLanguage, else stick to detected input (STT) language
        response_language = forceLanguage or detected_language
        
        logger.info(f"Language info - Detected: {detected_language}, Using: {response_language}")
        
        # Save voice messages to Firestore for conversation persistence
        real_conversation_id = conversationId
        if not real_conversation_id:
            # Create new conversation if none provided
            from app.services.firestore import FirestoreService
            firestore_service = FirestoreService()
            real_conversation_id = await firestore_service.create_or_update_conversation(
                "anonymous", force_new=False
            )
        
        # Save user voice message and AI response for context
        try:
            import uuid
            from datetime import datetime, timezone
            from app.services.firestore import FirestoreService
            firestore_service = FirestoreService()
            
            transcript_text = result.get("transcript", "")
            ai_response_text = result.get("gemini_response", {}).get("response", "")
            
            # Save user message
            user_message_data = {
                "message_id": str(uuid.uuid4()),
                "conversation_id": real_conversation_id,
                "sender_id": "user",
                "text": transcript_text,
                "timestamp": datetime.now(timezone.utc),
                "metadata": {
                    "source": "voice",
                    "language": detected_language,
                    "embedding_id": None,
                    "emotion_score": json.dumps(result.get("emotions", {}))
                }
            }
            await firestore_service.save_message(real_conversation_id, user_message_data)
            
            # Save AI response
            ai_message_data = {
                "message_id": str(uuid.uuid4()),
                "conversation_id": real_conversation_id,
                "sender_id": "ai",
                "text": ai_response_text,
                "timestamp": datetime.now(timezone.utc),
                "metadata": {
                    "source": "voice",
                    # Save the actual response language (may be forced)
                    "language": response_language,
                    "embedding_id": None,
                    "emotion_score": "{}"
                }
            }
            await firestore_service.save_message(real_conversation_id, ai_message_data)
            
            logger.info(f"Saved voice messages to conversation {real_conversation_id}")
        except Exception as e:
            logger.warning(f"Failed to save voice messages to Firestore: {e}")
        
        # Format response to match VoiceCompanion expectations
        response = {
            "transcription": {
                "text": result.get("transcript", ""),
                "language": response_language,
                "confidence": 0.9,
                "detectedLanguage": detected_language
            },
            "emotion": _format_emotion_response(result.get("emotions", {})),
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
                "conversationId": real_conversation_id,  # Use real conversation ID
                "timestamp": str(int(time.time()))
            }
        }
        
        logger.info(f"Pipeline successful - Transcript: '{response['transcription']['text'][:50]}...'")
        
        # Debug: Log the full response JSON to console for debugging
        print("\n" + "="*60)
        print("🎤 VOICE PIPELINE RESPONSE DEBUG")
        print("="*60)
        print(json.dumps({
            "conversationId": real_conversation_id,
            "contextUsed": len(conversation_context) > 0,
            "contextLength": len(conversation_context),
            "transcription": response['transcription']['text'],
            "aiResponse": response['aiResponse']['text'][:200] + "..." if len(response['aiResponse']['text']) > 200 else response['aiResponse']['text'],
            "hasAudio": bool(response['ttsAudio']['url']),
            "emotion": response['emotion']['primaryEmotion'] if response.get('emotion') else None,
            "crisisScore": response['aiResponse'].get('crisisScore', 0)
        }, indent=2))
        print("="*60 + "\n")
        
        return response
        
    except HTTPException as e:
        # Let FastAPI propagate intended status codes
        raise e
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
