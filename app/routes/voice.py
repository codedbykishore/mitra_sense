# app/routes/voice.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.google_speech import SpeechService

router = APIRouter()
speech_service = SpeechService()


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


@router.post("/voice/synthesize")
async def synthesize_voice(
    text: str, language: str = "en-IN", cultural_tone: str = "empathetic_calm"
):
    try:
        speech_bytes = await speech_service.synthesize_response(
            text, language, cultural_tone
        )
        return {"audio": speech_bytes}  # Return as bytes, handle streaming if needed
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS error: {e}")


@router.post("/voice/pipeline")
async def full_voice_pipeline(audio: UploadFile = File(...)):
    try:
        audio_bytes = await audio.read()
        result = await speech_service.process_voice_pipeline(audio_bytes)
        return {
            "transcript": result["transcript"],
            "response": result["gemini_response"],
            "audio_output": result["audio_output"],
            "emotions": result["emotions"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {e}")
