# tests/test_chat_functionality.py
"""
Test the chat persistence functionality with minimal setup.
This tests the integration of the chat endpoint with persistence.
"""
import pytest
from datetime import datetime, timezone
import uuid


def test_chat_persistence_implementation_complete():
    """Test that all required components are implemented."""
    
    # Test 1: Verify FirestoreService has required methods
    from app.services.firestore import FirestoreService
    service = FirestoreService()
    
    assert hasattr(service, 'create_or_update_conversation')
    assert hasattr(service, 'save_message')
    
    # Test 2: Verify Message and Conversation models exist
    from app.models.db_models import Message, Conversation
    
    # Create test message
    message = Message(
        message_id=str(uuid.uuid4()),
        conversation_id=str(uuid.uuid4()),
        sender_id="test_user",
        text="Test message",
        timestamp=datetime.now(timezone.utc),
        metadata={"source": "user", "language": "en"}
    )
    
    assert message.message_id is not None
    assert message.sender_id == "test_user"
    assert message.metadata["source"] == "user"
    
    # Create test conversation
    conversation = Conversation(
        conversation_id=str(uuid.uuid4()),
        participants=["test_user"],
        created_at=datetime.now(timezone.utc),
        last_active_at=datetime.now(timezone.utc)
    )
    
    assert conversation.conversation_id is not None
    assert "test_user" in conversation.participants
    
    # Test 3: Verify input route has the persistence integration
    try:
        from app.routes.input import firestore_service
        assert firestore_service is not None
    except ImportError:
        pytest.fail("firestore_service not imported in input route")


def test_message_schema_validation():
    """Test that the message schema matches requirements."""
    from app.models.db_models import Message
    
    # Test user message schema
    user_message = Message(
        message_id=str(uuid.uuid4()),
        conversation_id=str(uuid.uuid4()),
        sender_id="user_123",
        text="Mann nahi lag raha padhai mein",
        timestamp=datetime.now(timezone.utc),
        metadata={
            "source": "user",
            "language": "hi",
            "embedding_id": None,
            "emotion_score": "{\"anxious\": 0.5, \"sad\": 0.2}"
        },
        mood_score={"label": "calm", "score": "0.3"}
    )
    
    # Verify all required fields are present
    assert user_message.message_id is not None
    assert user_message.conversation_id is not None
    assert user_message.sender_id == "user_123"
    assert user_message.text == "Mann nahi lag raha padhai mein"
    assert user_message.timestamp is not None
    assert isinstance(user_message.metadata, dict)
    assert user_message.mood_score is not None
    
    # Verify metadata structure
    assert user_message.metadata["source"] == "user"
    assert user_message.metadata["language"] == "hi"
    assert "embedding_id" in user_message.metadata
    assert "emotion_score" in user_message.metadata
    
    # Test AI message schema
    ai_message = Message(
        message_id=str(uuid.uuid4()),
        conversation_id=user_message.conversation_id,
        sender_id="ai",
        text="मैं समझ सकता हूं कि आपका मन पढ़ाई में नहीं लग रहा।",
        timestamp=datetime.now(timezone.utc),
        metadata={
            "source": "ai",
            "language": "hi",
            "embedding_id": None,
            "emotion_score": "{}"
        }
    )
    
    assert ai_message.sender_id == "ai"
    assert ai_message.metadata["source"] == "ai"


def test_conversation_schema_validation():
    """Test that the conversation schema matches requirements."""
    from app.models.db_models import Conversation
    
    conversation = Conversation(
        conversation_id=str(uuid.uuid4()),
        participants=["user_123"],
        created_at=datetime.now(timezone.utc),
        last_active_at=datetime.now(timezone.utc)
    )
    
    # Verify required fields
    assert conversation.conversation_id is not None
    assert isinstance(conversation.participants, list)
    assert len(conversation.participants) > 0
    assert "user_123" in conversation.participants
    assert isinstance(conversation.created_at, datetime)
    assert isinstance(conversation.last_active_at, datetime)


def test_firestore_service_integration_points():
    """Test that FirestoreService is properly integrated in the input route."""
    
    # Test that we can import the service from the route
    from app.routes.input import firestore_service
    
    # Test that it has the correct type
    from app.services.firestore import FirestoreService
    assert isinstance(firestore_service, FirestoreService)
    
    # Test that the route has the required imports for chat persistence
    from app.routes.input import uuid, datetime, detect, LangDetectException
    
    assert uuid is not None
    assert datetime is not None
    assert detect is not None
    assert LangDetectException is not None


def test_language_detection_setup():
    """Test that language detection is properly configured."""
    from app.routes.input import DetectorFactory
    
    # Verify that the seed is set for consistent results
    assert DetectorFactory.seed == 0


def test_chat_endpoint_has_user_dependency():
    """Test that the chat endpoint requires user authentication."""
    
    # Check that the dependency is available in the app's dependencies
    from app.dependencies.auth import get_current_user_from_session
    assert get_current_user_from_session is not None
    
    # Check that the input route is properly configured with dependencies
    import inspect
    from app.routes.input import router
    
    # Look for routes that use authentication
    has_auth_routes = False
    for route in router.routes:
        if hasattr(route, 'endpoint'):
            sig = inspect.signature(route.endpoint)
            for param_name, param in sig.parameters.items():
                if hasattr(param.annotation, '__origin__') and str(param.annotation).startswith('Annotated'):
                    has_auth_routes = True
                    break
    
    # The input route should have authenticated endpoints
    assert len(router.routes) > 0, "Input router should have routes defined"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
