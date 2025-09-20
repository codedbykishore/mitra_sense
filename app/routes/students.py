# app/routes/students.py
from fastapi import APIRouter, HTTPException, Depends, Query
from app.models.schemas import (
    StudentsListResponse, StudentInfo,
    AddMoodRequest, AddMoodResponse, MoodsListResponse, MoodEntry
)
from app.models.db_models import User
from app.services.student_service import StudentService
from app.services.firestore import FirestoreService
from app.services.privacy_service import PrivacyService
from app.services.logging_service import LoggingService
from app.middleware.privacy_middleware import PrivacyMiddleware
from app.dependencies.auth import get_current_user_from_session
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
student_service = StudentService()

# Initialize privacy services
firestore_service = FirestoreService()
privacy_service = PrivacyService(firestore_service)
logging_service = LoggingService(firestore_service)
privacy_middleware = PrivacyMiddleware(privacy_service, logging_service)


@router.get("/students", response_model=StudentsListResponse)
async def list_students(
    current_user: User = Depends(get_current_user_from_session)
):
    """
    Get list of all registered students.
    Requires authentication.
    """
    try:
        logger.info(f"User {current_user.user_id} requesting student list")
        
        students_data = await student_service.list_students()
        
        # Convert to StudentInfo objects
        students = [
            StudentInfo(**student_data) for student_data in students_data
        ]
        
        return StudentsListResponse(
            students=students,
            total_count=len(students)
        )
        
    except Exception as e:
        logger.error(f"Error listing students: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve students: {str(e)}"
        )


@router.post(
    "/students/{student_id}/moods",
    response_model=AddMoodResponse
)
async def add_student_mood(
    student_id: str,
    request: AddMoodRequest,
    current_user: User = Depends(get_current_user_from_session)
):
    """
    Add a new mood entry for a student.
    Requires authentication.
    """
    try:
        logger.info(
            f"User {current_user.user_id} adding mood for student {student_id}"
        )
        
        # Add the mood entry
        mood_data = await student_service.add_mood(
            student_id=student_id,
            mood=request.mood,
            notes=request.notes
        )
        
        # Create mood entry response
        mood_entry = MoodEntry(**mood_data)
        
        return AddMoodResponse(
            success=True,
            message="Mood entry added successfully",
            mood_entry=mood_entry
        )
        
    except ValueError as e:
        logger.warning(f"Invalid request for adding mood: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding mood for student {student_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add mood entry: {str(e)}"
        )


@router.get(
    "/students/{student_id}/moods",
    response_model=MoodsListResponse
)
async def get_student_moods(
    student_id: str,
    limit: int = Query(
        10, ge=1, le=100, description="Number of moods to return"
    ),
    current_user: User = Depends(get_current_user_from_session)
):
    """
    Get recent mood entries for a student.
    Requires authentication and privacy check.
    """
    try:
        logger.info(
            f"User {current_user.user_id} requesting moods for "
            f"student {student_id} (limit: {limit})"
        )
        
        # Check privacy flags and log access
        await privacy_middleware.check_and_log_access(
            target_user_id=student_id,
            resource_type="moods",
            action="view",
            current_user=current_user.model_dump(),
            metadata={"limit": str(limit)}
        )
        
        # Get mood entries
        moods_data = await student_service.get_moods(
            student_id=student_id,
            limit=limit
        )
        
        # Convert to MoodEntry objects
        moods = [MoodEntry(**mood_data) for mood_data in moods_data]
        
        return MoodsListResponse(
            student_id=student_id,
            moods=moods,
            total_count=len(moods)
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions from privacy middleware
        raise
    except ValueError as e:
        logger.warning(f"Invalid request for getting moods: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting moods for student {student_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve mood entries: {str(e)}"
        )


@router.get("/students/{student_id}")
async def get_student_info(
    student_id: str,
    current_user: User = Depends(get_current_user_from_session)
):
    """
    Get detailed information about a specific student.
    Requires authentication.
    """
    try:
        logger.info(
            f"User {current_user.user_id} requesting info for "
            f"student {student_id}"
        )
        
        student_info = await student_service.get_student_info(student_id)
        
        if not student_info:
            raise HTTPException(
                status_code=404,
                detail="Student not found"
            )
        
        return student_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting student info for {student_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve student information: {str(e)}"
        )


@router.get("/students/analytics/mood-summary")
async def get_mood_analytics(
    current_user: User = Depends(get_current_user_from_session)
):
    """
    Get aggregated mood analytics across all students.
    Provides overview statistics for facilitator dashboard.
    """
    try:
        logger.info(f"User {current_user.user_id} requesting mood analytics")
        
        # Get all students
        students_data = await student_service.list_students()
        
        # Initialize counters
        total_students = len(students_data)
        total_mood_entries = 0
        mood_distribution = {}
        students_with_recent_moods = 0
        
        # Process each student's mood data
        for student in students_data:
            try:
                # Get recent moods for this student (last 10)
                moods = await student_service.get_moods(
                    student["user_id"], limit=10
                )
                
                if moods:
                    students_with_recent_moods += 1
                    total_mood_entries += len(moods)
                    
                    # Count mood types
                    for mood_entry in moods:
                        mood = mood_entry["mood"]
                        mood_distribution[mood] = mood_distribution.get(mood, 0) + 1
                        
            except Exception as e:
                logger.warning(f"Error processing moods for student {student['user_id']}: {e}")
                continue
        
        # Calculate percentages
        mood_percentages = {}
        if total_mood_entries > 0:
            for mood, count in mood_distribution.items():
                mood_percentages[mood] = round((count / total_mood_entries) * 100, 1)
        
        return {
            "total_students": total_students,
            "students_with_mood_entries": students_with_recent_moods,
            "total_mood_entries": total_mood_entries,
            "mood_distribution": mood_distribution,
            "mood_percentages": mood_percentages,
            "average_moods_per_active_student": round(
                total_mood_entries / students_with_recent_moods, 1
            ) if students_with_recent_moods > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"Error getting mood analytics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve mood analytics: {str(e)}"
        )
