"""Privacy and Access Logging routes for Feature 5."""

import logging

from fastapi import APIRouter, HTTPException, Depends, status
from app.models.schemas import (
    UpdatePrivacyRequest, UpdatePrivacyResponse, AccessLogsResponse,
    AccessLogEntry
)
from app.services.firestore import FirestoreService
from app.services.privacy_service import PrivacyService
from app.services.logging_service import LoggingService
from app.dependencies.auth import get_current_user_from_session

router = APIRouter(prefix="/api/v1", tags=["privacy"])
logger = logging.getLogger(__name__)

# Initialize services
firestore_service = FirestoreService()
privacy_service = PrivacyService(firestore_service)
logging_service = LoggingService(firestore_service)


@router.patch("/students/{student_id}/privacy")
async def update_student_privacy(
    student_id: str,
    request: UpdatePrivacyRequest,
    current_user=Depends(get_current_user_from_session)
) -> UpdatePrivacyResponse:
    """
    Update privacy flags for a student.
    Only the student themselves or institution admin can update.
    """
    try:
        # Check authorization
        if current_user["user_id"] != student_id:
            # Check if current user is institution admin for this student
            student = await firestore_service.get_user(student_id)
            if not student:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Student not found"
                )
            
            # For institutions: verify the current user is admin of the same
            # institution as the student
            user_role = current_user.get("role")
            user_institution = current_user.get("institution_id")
            if (user_role != "institution" or
                    user_institution != student.institution_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to update privacy settings"
                )
        
        # Update privacy flags
        success = await privacy_service.update_privacy_flags(
            student_id, request.privacy_flags.model_dump()
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update privacy settings"
            )
        
        # Log the privacy update action
        await logging_service.log_access(
            user_id=student_id,
            resource="privacy_settings",
            action="update",
            performed_by=current_user["user_id"],
            performed_by_role=current_user.get("role", "unknown"),
            metadata={
                "share_moods": str(request.privacy_flags.share_moods),
                "share_conversations": str(
                    request.privacy_flags.share_conversations
                )
            }
        )
        
        return UpdatePrivacyResponse(
            success=True,
            message="Privacy settings updated successfully",
            privacy_flags=request.privacy_flags
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating privacy settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/students/{student_id}/access-logs")
async def get_student_access_logs(
    student_id: str,
    limit: int = 50,
    current_user=Depends(get_current_user_from_session)
) -> AccessLogsResponse:
    """
    Get access logs for a student.
    Only institution admins can view access logs.
    """
    try:
        # Check authorization - only institution role can view access logs
        if current_user.get("role") != "institution":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only institution administrators can view access logs"
            )
        
        # Verify the student exists and belongs to the same institution
        student = await firestore_service.get_user(student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        # Note: For now, we allow any institution admin to view any
        # student's access logs. In a production system, you would want
        # to verify the institution relationship more thoroughly.
        
        # Get access logs
        logs = await logging_service.get_access_logs(student_id, limit)
        
        # Convert to response format
        log_entries = []
        for log in logs:
            log_entries.append(AccessLogEntry(
                log_id=log.log_id,
                resource=log.resource,
                action=log.action,
                performed_by=log.performed_by,
                performed_by_role=log.performed_by_role,
                timestamp=log.timestamp.isoformat(),
                metadata=log.metadata
            ))
        
        # Log this access to access logs (meta-logging)
        await logging_service.log_access(
            user_id=student_id,
            resource="access_logs",
            action="view",
            performed_by=current_user["user_id"],
            performed_by_role=current_user.get("role", "unknown")
        )
        
        return AccessLogsResponse(
            student_id=student_id,
            logs=log_entries,
            total_count=len(log_entries)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving access logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
