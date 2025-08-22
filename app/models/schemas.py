from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class LanguageCode(str, Enum):
    ENGLISH_US = "en-US"
    ENGLISH_GB = "en-GB"
    SPANISH = "es-ES"
    FRENCH = "fr-FR"
    HINDI_IN = "hi-IN"


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=1024,
        description="User text or voice converted to text",
    )
    language: LanguageCode = Field(
        LanguageCode.ENGLISH_US, description="Language code of the message"
    )
    cultural_context: Optional[Dict[str, str]] = Field(
        default_factory=dict, description="Optional cultural metadata"
    )
    voice_data: Optional[str] = Field(
        None, description="Optional base64 encoded voice input"
    )


class ChatResponse(BaseModel):
    response: str = Field(..., description="AI-generated response text")
    emotion_detected: Optional[Dict[str, float]] = Field(
        default_factory=dict, description="Emotion scores"
    )
    crisis_score: Optional[float] = Field(0.0, description="Crisis risk score")
    rag_sources: Optional[List[str]] = Field(
        default_factory=list, description="Sources used by RAG"
    )
    suggested_actions: Optional[List[str]] = Field(
        default_factory=list, description="Suggested next steps"
    )
    cultural_adaptations: Optional[Dict[str, str]] = Field(
        default_factory=dict, description="Cultural content adjustments"
    )


class PeerMatchRequest(BaseModel):
    interests: Optional[List[str]] = Field(
        default_factory=list, description="User interests"
    )
    cultural_background: Optional[str] = Field(
        "indian_general", description="User cultural group"
    )
    support_type: Optional[str] = Field(
        "general", description="Type of mental health support requested"
    )


class PeerMatchResponse(BaseModel):
    matched_user_ids: List[str] = Field(
        ..., description="List of anonymous peer user IDs matched"
    )


class FamilyEducationRequest(BaseModel):
    family_type: Optional[str] = Field(
        "nuclear", description="Type of family structure"
    )
    cultural_region: Optional[str] = Field(
        "north_indian", description="Cultural/regional background"
    )
    education_level: Optional[str] = Field(
        "college_educated", description="Education level"
    )
    specific_concerns: Optional[List[str]] = Field(
        default_factory=list, description="Specific mental health concerns"
    )


class FamilyEducationResponse(BaseModel):
    educational_content: str = Field(
        ..., description="Generated family education content"
    )
    recommended_resources: Optional[List[str]] = Field(
        default_factory=list, description="Links or documents"
    )


class CrisisDetectionRequest(BaseModel):
    conversation_history: List[Dict] = Field(
        ..., description="Sequence of messages for analysis"
    )


class CrisisDetectionResponse(BaseModel):
    crisis_score: float = Field(..., description="Computed crisis severity score")
    escalation_needed: bool = Field(
        ..., description="Flag indicating if escalation is necessary"
    )
    detected_patterns: List[str] = Field(
        default_factory=list, description="Warning signs identified"
    )
