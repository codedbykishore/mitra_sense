import pytest
from app.models.schemas import (ChatRequest, ChatResponse, PeerMatchRequest, FamilyEducationRequest, CrisisDetectionRequest)

def test_chat_request_valid():
    req = ChatRequest(message="Hello", language="en-US")
    assert req.message == "Hello"
    assert req.language.value == "en-US"

def test_chat_response_serialization():
    resp = ChatResponse(
        response="Hi there",
        emotion_detected={"calmness": 0.8},
        crisis_score=0.1,
        rag_sources=["source1"],
        suggested_actions=["breathe deeply"],
        cultural_adaptations={"tone": "empathetic"}
    )
    json_data = resp.json()
    assert '"Hi there"' in json_data

def test_peer_match_request_defaults():
    req = PeerMatchRequest()
    assert req.cultural_background == "indian_general"
    assert req.support_type == "general"

def test_family_education_request_validation():
    req = FamilyEducationRequest(family_type="joint", cultural_region="south_indian", education_level="high_school")
    assert req.family_type == "joint"
    assert req.cultural_region == "south_indian"

def test_crisis_detection_request():
    req = CrisisDetectionRequest(conversation_history=[{"text": "I feel anxious"}])
    assert len(req.conversation_history) == 1
