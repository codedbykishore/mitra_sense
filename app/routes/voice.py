# app/routes/voice.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from app.services.google_speech import SpeechService
from fastapi.responses import StreamingResponse, JSONResponse
import io
import base64
import logging
from app.config import settings # Import settings

logger = logging.getLogger(__name__)

router = APIRouter()
speech_service = SpeechService(rag_corpus_name=settings.CORPUS_NAME) # Pass RAG corpus name


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


@router.get("/voice/pipeline/audio")
@router.post(
    "/voice/pipeline/audio",
    response_class=StreamingResponse,
    responses={200: {"content": {"audio/mpeg": {}}}},
)
async def full_voice_pipeline_file(audio: UploadFile = File(...)):
    try:
        logger.info(f"Received audio file (file route): {audio.filename}, Content-Type: {audio.content_type}")
        audio_bytes = await audio.read()
        result = await speech_service.process_voice_pipeline(audio_bytes)

        headers = {"Content-Disposition": "attachment; filename=output.mp3"}
        return StreamingResponse(
            io.BytesIO(result["audio_output"]),
            media_type="audio/mpeg",
            headers=headers,
        )
    except Exception as e:
        logger.error(f"Pipeline error in full_voice_pipeline_file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Pipeline error: {e}")
