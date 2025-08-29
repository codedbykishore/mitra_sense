
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
    message: str = Field(..., min_length=1, max_length=1024)
    language: LanguageCode = Field(default=LanguageCode.ENGLISH_US)
    cultural_context: Dict[str, str] = Field(default_factory=dict)
    voice_data: Optional[str] = None  # base64 encoded


class ChatResponse(BaseModel):
    response: str
    emotion_detected: Dict[str, float] = Field(default_factory=dict)
    crisis_score: float = 0.0
    rag_sources: List[str] = Field(default_factory=list)
    suggested_actions: List[str] = Field(default_factory=list)
    cultural_adaptations: Dict[str, str] = Field(default_factory=dict)


class PeerMatchRequest(BaseModel):
    interests: List[str] = Field(default_factory=list)
    cultural_background: str = Field(default="indian_general")
    support_type: str = Field(default="general")


class PeerMatchResponse(BaseModel):
    user_ids: List[str]  # updated from 'anonymous peer user IDs'


class FamilyEducationRequest(BaseModel):
    family_type: str = Field(default="nuclear")
    cultural_region: str = Field(default="north_indian")
    education_level: str = Field(default="college_educated")
    specific_concerns: List[str] = Field(default_factory=list)


class FamilyEducationResponse(BaseModel):
    educational_content: str
    recommended_resources: List[str] = Field(default_factory=list)


class CrisisDetectionRequest(BaseModel):
    conversation_history: List[Dict] = Field(...)


class CrisisDetectionResponse(BaseModel):
    crisis_score: float
    escalation_needed: bool
    detected_patterns: List[str] = Field(default_factory=list)

