
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
    mood_inference: Optional[Dict] = Field(default=None, description="Auto mood inference results")


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


class ConversationInfo(BaseModel):
    """Schema for conversation metadata."""
    conversation_id: str
    participants: List[str] = Field(default_factory=list)
    created_at: Optional[str] = None
    last_active_at: Optional[str] = None
    participant_count: int = 0


class ConversationsListResponse(BaseModel):
    """Schema for listing user conversations."""
    conversations: List[ConversationInfo] = Field(default_factory=list)
    total_count: int = 0


class MessageInfo(BaseModel):
    """Schema for chat message data."""
    message_id: str
    conversation_id: str
    sender_id: str
    text: str
    timestamp: str
    metadata: Dict = Field(default_factory=dict)
    mood_score: Optional[Dict[str, str]] = None


class ConversationMessagesResponse(BaseModel):
    """Schema for conversation messages with pagination."""
    conversation_id: str
    messages: List[MessageInfo] = Field(default_factory=list)
    message_count: int = 0
    limit: int = 50
    has_more: bool = False


class ConversationContextResponse(BaseModel):
    """Schema for recent conversation context for RAG."""
    context: List[MessageInfo] = Field(default_factory=list)
    formatted_context: str = Field(
        default="",
        description="Pre-formatted context string for AI prompt inclusion"
    )
    message_count: int = 0
    conversation_id: str
    limit: int = 10


# Student and Mood schemas for Feature 3
class StudentInfo(BaseModel):
    """Schema for student information."""
    user_id: str
    name: str
    email: str
    institution_name: Optional[str] = None
    region: Optional[str] = None
    age: Optional[str] = None
    language_preference: Optional[str] = None
    created_at: str


class StudentsListResponse(BaseModel):
    """Schema for listing students."""
    students: List[StudentInfo] = Field(default_factory=list)
    total_count: int = 0


class MoodEntry(BaseModel):
    """Schema for a mood entry."""
    mood_id: str
    mood: str = Field(..., description="Mood (happy, sad, anxious, etc.)")
    intensity: Optional[int] = Field(
        None, ge=1, le=10, description="Mood intensity (1-10)"
    )
    notes: Optional[str] = Field(None, description="Optional notes")
    timestamp: str
    created_at: str


class AddMoodRequest(BaseModel):
    """Schema for adding a new mood entry."""
    mood: str = Field(..., min_length=1, max_length=50, description="Mood")
    intensity: Optional[int] = Field(
        None, ge=1, le=10, description="Mood intensity (1-10)"
    )
    notes: Optional[str] = Field(None, max_length=500, description="Notes")


class AddMoodResponse(BaseModel):
    """Schema for mood addition response."""
    success: bool
    message: str
    mood_entry: MoodEntry


class MoodsListResponse(BaseModel):
    """Schema for listing student moods."""
    student_id: str
    moods: List[MoodEntry] = Field(default_factory=list)
    total_count: int = 0


# Privacy and Access Logging schemas for Feature 5
class PrivacyFlags(BaseModel):
    """Schema for privacy flags."""
    share_moods: bool = Field(True, description="Allow sharing moods")
    share_conversations: bool = Field(
        True, description="Allow sharing conversations"
    )


class UpdatePrivacyRequest(BaseModel):
    """Schema for updating privacy flags."""
    privacy_flags: PrivacyFlags


class UpdatePrivacyResponse(BaseModel):
    """Schema for privacy update response."""
    success: bool
    message: str
    privacy_flags: PrivacyFlags


class AccessLogEntry(BaseModel):
    """Schema for access log entry."""
    log_id: str
    resource: str
    action: str
    performed_by: str
    performed_by_role: str
    timestamp: str
    metadata: Dict[str, str] = Field(default_factory=dict)


class AccessLogsResponse(BaseModel):
    """Schema for access logs response."""
    student_id: str
    logs: List[AccessLogEntry] = Field(default_factory=list)
    total_count: int = 0


# Enhanced Mood Schemas for Feature 6
class UpdateMoodRequest(BaseModel):
    """Schema for updating student mood."""
    mood: str = Field(..., min_length=1, max_length=50, description="Mood")
    intensity: Optional[int] = Field(
        None, ge=1, le=10, description="Mood intensity (1-10)"
    )
    notes: Optional[str] = Field(None, max_length=500, description="Notes")


class CurrentMoodResponse(BaseModel):
    """Schema for current mood response."""
    mood_id: Optional[str] = None
    mood: Optional[str] = None
    intensity: Optional[int] = None
    notes: Optional[str] = None
    timestamp: Optional[str] = None
    created_at: Optional[str] = None


class MoodStreamEntry(BaseModel):
    """Schema for mood stream entry with student info."""
    mood_id: str
    student_id: str
    student_name: str
    mood: str
    intensity: Optional[int] = None
    timestamp: str


class MoodStreamResponse(BaseModel):
    """Schema for mood stream response."""
    mood_entries: List[MoodStreamEntry] = Field(default_factory=list)
    total_count: int = 0


class MoodAnalyticsResponse(BaseModel):
    """Schema for mood analytics response."""
    total_students: int
    students_with_mood_sharing: int
    total_mood_entries: int
    recent_mood_entries_24h: int
    mood_distribution: Dict[str, int] = Field(default_factory=dict)
    mood_percentages: Dict[str, float] = Field(default_factory=dict)
    average_moods_per_student: float
    most_common_mood: Optional[str] = None


# Emotion Analysis and Mood Inference Schemas
class EmotionAnalysisResponse(BaseModel):
    """Schema for emotion analysis results."""
    emotions: Dict[str, float] = Field(default_factory=dict)
    inferred_mood: str
    intensity: int = Field(ge=1, le=10)
    confidence: float = Field(ge=0.0, le=1.0)
    auto_updated: bool = False
    timestamp: str


class MoodInferenceRequest(BaseModel):
    """Schema for mood inference request."""
    message: str = Field(..., min_length=1, max_length=2000)
    language: str = Field(default="en")
    auto_update_enabled: bool = Field(default=True)


class MoodInferenceResponse(BaseModel):
    """Schema for mood inference response."""
    message_analyzed: str
    emotion_analysis: EmotionAnalysisResponse
    suggestion: str
    privacy_note: str
