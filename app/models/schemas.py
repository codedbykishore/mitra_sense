
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


class RAGQuery(BaseModel):
    """Schema for RAG query parameters"""
    query: str = Field(..., description="The search query")
    language: str = Field("en", description="Language code (e.g., 'en', 'hi')")
    region: Optional[str] = Field(
        None,
        description="Region code (e.g., 'north_india', 'south_india')",
        example="north_india"
    )
    tags: Optional[List[str]] = Field(
        None,
        description="List of tags to filter by",
        example=["cultural", "coping"]
    )
    max_results: int = Field(
        5,
        ge=1,
        le=20,
        description="Maximum number of results to return"
    )
    min_score: float = Field(
        0.6,
        ge=0.0,
        le=1.0,
        description="Minimum relevance score (0-1)"
    )


class RAGResponse(BaseModel):
    """Schema for RAG response items"""
    text: str = Field(..., description="The retrieved text content")
    title: str = Field(..., description="Title of the document")
    source: str = Field(..., description="Source of the document")
    language: str = Field(..., description="Language of the document")
    region: str = Field(..., description="Region the document is relevant for")
    tags: List[str] = Field(..., description="Tags associated with the document")
    sensitivity: str = Field(..., description="Sensitivity level of the content")
    relevance_score: float = Field(
        ...,
        description="Relevance score (0-1)",
        ge=0.0,
        le=1.0
    )


class UserRole(str, Enum):
    STUDENT = "student"
    INSTITUTION = "institution"


class OnboardingRequest(BaseModel):
    role: UserRole = Field(
        ..., description="User role: student or institution"
    )
    profile: Dict[str, str] = Field(
        ...,
        description="Profile data based on role"
    )
    institution_id: Optional[str] = Field(
        None,
        description="Institution ID for students (null for No Institution)"
    )
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "role": "student",
                    "profile": {
                        "name": "Priya Sharma",
                        "age": "20",
                        "region": "North India",
                        "language_preference": "hi-IN"
                    },
                    "institution_id": "inst_123"
                },
                {
                    "role": "institution",
                    "profile": {
                        "institution_name": "Delhi University",
                        "contact_person": "Dr. Rajesh Kumar",
                        "region": "North India"
                    }
                }
            ]
        }


class OnboardingResponse(BaseModel):
    success: bool
    message: str
    user_profile: Dict[str, str] = Field(default_factory=dict)


class InstitutionInfo(BaseModel):
    institution_id: str
    institution_name: str
    region: str
    student_count: int = 0
    active: bool = True


class InstitutionsListResponse(BaseModel):
    institutions: List[InstitutionInfo] = Field(default_factory=list)
