# app/routes/mood.py
from fastapi import APIRouter, HTTPException, Depends, Path
from app.models.schemas import (
    UpdateMoodRequest, AddMoodResponse, CurrentMoodResponse,
    MoodStreamResponse, MoodAnalyticsResponse, MoodEntry,
    MoodInferenceRequest, MoodInferenceResponse, EmotionAnalysisResponse
)
from app.models.db_models import User
from app.services.mood_service import MoodService
from app.services.emotion_analysis import EmotionAnalysisService
from app.dependencies.auth import get_current_user_from_session
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
mood_service = MoodService()
emotion_analysis_service = EmotionAnalysisService()


@router.post(
    "/students/{student_id}/mood",
    response_model=AddMoodResponse,
    summary="Update student mood",
    description="Update a student's current mood. Self-access only."
)
async def update_student_mood(
    student_id: str = Path(..., description="Student user ID"),
    request: UpdateMoodRequest = ...,
    current_user: User = Depends(get_current_user_from_session)
):
    """
    Update a student's mood with privacy enforcement and access logging.
    Students can only update their own mood.
    """
    try:
        logger.info(
            f"User {current_user.user_id} updating mood for {student_id}"
        )
        
        # Update the mood using the enhanced service
        mood_data = await mood_service.update_mood(
            student_id=student_id,
            mood=request.mood,
            intensity=request.intensity,
            notes=request.notes,
            current_user=current_user
        )
        
        # Create mood entry response
        mood_entry = MoodEntry(
            mood_id=mood_data["mood_id"],
            mood=mood_data["mood"],
            intensity=mood_data["intensity"],
            notes=mood_data["notes"],
            timestamp=mood_data["timestamp"],
            created_at=mood_data["created_at"]
        )
        
        return AddMoodResponse(
            success=True,
            message="Mood updated successfully",
            mood_entry=mood_entry
        )
        
    except PermissionError as e:
        logger.warning(f"Permission denied for mood update: {e}")
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        logger.warning(f"Invalid request for mood update: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating mood for student {student_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update mood: {str(e)}"
        )


@router.get(
    "/students/{student_id}/mood",
    response_model=CurrentMoodResponse,
    summary="Get current student mood",
    description="Get most recent mood entry. Respects privacy flags."
)
async def get_current_student_mood(
    student_id: str = Path(..., description="Student user ID"),
    current_user: User = Depends(get_current_user_from_session)
):
    """
    Get the most recent mood entry for a student with privacy enforcement.
    Access is logged for audit purposes.
    """
    try:
        logger.info(
            f"User {current_user.user_id} requesting current mood for {student_id}"
        )
        
        # Get current mood using the enhanced service
        mood_data = await mood_service.get_current_mood(
            student_id=student_id,
            current_user=current_user
        )
        
        if mood_data:
            return CurrentMoodResponse(**mood_data)
        else:
            return CurrentMoodResponse()  # Empty response if no mood found
        
    except PermissionError as e:
        logger.warning(f"Permission denied for mood access: {e}")
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        logger.warning(f"Invalid request for mood access: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting current mood for {student_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get current mood: {str(e)}"
        )


@router.get(
    "/students/mood/stream",
    response_model=MoodStreamResponse,
    summary="Get real-time mood feed",
    description="Get recent mood updates from multiple students for real-time monitoring."
)
async def get_mood_stream(
    limit: int = 50,
    current_user: User = Depends(get_current_user_from_session)
):
    """
    Get recent mood updates from multiple students for real-time feed.
    Only includes data from students who have enabled mood sharing.
    """
    try:
        logger.info(f"User {current_user.user_id} requesting mood stream")
        
        # Get mood stream data using the enhanced service
        mood_entries = await mood_service.get_mood_stream_data(
            current_user=current_user,
            limit=limit
        )
        
        # Convert to response format
        from app.models.schemas import MoodStreamEntry
        stream_entries = [
            MoodStreamEntry(**entry) for entry in mood_entries
        ]
        
        return MoodStreamResponse(
            mood_entries=stream_entries,
            total_count=len(stream_entries)
        )
        
    except Exception as e:
        logger.error(f"Error getting mood stream: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get mood stream: {str(e)}"
        )


@router.get(
    "/students/mood/analytics",
    response_model=MoodAnalyticsResponse,
    summary="Get mood analytics",
    description="Get aggregated mood analytics across students with sharing enabled."
)
async def get_mood_analytics(
    current_user: User = Depends(get_current_user_from_session)
):
    """
    Get aggregated mood analytics across students with mood sharing enabled.
    Provides overview statistics for facilitator dashboard.
    """
    try:
        logger.info(f"User {current_user.user_id} requesting mood analytics")
        
        # Get analytics using the enhanced service
        analytics_data = await mood_service.get_mood_analytics(
            current_user=current_user
        )
        
        return MoodAnalyticsResponse(**analytics_data)
        
    except Exception as e:
        logger.error(f"Error getting mood analytics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get mood analytics: {str(e)}"
        )


@router.post(
    "/students/mood/infer",
    response_model=MoodInferenceResponse,
    summary="Infer mood from text",
    description="Analyze text for emotional content and infer mood automatically."
)
async def infer_mood_from_text(
    request: MoodInferenceRequest,
    current_user: User = Depends(get_current_user_from_session)
):
    """
    Analyze text for emotional content and infer mood automatically.
    This endpoint allows testing the mood inference functionality.
    """
    try:
        logger.info(f"User {current_user.user_id} requesting mood inference for text")
        
        # Analyze emotions from text
        emotions = await emotion_analysis_service.analyze_text_emotion(
            request.message, 
            request.language
        )
        
        # Infer mood from emotions
        mood, intensity, confidence = emotion_analysis_service.infer_mood_from_emotions(emotions)
        
        # Check if auto-update should happen
        should_auto_update = False
        if request.auto_update_enabled:
            should_auto_update = await emotion_analysis_service.should_auto_update_mood(
                current_user.user_id, confidence
            )
        
        auto_updated = False
        if should_auto_update:
            try:
                # Auto-update the user's mood
                mood_notes = f"Auto-inferred from text analysis (confidence: {confidence:.1%})"
                await mood_service.update_mood(
                    user_id=current_user.user_id,
                    mood=mood,
                    intensity=intensity,
                    notes=mood_notes
                )
                auto_updated = True
                logger.info(f"Auto-updated mood for user {current_user.user_id}: {mood}")
            except Exception as e:
                logger.error(f"Failed to auto-update mood: {e}")
        
        # Create emotion analysis response
        emotion_analysis = EmotionAnalysisResponse(
            emotions=emotions,
            inferred_mood=mood,
            intensity=intensity,
            confidence=confidence,
            auto_updated=auto_updated,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        # Generate suggestion text
        if confidence >= 0.7:
            suggestion = f"High confidence ({confidence:.1%}) - mood automatically detected as '{mood}'"
        elif confidence >= 0.5:
            suggestion = f"Medium confidence ({confidence:.1%}) - consider confirming mood as '{mood}'"
        else:
            suggestion = f"Low confidence ({confidence:.1%}) - manual mood selection recommended"
        
        if auto_updated:
            suggestion += " and updated automatically."
        elif should_auto_update:
            suggestion += " but auto-update is disabled."
        else:
            suggestion += " (auto-update not triggered)."
        
        privacy_note = "Mood inference respects your privacy settings and requires consent for auto-updates."
        
        return MoodInferenceResponse(
            message_analyzed=request.message,
            emotion_analysis=emotion_analysis,
            suggestion=suggestion,
            privacy_note=privacy_note
        )
        
    except Exception as e:
        logger.error(f"Error in mood inference: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to infer mood: {str(e)}"
        )
