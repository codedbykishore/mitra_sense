from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict
from pydantic import BaseModel, Field
from app.dependencies.auth import get_current_user_from_session
from app.models.db_models import User
from app.services.firestore import FirestoreService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
fs = FirestoreService()


class NotificationItem(BaseModel):
    notification_id: str
    institution_id: str
    user_id: str
    type: str
    severity: str
    risk_score: int
    risk_level: str
    reason: str | None = None
    status: str
    created_at: str | None = None
    metadata: Dict[str, str] = Field(default_factory=dict)


class NotificationsListResponse(BaseModel):
    notifications: List[NotificationItem] = Field(default_factory=list)


@router.get("/notifications/institution", response_model=NotificationsListResponse)
async def list_institution_notifications(
    current_user: User = Depends(get_current_user_from_session),
    institution_id: str | None = None,
):
    if current_user.role not in ("institution", "admin"):
        raise HTTPException(status_code=403, detail="Not authorized")

    resolved_inst_id = None
    if institution_id:
        resolved_inst_id = institution_id
    elif current_user.role == "institution":
        # institution users may not have institution_id on their User doc; look up by owner
        inst = await fs.get_institution_by_owner_user(current_user.user_id)
        resolved_inst_id = inst.institution_id if inst else current_user.institution_id
    elif current_user.role == "admin":
        raise HTTPException(status_code=400, detail="Admin must specify institution_id")
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

    if not resolved_inst_id:
        raise HTTPException(status_code=400, detail="Institution context missing")

    items = await fs.list_institution_notifications(resolved_inst_id)
    return NotificationsListResponse(
        notifications=[NotificationItem(**item) for item in items]
    )


class MarkReadResponse(BaseModel):
    success: bool


@router.post("/notifications/{notification_id}/read", response_model=MarkReadResponse)
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user_from_session)
):
    if current_user.role not in ("institution", "admin"):
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        await fs.mark_notification_read(notification_id)
        return MarkReadResponse(success=True)
    except Exception as e:
        logger.error(f"Failed to mark notification read: {e}")
        raise HTTPException(status_code=500, detail="Failed to update notification")
