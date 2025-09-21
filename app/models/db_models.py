
from datetime import datetime, timezone
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class User(BaseModel):
    user_id: str
    email: str
    google_id: Optional[str] = None
    name: Optional[str] = None
    picture: Optional[str] = None
    cultural_background: str = Field(default="indian_general")
    preferred_language: str = Field(default="en-US")
    age_group: Optional[str] = None
    
    # Onboarding fields
    onboarding_completed: bool = Field(default=False)
    role: Optional[str] = None  # "student" or "institution"
    
    # Role-specific profile fields
    profile: Dict[str, str] = Field(default_factory=dict)
    
    # Institution relationship (for students)
    institution_id: Optional[str] = None  # null if "No Institution"
    
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    last_active: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    privacy_settings: Dict[str, bool] = Field(
        default_factory=lambda: {"share_data": False}
    )
    
    # Privacy flags for Feature 5
    privacy_flags: Dict[str, bool] = Field(
        default_factory=lambda: {
            "share_moods": True,
            "share_conversations": True
        }
    )


class Institution(BaseModel):
    institution_id: str
    institution_name: str  # Must be unique
    contact_person: str
    region: str
    email: str  # Institution's email (from the user who registered it)
    user_id: str  # Reference to the User who registered this institution
    
    # Stats and metadata
    student_count: int = Field(default=0)
    active: bool = Field(default=True)
    
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class Message(BaseModel):
    message_id: str
    conversation_id: str
    sender_id: str  # user_id or "ai"
    text: str
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    metadata: Dict[str, Optional[str]] = Field(default_factory=dict)
    mood_score: Optional[Dict[str, str]] = None  # mood details


class Conversation(BaseModel):
    conversation_id: str
    participants: List[str] = Field(default_factory=list)  # user_ids
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    last_active_at: datetime = Field(
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


class InstitutionNotification(BaseModel):
    """Notification shown on institution dashboard (privacy-preserving)."""
    notification_id: str
    institution_id: str
    user_id: str  # student user_id; no PII beyond ID
    type: str = Field(default="crisis")  # e.g., crisis, info, system
    severity: str = Field(default="high")  # low/medium/high
    risk_score: int = 0
    risk_level: str = "low"
    reason: Optional[str] = None  # brief, non-sensitive reason string
    status: str = Field(default="unread")  # unread/read/acknowledged
    metadata: Dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class Mood(BaseModel):
    """Mood entry for students."""
    mood_id: str
    student_id: str  # user_id of the student
    mood: str  # mood value (happy, sad, anxious, etc.)
    notes: Optional[str] = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class AccessLog(BaseModel):
    """Access log entry for tracking data access."""
    log_id: str
    user_id: str  # The user whose data was accessed
    resource: str  # Resource accessed (e.g., "moods", "conversations")
    action: str  # Action performed (e.g., "view", "export", "list")
    performed_by: str  # user_id of who performed the action
    performed_by_role: str  # Role of the person who performed the action
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    metadata: Dict[str, str] = Field(default_factory=dict)  # Additional info

