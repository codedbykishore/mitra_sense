
from datetime import datetime, timezone
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class User(BaseModel):
    user_id: str
    email: str
    hashed_password: Optional[str] = None
    google_id: Optional[str] = None
    cultural_background: str = Field(default="indian_general")
    preferred_language: str = Field(default="en-US")
    age_group: Optional[str] = None
    
    # Onboarding fields
    onboarding_completed: bool = Field(default=False)
    role: Optional[str] = None  # "student" or "institution"
    
    # Role-specific profile fields
    profile: Dict[str, str] = Field(default_factory=dict)
    
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    last_active: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    privacy_settings: Dict[str, bool] = Field(
        default_factory=lambda: {"share_data": False}
    )


class Conversation(BaseModel):
    conversation_id: str
    user_id: str
    messages: List[Dict] = Field(default_factory=list)
    emotion_analysis: Dict[str, float] = Field(default_factory=dict)
    crisis_score: float = 0.0
    cultural_context: Dict[str, str] = Field(default_factory=dict)
    rag_sources: List[str] = Field(default_factory=list)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class PeerCircle(BaseModel):
    circle_id: str
    participants: List[str] = Field(default_factory=list)
    cultural_match_score: float = 0.0
    topic_category: str = "general"
    active_status: bool = True
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    last_activity: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class CrisisAlert(BaseModel):
    alert_id: str
    user_id: str
    crisis_score: float
    detected_patterns: List[str] = Field(default_factory=list)
    escalation_status: str = "pending"  # pending/resolved/escalated
    tele_manas_notified: bool = False
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    resolved_at: Optional[datetime] = None

