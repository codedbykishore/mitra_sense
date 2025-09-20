# app/routes/crisis.py
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging

from app.services.crisis import CrisisService
from app.services.gemini_ai import GeminiService
from app.services.firestore import FirestoreService

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
firestore_service = FirestoreService()
gemini_service = GeminiService()
crisis_service = CrisisService(
    firestore_client=firestore_service.db,
    gemini_service=gemini_service,
    twilio_client=None  # TODO: Add Twilio client when ready
)


class CrisisDetectionRequest(BaseModel):
    """Request schema for crisis detection"""
    text: str = Field(..., description="The text to analyze for crisis indicators")
    user_id: Optional[str] = Field(None, description="User ID (optional if using auth)")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")


class CrisisDetectionResponse(BaseModel):
    """Response schema for crisis detection"""
    risk_score: int = Field(..., description="Risk score (0-10)")
    risk_level: str = Field(..., description="Risk level: low, medium, high")
    reason: str = Field(..., description="Explanation of the risk assessment")
    requires_escalation: bool = Field(..., description="Whether escalation is recommended")
    escalation_performed: bool = Field(default=False, description="Whether escalation was performed")
    escalation_details: Optional[Dict[str, Any]] = Field(None, description="Details of escalation if performed")


class EscalationRequest(BaseModel):
    """Request schema for manual escalation"""
    user_id: str = Field(..., description="User ID to escalate")
    risk_score: int = Field(..., description="Risk score (0-10)", ge=0, le=10)
    risk_level: str = Field(..., description="Risk level", pattern="^(low|medium|high)$")
    reason: str = Field(..., description="Reason for escalation")
    force: bool = Field(default=False, description="Force escalation even if under cooldown")


class EscalationResponse(BaseModel):
    """Response schema for escalation"""
    status: str = Field(..., description="Escalation status")
    action: str = Field(..., description="Action taken")
    escalation_doc: Optional[Dict[str, Any]] = Field(None, description="Escalation document created")
    telemanas_result: Optional[Dict[str, Any]] = Field(None, description="Tele MANAS notification result")
    whatsapp_result: Optional[Dict[str, Any]] = Field(None, description="WhatsApp notification result")


@router.post("/detect", response_model=CrisisDetectionResponse)
async def detect_crisis(
    request: CrisisDetectionRequest
):
    """
    Detect crisis indicators in text and optionally trigger escalation.
    Combines keyword detection and Gemini AI analysis.
    """
    try:
        # Get user ID from auth or request
        user_id = request.user_id or "anonymous"
        
        logger.info(f"Crisis detection request for user {user_id}: {request.text[:50]}...")
        
        # Assess risk using CrisisService
        risk_report = await crisis_service.assess_risk(
            user_id=user_id,
            text=request.text,
            gemini_response=request.context.get("gemini_response")
        )
        
        requires_escalation = risk_report["risk_level"] in ("medium", "high")
        escalation_performed = False
        escalation_details = None
        
        # Auto-escalate for high risk
        if risk_report["risk_level"] == "high":
            try:
                escalation_result = await crisis_service.escalate(user_id, risk_report)
                escalation_performed = escalation_result["status"] == "escalated"
                escalation_details = escalation_result
                logger.warning(f"Auto-escalation triggered for user {user_id}: {escalation_result['action']}")
            except Exception as e:
                logger.error(f"Auto-escalation failed for user {user_id}: {e}")
                # Don't fail the detection if escalation fails
        
        return CrisisDetectionResponse(
            risk_score=risk_report["risk_score"],
            risk_level=risk_report["risk_level"],
            reason=risk_report["reason"],
            requires_escalation=requires_escalation,
            escalation_performed=escalation_performed,
            escalation_details=escalation_details
        )
        
    except Exception as e:
        logger.error(f"Crisis detection failed for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Crisis detection failed: {str(e)}"
        )


@router.post("/escalate", response_model=EscalationResponse)
async def escalate_crisis(
    request: EscalationRequest
):
    """
    Manually escalate a crisis situation.
    Logs to Firestore, notifies Tele MANAS, and sends parent alerts if configured.
    """
    try:
        logger.info(f"Manual escalation request for user {request.user_id}: risk_level={request.risk_level}")
        
        # Check if under cooldown (unless forced)
        if not request.force and await crisis_service.is_under_cooldown(request.user_id):
            logger.warning(f"Escalation blocked by cooldown for user {request.user_id}")
            return EscalationResponse(
                status="cooldown",
                action="none",
                escalation_doc=None,
                telemanas_result=None,
                whatsapp_result=None
            )
        
        # Create risk report for escalation
        risk_report = {
            "risk_score": request.risk_score,
            "risk_level": request.risk_level,
            "reason": request.reason,
            "user_profile": await crisis_service._get_user_profile(request.user_id)
        }
        
        # Perform escalation
        escalation_result = await crisis_service.escalate(request.user_id, risk_report)
        
        logger.info(f"Manual escalation completed for user {request.user_id}: {escalation_result['action']}")
        
        return EscalationResponse(
            status=escalation_result["status"],
            action=escalation_result["action"],
            escalation_doc=escalation_result.get("escalation_doc"),
            telemanas_result=escalation_result.get("telemanas_result"),
            whatsapp_result=escalation_result.get("whatsapp_result")
        )
        
    except Exception as e:
        logger.error(f"Manual escalation failed for user {request.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Escalation failed: {str(e)}"
        )


@router.get("/status/{user_id}")
async def get_crisis_status(
    user_id: str
):
    """
    Get crisis status for a user (cooldown status, recent escalations).
    """
    try:
        logger.info(f"Crisis status request for user {user_id}")
        
        # Check cooldown status
        under_cooldown = await crisis_service.is_under_cooldown(user_id)
        
        # Get user profile
        user_profile = await crisis_service._get_user_profile(user_id)
        
        return {
            "user_id": user_id,
            "under_cooldown": under_cooldown,
            "cooldown_hours": crisis_service.cooldown_hours,
            "whatsapp_enabled": crisis_service.whatsapp_enabled,
            "has_parent_contact": bool(user_profile.get("parent_contact")),
            "parent_escalation_consent": user_profile.get("parent_escalation"),
            "age": user_profile.get("age")
        }
        
    except Exception as e:
        logger.error(f"Crisis status check failed for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Status check failed: {str(e)}"
        )


@router.get("/keywords")
async def get_crisis_keywords():
    """
    Get the list of crisis keywords used for detection (for transparency/debugging).
    """
    try:
        return {
            "keywords": crisis_service.DEFAULT_KEYWORDS,
            "risk_levels": crisis_service.RISK_LEVELS,
            "scoring_weights": {
                "gemini_weight": 0.6,
                "keyword_weight": 0.4,
                "high_risk_threshold": 7
            }
        }
    except Exception as e:
        logger.error(f"Keywords request failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Keywords request failed: {str(e)}"
        )


@router.get("/health")
async def crisis_service_health():
    """
    Health check for crisis service components.
    """
    try:
        health_status = {
            "service": "operational",
            "firestore": bool(crisis_service.firestore),
            "gemini": bool(crisis_service.gemini_service),
            "twilio": bool(crisis_service.twilio_client),
            "whatsapp_enabled": crisis_service.whatsapp_enabled,
            "cooldown_hours": crisis_service.cooldown_hours
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Crisis service health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )
