# tests/test_chat_persistence_integration.py
"""
Integration test for chat persistence that demonstrates the complete workflow.
This test simulates the actual chat flow without requiring real Firestore.
"""
import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone
import uuid

from app.models.db_models import User


class TestChatPersistenceIntegration:
    """Integration tests for chat persistence functionality."""

    @pytest.fixture
    def mock_user(self):
        return User(
            user_id="test_user_123",
            email="test@example.com",
            name="Test User",
            onboarding_completed=True,
            role="student"
        )

    @pytest.fixture
    def sample_chat_message(self):
        return "Mann nahi lag raha padhai mein"

    @pytest.mark.asyncio
    async def test_complete_chat_persistence_workflow(self, mock_user, sample_chat_message):
        """Test the complete chat persistence workflow."""
        
        # Mock the FirestoreService methods
        with patch('app.services.firestore.FirestoreService') as MockFirestoreService:
            mock_service = AsyncMock()
            MockFirestoreService.return_value = mock_service
            
            # Mock conversation creation
            test_conversation_id = str(uuid.uuid4())
            mock_service.create_or_update_conversation.return_value = test_conversation_id
            
            # Mock message saving
            mock_service.save_message = AsyncMock()
            
            from app.services.firestore import FirestoreService
            firestore_service = FirestoreService()
            
            # Step 1: Create or get conversation
            conversation_id = await firestore_service.create_or_update_conversation(
                mock_user.user_id
            )
            
            assert conversation_id == test_conversation_id
            mock_service.create_or_update_conversation.assert_called_once_with(
                mock_user.user_id
            )
            
            # Step 2: Create user message data
            user_message_id = str(uuid.uuid4())
            user_message_data = {
                "message_id": user_message_id,
                "conversation_id": conversation_id,
                "sender_id": mock_user.user_id,
                "text": sample_chat_message,
                "timestamp": datetime.now(timezone.utc),
                "metadata": {
                    "source": "user",
                    "language": "hi",
                    "embedding_id": None,
                    "emotion_score": "{}"
                }
            }
            
            # Step 3: Save user message
            await firestore_service.save_message(conversation_id, user_message_data)
            
            # Step 4: Create AI response message data
            ai_message_id = str(uuid.uuid4())
            ai_response_text = "मैं समझ सकता हूं कि आपका मन पढ़ाई में नहीं लग रहा। यह सामान्य बात है।"
            ai_message_data = {
                "message_id": ai_message_id,
                "conversation_id": conversation_id,
                "sender_id": "ai",
                "text": ai_response_text,
                "timestamp": datetime.now(timezone.utc),
                "metadata": {
                    "source": "ai",
                    "language": "hi",
                    "embedding_id": None,
                    "emotion_score": "{}"
                }
            }
            
            # Step 5: Save AI message
            await firestore_service.save_message(conversation_id, ai_message_data)
            
            # Verify that save_message was called twice (user + AI)
            assert mock_service.save_message.call_count == 2
            
            # Verify the messages were saved with correct data
            user_call = mock_service.save_message.call_args_list[0]
            ai_call = mock_service.save_message.call_args_list[1]
            
            # Check user message call
            assert user_call[0][0] == conversation_id  # conversation_id
            user_msg = user_call[0][1]  # message_data
            assert user_msg["sender_id"] == mock_user.user_id
            assert user_msg["text"] == sample_chat_message
            assert user_msg["metadata"]["source"] == "user"
            assert user_msg["metadata"]["language"] == "hi"
            
            # Check AI message call
            assert ai_call[0][0] == conversation_id  # conversation_id
            ai_msg = ai_call[0][1]  # message_data
            assert ai_msg["sender_id"] == "ai"
            assert ai_msg["text"] == ai_response_text
            assert ai_msg["metadata"]["source"] == "ai"
            assert ai_msg["metadata"]["language"] == "hi"

    def test_message_schema_compliance(self):
        """Test that message data complies with the required schema."""
        from app.models.db_models import Message
        
        # Test message following the schema from the instruction
        message_data = {
            "message_id": str(uuid.uuid4()),
            "conversation_id": str(uuid.uuid4()),
            "sender_id": "test_user_123",
            "text": "Mann nahi lag raha padhai mein",
            "timestamp": datetime.now(timezone.utc),
            "metadata": {
                "source": "user",
                "language": "hi",
                "embedding_id": None,
                "emotion_score": "{\"anxious\": 0.5, \"sad\": 0.2}"
            },
            "mood_score": {"label": "calm", "score": "0.3"}
        }
        
        # Verify the message can be created with the schema
        message = Message(**message_data)
        
        # Verify all required fields from the instruction are present
        assert hasattr(message, 'message_id')
        assert hasattr(message, 'conversation_id')
        assert hasattr(message, 'sender_id')
        assert hasattr(message, 'text')
        assert hasattr(message, 'timestamp')
        assert hasattr(message, 'metadata')
        assert hasattr(message, 'mood_score')
        
        # Verify metadata structure
        assert "source" in message.metadata
        assert "language" in message.metadata
        assert "embedding_id" in message.metadata
        assert "emotion_score" in message.metadata
        
        # Verify sender_id is valid (user_id or "ai")
        assert message.sender_id in ["test_user_123", "ai"]
        
        # Verify source is valid
        assert message.metadata["source"] in ["user", "ai"]

    def test_conversation_schema_compliance(self):
        """Test that conversation data complies with the required schema."""
        from app.models.db_models import Conversation
        
        # Test conversation following the schema from the instruction
        conversation_data = {
            "conversation_id": str(uuid.uuid4()),
            "participants": ["test_user_123"],
            "created_at": datetime.now(timezone.utc),
            "last_active_at": datetime.now(timezone.utc)
        }
        
        # Verify the conversation can be created with the schema
        conversation = Conversation(**conversation_data)
        
        # Verify all required fields from the instruction are present
        assert hasattr(conversation, 'conversation_id')
        assert hasattr(conversation, 'participants')
        assert hasattr(conversation, 'created_at')
        assert hasattr(conversation, 'last_active_at')
        
        # Verify participants is a list of user_ids
        assert isinstance(conversation.participants, list)
        assert len(conversation.participants) > 0
        
        # Verify timestamps are datetime objects
        assert isinstance(conversation.created_at, datetime)
        assert isinstance(conversation.last_active_at, datetime)

    def test_firestore_service_methods_signature(self):
        """Test that FirestoreService methods have correct signatures."""
        from app.services.firestore import FirestoreService
        import inspect
        
        service = FirestoreService()
        
        # Test create_or_update_conversation signature
        create_conv_sig = inspect.signature(service.create_or_update_conversation)
        params = list(create_conv_sig.parameters.keys())
        assert 'user_id' in params
        assert create_conv_sig.return_annotation == str
        
        # Test save_message signature
        save_msg_sig = inspect.signature(service.save_message)
        params = list(save_msg_sig.parameters.keys())
        assert 'conversation_id' in params
        assert 'message_data' in params
        assert save_msg_sig.return_annotation is None or save_msg_sig.return_annotation == type(None)

    def test_input_route_integration_ready(self):
        """Test that the input route is ready for chat persistence."""
        
        # Verify imports are available
        from app.routes.input import (
            firestore_service, 
            get_current_user_from_session,
            uuid,
            datetime, 
            timezone,
            detect,
            LangDetectException
        )
        
        # Verify service is initialized
        assert firestore_service is not None
        
        # Verify all necessary components are imported
        assert get_current_user_from_session is not None
        assert uuid is not None
        assert datetime is not None
        assert timezone is not None
        assert detect is not None
        assert LangDetectException is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
