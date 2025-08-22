from datetime import datetime, UTC
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, ConfigDict, field_serializer


class AnonymousUser(BaseModel):
    user_id: str = Field(..., description="Anonymous unique user identifier")
    cultural_background: str = Field(
        "indian_general", description="User's cultural grouping"
    )
    preferred_language: str = Field("en", description="Preferred language code")
    age_group: Optional[str] = Field(None, description="User age group")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_active: Optional[datetime] = Field(default_factory=lambda: datetime.now(UTC))
    privacy_settings: Optional[Dict[str, bool]] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created_at", "last_active")
    def serialize_datetimes(self, dt: datetime) -> str:
        return dt.isoformat()


class Conversation(BaseModel):
    conversation_id: str = Field(..., description="Unique conversation ID")
    user_id: str = Field(..., description="Associated anonymous user ID")
    messages: List[Dict] = Field(
        default_factory=list, description="Sequence of message dicts"
    )
    emotion_analysis: Optional[Dict[str, float]] = Field(default_factory=dict)
    crisis_score: Optional[float] = Field(0.0)
    cultural_context: Optional[Dict[str, str]] = Field(default_factory=dict)
    rag_sources: Optional[List[str]] = Field(
        default_factory=list, description="RAG knowledge sources referenced"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created_at", "updated_at")
    def serialize_datetimes(self, dt: datetime) -> str:
        return dt.isoformat()


class PeerCircle(BaseModel):
    circle_id: str = Field(..., description="Peer circle unique ID")
    participants: List[str] = Field(
        default_factory=list, description="List of anonymous user IDs"
    )
    cultural_match_score: Optional[float] = Field(0.0)
    topic_category: Optional[str] = Field(
        "general", description="Discussion topic category"
    )
    active_status: bool = Field(True, description="Whether the circle is active")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_activity: Optional[datetime] = Field(default_factory=lambda: datetime.now(UTC))

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created_at", "last_activity")
    def serialize_datetimes(self, dt: datetime) -> str:
        return dt.isoformat()


class CrisisAlert(BaseModel):
    alert_id: str = Field(..., description="Unique alert identifier")
    user_id: str = Field(..., description="Anonymous user ID involved")
    crisis_score: float = Field(..., description="Calculated severity score")
    detected_patterns: List[str] = Field(
        default_factory=list, description="Warning signs detected"
    )
    escalation_status: str = Field(
        "pending", description="Escalation status: pending, notified, resolved"
    )
    tele_manas_notified: bool = Field(
        False, description="Whether Tele MANAS was notified"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created_at", "resolved_at")
    def serialize_datetimes(self, dt: Optional[datetime]) -> Optional[str]:
        return dt.isoformat() if dt else None
