import pytest
from unittest.mock import MagicMock

from app.services.crisis import CrisisService

@pytest.fixture
def mock_firestore():
    client = MagicMock()
    coll = MagicMock()
    doc = MagicMock()
    doc.exists = True
    doc.to_dict.return_value = {
        "age": 17,
        "parent_escalation": True,
        "parent_contact": "+911234567890",
    }
    coll.document.return_value.get.return_value = doc
    client.collection.return_value = coll
    coll.stream.return_value = []
    return client

@pytest.fixture
def mock_gemini():
    svc = MagicMock()
    svc.analyze_risk.return_value = 9
    return svc

def test_keyword_only_high_risk_triggers(mock_firestore):
    crisis = CrisisService(firestore_client=mock_firestore)
    score = crisis.detect_keywords("I want to commit suicide")
    assert score == 6

def test_gemini_only_high_risk_triggers(mock_firestore, mock_gemini):
    crisis = CrisisService(firestore_client=mock_firestore, gemini_service=mock_gemini)
    score = crisis.assess_with_gemini("I feel hopeless")
    assert score == 9

def test_combined_scoring_triggers_escalation(mock_firestore, mock_gemini):
    crisis = CrisisService(firestore_client=mock_firestore, gemini_service=mock_gemini)
    report = crisis.assess_risk("user123", "I want to commit suicide")
    assert report["risk_score"] >= 7
    assert report["risk_level"] == "high"
    result = crisis.escalate("user123", report)
    assert result["action"] in ("tele_manas+parent", "tele_manas", "parent_whatsapp")

def test_cooldown_prevents_repeated_escalation(mock_firestore, mock_gemini):
    crisis = CrisisService(firestore_client=mock_firestore, gemini_service=mock_gemini)
    crisis.is_under_cooldown = MagicMock(return_value=True)
    report = crisis.assess_risk("user123", "I want to commit suicide")
    result = crisis.escalate("user123", report)
    assert result["status"] == "cooldown"

def test_consent_prevents_parent_whatsapp_for_adults(mock_firestore, mock_gemini):
    mock_firestore.collection.return_value.document.return_value.get.return_value.to_dict.return_value = {
        "age": 19,
        "parent_escalation": False,
        "parent_contact": "+911234567890",
    }
    crisis = CrisisService(firestore_client=mock_firestore, gemini_service=mock_gemini)
    report = crisis.assess_risk("user123", "I want to commit suicide")
    assert not crisis.should_escalate_to_parent(report["user_profile"], report["risk_score"])
