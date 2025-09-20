# tests/test_chat_history_real.py
"""
Integration tests for chat history functionality with real Firestore.
These tests require actual GCP credentials and will create/delete test data.
"""
import pytest
import pytest_asyncio
from datetime import datetime, timezone
from app.services.firestore import FirestoreService
from app.models.db_models import User, Conversation
import uuid
import asyncio


@pytest.mark.integration
class TestChatHistoryIntegration:
    """Integration tests with real Firestore database."""

    @pytest_asyncio.fixture
    async def firestore_service(self):
        """Create a real FirestoreService instance."""
        return FirestoreService()

    @pytest_asyncio.fixture
    async def test_user(self, firestore_service):
        """Create a test user and clean it up after the test."""
        user_id = f"test_chat_history_{uuid.uuid4().hex[:8]}"
        user = User(
            user_id=user_id,
            email=f"{user_id}@test.com",
            name="Test Chat History User",
            onboarding_completed=True,
            role="student"
        )
        
        # Create user in Firestore
        await firestore_service.create_user(user)
        
        yield user
        
        # Cleanup: Delete user after test
        try:
            await firestore_service.delete_user(user_id)
        except Exception:
            pass  # Ignore cleanup errors

    @pytest_asyncio.fixture
    async def test_conversation(self, firestore_service, test_user):
        """Create a test conversation and clean it up after the test."""
        conversation_id = f"test_conv_{uuid.uuid4().hex[:8]}"
        conversation = Conversation(
            conversation_id=conversation_id,
            participants=[test_user.user_id],
            created_at=datetime.now(timezone.utc),
            last_active_at=datetime.now(timezone.utc)
        )
        
        # Create conversation in Firestore
        await firestore_service.store_conversation(conversation)
        
        yield conversation
        
        # Cleanup: Delete conversation and its messages
        try:
            await firestore_service.delete_conversation(conversation_id)
        except Exception:
            pass  # Ignore cleanup errors

    @pytest.mark.asyncio
    async def test_save_and_retrieve_messages_real(
        self, firestore_service, test_conversation
    ):
        """Test saving and retrieving messages with real Firestore."""
        conversation_id = test_conversation.conversation_id
        
        # Save test messages
        messages_data = [
            {
                "message_id": f"msg_1_{uuid.uuid4().hex[:4]}",
                "conversation_id": conversation_id,
                "sender_id": test_conversation.participants[0],
                "text": "Hello, I need help with stress",
                "timestamp": datetime.now(timezone.utc),
                "metadata": {}
            },
            {
                "message_id": f"msg_2_{uuid.uuid4().hex[:4]}",
                "conversation_id": conversation_id,
                "sender_id": "ai",
                "text": "I'm here to help. Tell me more about your stress.",
                "timestamp": datetime.now(timezone.utc),
                "metadata": {"crisis_score": 0.1}
            }
        ]
        
        # Save messages to Firestore
        for message_data in messages_data:
            await firestore_service.save_message(conversation_id, message_data)
        
        # Small delay to ensure Firestore consistency
        await asyncio.sleep(1)
        
        # Retrieve messages
        retrieved_messages = await firestore_service.get_messages(
            conversation_id, limit=10
        )
        
        # Verify messages were saved and retrieved correctly
        assert len(retrieved_messages) == 2
        
        # Verify message content
        message_texts = [msg["text"] for msg in retrieved_messages]
        assert "Hello, I need help with stress" in message_texts
        assert "I'm here to help. Tell me more about your stress." in message_texts
        
        # Verify messages are ordered by timestamp (ascending)
        timestamps = [msg["timestamp"] for msg in retrieved_messages]
        assert timestamps == sorted(timestamps)

    @pytest.mark.asyncio
    async def test_get_user_conversations_real(
        self, firestore_service, test_user, test_conversation
    ):
        """Test retrieving user conversations with real Firestore."""
        # Small delay to ensure Firestore consistency
        await asyncio.sleep(1)
        
        # Retrieve user's conversations
        conversations = await firestore_service.get_user_conversations(
            test_user.user_id
        )
        
        # Verify the test conversation is returned
        assert len(conversations) >= 1
        
        # Find our test conversation
        test_conv_found = False
        for conv in conversations:
            if conv["conversation_id"] == test_conversation.conversation_id:
                test_conv_found = True
                assert test_user.user_id in conv["participants"]
                assert "created_at" in conv
                assert "last_active_at" in conv
                break
        
        assert test_conv_found, "Test conversation not found in user's conversations"

    @pytest.mark.asyncio
    async def test_conversation_access_control_real(
        self, firestore_service, test_user
    ):
        """Test that users can only access their own conversations."""
        # Create another user
        other_user_id = f"other_user_{uuid.uuid4().hex[:8]}"
        other_user = User(
            user_id=other_user_id,
            email=f"{other_user_id}@test.com",
            name="Other Test User"
        )
        await firestore_service.create_user(other_user)
        
        # Create conversation for other user only
        other_conversation_id = f"other_conv_{uuid.uuid4().hex[:8]}"
        other_conversation = Conversation(
            conversation_id=other_conversation_id,
            participants=[other_user_id],  # Only other user
            created_at=datetime.now(timezone.utc),
            last_active_at=datetime.now(timezone.utc)
        )
        await firestore_service.store_conversation(other_conversation)
        
        try:
            # Small delay for consistency
            await asyncio.sleep(1)
            
            # Test user should not see other user's conversation
            user_conversations = await firestore_service.get_user_conversations(
                test_user.user_id
            )
            
            other_conv_ids = [
                conv["conversation_id"] for conv in user_conversations
            ]
            assert other_conversation_id not in other_conv_ids
            
        finally:
            # Cleanup
            try:
                await firestore_service.delete_user(other_user_id)
                await firestore_service.delete_conversation(other_conversation_id)
            except Exception:
                pass  # Ignore cleanup errors

    @pytest.mark.asyncio
    async def test_empty_conversation_messages_real(
        self, firestore_service, test_conversation
    ):
        """Test retrieving messages from conversation with no messages."""
        # Don't add any messages, just try to retrieve
        messages = await firestore_service.get_messages(
            test_conversation.conversation_id
        )
        
        # Should return empty list
        assert messages == []

    @pytest.mark.asyncio
    async def test_message_limit_real(
        self, firestore_service, test_conversation
    ):
        """Test message retrieval with limit parameter."""
        conversation_id = test_conversation.conversation_id
        
        # Create 5 test messages
        for i in range(5):
            message_data = {
                "message_id": f"msg_{i}_{uuid.uuid4().hex[:4]}",
                "conversation_id": conversation_id,
                "sender_id": test_conversation.participants[0],
                "text": f"Test message {i}",
                "timestamp": datetime.now(timezone.utc),
                "metadata": {}
            }
            await firestore_service.save_message(conversation_id, message_data)
        
        # Small delay for consistency
        await asyncio.sleep(1)
        
        # Retrieve with limit of 3
        messages = await firestore_service.get_messages(
            conversation_id, limit=3
        )
        
        # Should return exactly 3 messages
        assert len(messages) == 3
        
        # Verify they're ordered by timestamp
        timestamps = [msg["timestamp"] for msg in messages]
        assert timestamps == sorted(timestamps)


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "-m", "integration"])
