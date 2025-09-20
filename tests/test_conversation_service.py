import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from app.services.conversation_service import ConversationService


class TestConversationService:
    """Test the new ConversationService functionality."""

    @pytest.mark.asyncio
    async def test_get_recent_context_basic(self):
        """Test basic get_recent_context functionality."""
        conversation_service = ConversationService()
        
        # Mock the FirestoreService dependency
        with patch.object(conversation_service, 'firestore_service') as mock_firestore:
            # Mock conversation exists
            mock_conversation = MagicMock()
            mock_conversation.conversation_id = "test_conv_123"
            mock_conversation.participants = ["user_123"]
            mock_firestore.get_conversation.return_value = mock_conversation
            
            # Mock message query results
            mock_messages = [
                {
                    "message_id": "msg_1",
                    "conversation_id": "test_conv_123",
                    "sender_id": "user_123",
                    "text": "First message",
                    "timestamp": datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
                    "metadata": {"source": "user"}
                },
                {
                    "message_id": "msg_2",
                    "conversation_id": "test_conv_123",
                    "sender_id": "ai",
                    "text": "AI response",
                    "timestamp": datetime(2025, 1, 1, 10, 1, 0, tzinfo=timezone.utc),
                    "metadata": {"source": "ai"}
                },
                {
                    "message_id": "msg_3",
                    "conversation_id": "test_conv_123",
                    "sender_id": "user_123",
                    "text": "Latest message",
                    "timestamp": datetime(2025, 1, 1, 10, 2, 0, tzinfo=timezone.utc),
                    "metadata": {"source": "user"}
                }
            ]
            
            # Mock the Firestore query chain
            mock_doc_1 = MagicMock()
            mock_doc_1.to_dict.return_value = mock_messages[2]  # Latest first
            mock_doc_2 = MagicMock()
            mock_doc_2.to_dict.return_value = mock_messages[1]
            mock_doc_3 = MagicMock()
            mock_doc_3.to_dict.return_value = mock_messages[0]
            
            async def mock_stream():
                yield mock_doc_1
                yield mock_doc_2
                yield mock_doc_3
            
            mock_query = MagicMock()
            mock_query.stream.return_value = mock_stream()
            
            mock_collection = MagicMock()
            mock_collection.order_by.return_value.limit.return_value = mock_query
            
            mock_document = MagicMock()
            mock_document.collection.return_value = mock_collection
            
            mock_firestore.db.collection.return_value.document.return_value = mock_document
            
            # Call the method
            result = await conversation_service.get_recent_context("test_conv_123", 3)
            
            # Verify results are in ascending order (oldest → newest)
            assert len(result) == 3
            assert result[0]["text"] == "First message"
            assert result[1]["text"] == "AI response"
            assert result[2]["text"] == "Latest message"
            
            # Verify firestore calls
            mock_firestore.get_conversation.assert_called_once_with("test_conv_123")

    @pytest.mark.asyncio
    async def test_format_context_for_rag(self):
        """Test formatting messages for RAG context."""
        conversation_service = ConversationService()
        
        messages = [
            {
                "message_id": "msg_1",
                "sender_id": "user_123",
                "text": "I'm feeling anxious",
                "timestamp": datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
                "mood_score": {"anxiety": "0.8"}
            },
            {
                "message_id": "msg_2",
                "sender_id": "ai",
                "text": "I understand you're feeling anxious. Can you tell me more?",
                "timestamp": datetime(2025, 1, 1, 10, 1, 0, tzinfo=timezone.utc),
            }
        ]
        
        # Test basic formatting
        formatted = await conversation_service.format_context_for_rag(messages, include_metadata=False)
        
        expected_lines = [
            "Recent conversation context:",
            "User: I'm feeling anxious",
            "AI Assistant: I understand you're feeling anxious. Can you tell me more?",
            ""
        ]
        assert formatted == "\n".join(expected_lines)
        
        # Test with metadata
        formatted_with_meta = await conversation_service.format_context_for_rag(messages, include_metadata=True)
        
        assert "User: I'm feeling anxious" in formatted_with_meta
        assert "[Time:" in formatted_with_meta
        assert "[Mood:" in formatted_with_meta

    @pytest.mark.asyncio
    async def test_validate_user_access(self):
        """Test user access validation."""
        conversation_service = ConversationService()
        
        with patch.object(conversation_service, 'firestore_service') as mock_firestore:
            # Mock conversation with participants
            mock_conversation = MagicMock()
            mock_conversation.participants = ["user_123", "user_456"]
            mock_firestore.get_conversation.return_value = mock_conversation
            
            # Test valid user
            has_access = await conversation_service.validate_user_access("conv_123", "user_123")
            assert has_access is True
            
            # Test invalid user
            has_access = await conversation_service.validate_user_access("conv_123", "user_789")
            assert has_access is False
            
            # Test nonexistent conversation
            mock_firestore.get_conversation.return_value = None
            has_access = await conversation_service.validate_user_access("conv_123", "user_123")
            assert has_access is False

    @pytest.mark.asyncio
    async def test_get_recent_context_empty_conversation(self):
        """Test get_recent_context with empty conversation."""
        conversation_service = ConversationService()
        
        with patch.object(conversation_service, 'firestore_service') as mock_firestore:
            # Mock conversation exists but no messages
            mock_conversation = MagicMock()
            mock_firestore.get_conversation.return_value = mock_conversation
            
            async def mock_empty_stream():
                return
                yield  # This will never execute
            
            mock_query = MagicMock()
            mock_query.stream.return_value = mock_empty_stream()
            
            mock_collection = MagicMock()
            mock_collection.order_by.return_value.limit.return_value = mock_query
            
            mock_document = MagicMock()
            mock_document.collection.return_value = mock_collection
            
            mock_firestore.db.collection.return_value.document.return_value = mock_document
            
            result = await conversation_service.get_recent_context("test_conv_123", 10)
            
            assert result == []

    @pytest.mark.asyncio
    async def test_get_recent_context_nonexistent_conversation(self):
        """Test get_recent_context with nonexistent conversation."""
        conversation_service = ConversationService()
        
        with patch.object(conversation_service, 'firestore_service') as mock_firestore:
            # Mock conversation does not exist
            mock_firestore.get_conversation.return_value = None
            
            result = await conversation_service.get_recent_context("nonexistent_conv", 10)
            
            assert result == []
            mock_firestore.get_conversation.assert_called_once_with("nonexistent_conv")


if __name__ == "__main__":
    pytest.main([__file__])
