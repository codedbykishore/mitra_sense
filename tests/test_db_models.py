from datetime import datetime, timezone
import pytest
from app.models.db_models import AnonymousUser, Conversation, PeerCircle, CrisisAlert


def test_anonymous_user_model():
    user = AnonymousUser(
        user_id="user123",
        cultural_background="indian_general",
        preferred_language="hi",
        age_group="18-25",
        created_at=datetime.now(timezone.utc),
        privacy_settings={"share_data": False},
    )
    assert user.user_id == "user123"
    assert "share_data" in user.privacy_settings
    json_data = user.model_dump_json()
    assert isinstance(json_data, str)


def test_conversation_model():
    conv = Conversation(
        conversation_id="conv123",
        user_id="user123",
        messages=[{"text": "hello"}],
        crisis_score=0.1,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    assert conv.messages[0]["text"] == "hello"
    dict_rep = conv.model_dump()
    assert "messages" in dict_rep


def test_peer_circle_model():
    circle = PeerCircle(
        circle_id="circle123",
        participants=["user123", "user456"],
        cultural_match_score=0.85,
        topic_category="anxiety",
        active_status=True,
        created_at=datetime.now(timezone.utc),
    )
    assert circle.active_status
    assert len(circle.participants) == 2


def test_crisis_alert_model():
    alert = CrisisAlert(
        alert_id="alert123",
        user_id="user123",
        crisis_score=0.9,
        detected_patterns=["anxiety", "panic"],
        escalation_status="pending",
        tele_manas_notified=False,
        created_at=datetime.now(timezone.utc),
    )
    assert alert.escalation_status == "pending"
    assert "panic" in alert.detected_patterns
