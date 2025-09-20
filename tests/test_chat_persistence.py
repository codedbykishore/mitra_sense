# tests/test_chat_persistence.py
"""
Unit tests for chat persistence functionality.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone
import uuid

from fastapi.testclient import TestClient
from app.main import app


class TestChatPersistence:
    """Test chat persistence functionality with mocked Firestore."""

    @pytest.fixture
    def client(self):
        return TestClient(app)



    @pytest.fixture
    def sample_chat_request(self):
        return {
            "text": "Mann nahi lag raha padhai mein",
            "context": {},
            "language": "hi",
            "region": "india",
            "max_rag_results": 3
        }

    @pytest.mark.asyncio
    async def test_create_or_update_conversation_new_user(self):
        """Test creating a new conversation for a user."""
        from app.services.firestore import FirestoreService
        
        # Mock Firestore client and methods
        with patch(
            'app.services.firestore.firestore.AsyncClient'
        ) as mock_client:
            firestore_service = FirestoreService()
            
            # Mock no existing conversations
            mock_query = AsyncMock()
            mock_query.stream.return_value = [].__aiter__()
            
            mock_collection = AsyncMock()
            mock_collection.where.return_value = mock_query
            mock_client.return_value.collection.return_value = mock_collection
            
            # Mock store_conversation
            with patch.object(
                firestore_service, 'store_conversation', new_callable=AsyncMock
            ) as mock_store:
                conversation_id = await (
                    firestore_service.create_or_update_conversation(
                        "test_user_123"
                    )
                )
                
                # Verify conversation was created
                assert conversation_id is not None
                assert isinstance(conversation_id, str)
                mock_store.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_or_update_conversation_existing_user(self):
        """Test returning existing conversation for a user."""
        from app.services.firestore import FirestoreService
        
        with patch(
            'app.services.firestore.firestore.AsyncClient'
        ) as mock_client:
            firestore_service = FirestoreService()
            
            # Mock existing conversation
            existing_conversation = {
                "conversation_id": "existing_conv_123",
                "participants": ["test_user_123"],
                "last_active_at": datetime.now(timezone.utc)
            }
            
            mock_doc = MagicMock()
            mock_doc.id = "existing_conv_123"
            mock_doc.to_dict.return_value = existing_conversation
            
            mock_query = AsyncMock()
            mock_query.stream.return_value = [mock_doc].__aiter__()
            
            mock_collection = AsyncMock()
            mock_collection.where.return_value = mock_query
            mock_client.return_value.collection.return_value = mock_collection
            
            # Mock update_conversation
            with patch.object(
                firestore_service, 'update_conversation', new_callable=AsyncMock
            ) as mock_update:
                conversation_id = await (
                    firestore_service.create_or_update_conversation(
                        "test_user_123"
                    )
                )
                
                # Verify existing conversation was returned and updated
                assert conversation_id == "existing_conv_123"
                mock_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_message(self):
        """Test saving a message to Firestore."""
        from app.services.firestore import FirestoreService
        
        with patch(
            'app.services.firestore.firestore.AsyncClient'
        ) as mock_client:
            firestore_service = FirestoreService()
            
            # Mock Firestore document operations
            mock_message_ref = AsyncMock()
            mock_doc = AsyncMock()
            mock_doc.collection.return_value.document.return_value = (
                mock_message_ref
            )
            mock_collection = AsyncMock()
            mock_collection.document.return_value = mock_doc
            mock_client.return_value.collection.return_value = mock_collection
            
            # Mock update_conversation
            with patch.object(
                firestore_service, 'update_conversation', new_callable=AsyncMock
            ) as mock_update:
                message_data = {
                    "message_id": "msg_123",
                    "conversation_id": "conv_123",
                    "sender_id": "test_user_123",
                    "text": "Test message",
                    "timestamp": datetime.now(timezone.utc),
                    "metadata": {
                        "source": "user",
                        "language": "en",
                        "embedding_id": None,
                        "emotion_score": "{}"
                    }
                }
                
                await firestore_service.save_message("conv_123", message_data)
                
                # Verify conversation was updated and message was saved
                mock_update.assert_called_once()
                mock_message_ref.set.assert_called_once_with(message_data)

    @patch('app.routes.input.firestore_service')
    @patch('app.routes.input.rag_service')
    @patch('app.routes.input.gemini_service')
    @patch('app.dependencies.auth.get_current_user_from_session')
    def test_chat_endpoint_persistence(
        self, mock_get_user, mock_gemini, mock_rag, mock_firestore, client, mock_user, sample_chat_request
    ):
        """Test that chat endpoint persists both user and AI messages."""
        
        # Mock user authentication
        mock_get_user.return_value = mock_user
        
        # Mock conversation creation
        mock_firestore.create_or_update_conversation = AsyncMock(return_value="conv_123")
        mock_firestore.save_message = AsyncMock()
        
        # Mock RAG service
        mock_rag.retrieve_with_metadata = AsyncMock(return_value=[])
        
        # Mock Gemini AI response
        mock_gemini.process_cultural_conversation = AsyncMock(
            return_value="मैं समझ सकता हूं कि आपका मन पढ़ाई में नहीं लग रहा। यह सामान्य बात है।"
        )
        
        # Mock language detection
        with patch('app.routes.input.detect') as mock_detect:
            mock_detect.return_value = "hi"
            
            # Make request to chat endpoint
            response = client.post("/api/v1/input/chat", json=sample_chat_request)
            
            # Verify response
            assert response.status_code == 200
            response_data = response.json()
            assert "response" in response_data
            
            # Verify persistence calls were made
            mock_firestore.create_or_update_conversation.assert_called_once_with(mock_user.user_id)
            
            # Verify two messages were saved (user + AI)
            assert mock_firestore.save_message.call_count == 2
            
            # Verify user message was saved correctly
            user_message_call = mock_firestore.save_message.call_args_list[0]
            user_message_data = user_message_call[0][1]
            assert user_message_data["sender_id"] == mock_user.user_id
            assert user_message_data["text"] == sample_chat_request["text"]
            assert user_message_data["metadata"]["source"] == "user"
            assert user_message_data["metadata"]["language"] == "hi"
            
            # Verify AI message was saved correctly
            ai_message_call = mock_firestore.save_message.call_args_list[1]
            ai_message_data = ai_message_call[0][1]
            assert ai_message_data["sender_id"] == "ai"
            assert ai_message_data["metadata"]["source"] == "ai"
            assert ai_message_data["metadata"]["language"] == "hi"

    def test_message_schema_structure(self):
        """Test that message data follows the required schema."""
        message_data = {
            "message_id": str(uuid.uuid4()),
            "conversation_id": str(uuid.uuid4()),
            "sender_id": "test_user_123",
            "text": "Test message",
            "timestamp": datetime.now(timezone.utc),
            "metadata": {
                "source": "user",
                "language": "en",
                "embedding_id": None,
                "emotion_score": "{\"anxious\": 0.5, \"sad\": 0.2}"
            },
            "mood_score": {"label": "calm", "score": 0.3}
        }
        
        # Verify all required fields are present
        required_fields = [
            "message_id", "conversation_id", "sender_id", 
            "text", "timestamp", "metadata"
        ]
        for field in required_fields:
            assert field in message_data
        
        # Verify metadata structure
        metadata = message_data["metadata"]
        assert "source" in metadata
        assert "language" in metadata
        assert "embedding_id" in metadata
        assert "emotion_score" in metadata
        
        # Verify sender_id is valid
        assert message_data["sender_id"] in ["test_user_123", "ai"]
        
        # Verify source is valid
        assert metadata["source"] in ["user", "ai"]

    def test_conversation_schema_structure(self):
        """Test that conversation data follows the required schema."""
        conversation_data = {
            "conversation_id": str(uuid.uuid4()),
            "participants": ["test_user_123"],
            "created_at": datetime.now(timezone.utc),
            "last_active_at": datetime.now(timezone.utc)
        }
        
        # Verify all required fields are present
        required_fields = [
            "conversation_id", "participants", 
            "created_at", "last_active_at"
        ]
        for field in required_fields:
            assert field in conversation_data
        
        # Verify participants is a list
        assert isinstance(conversation_data["participants"], list)
        assert len(conversation_data["participants"]) > 0
        
        # Verify timestamps are datetime objects
        assert isinstance(conversation_data["created_at"], datetime)
        assert isinstance(conversation_data["last_active_at"], datetime)
