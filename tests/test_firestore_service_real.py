# tests/_test_firestore_service_real.py
import pytest
from datetime import datetime, UTC
from app.services.firestore import FirestoreService
from app.models.db_models import User, Conversation


@pytest.mark.asyncio
async def test_create_and_get_user():
    firestore_service = FirestoreService()

    user = User(
        user_id="testuser123",
        email="test@example.com",
        hashed_password="hashedpassword",
        created_at=datetime.now(UTC),
    )
    await firestore_service.create_user(user)

    fetched_user = await firestore_service.get_user("testuser123")
    assert fetched_user is not None
    assert fetched_user.user_id == "testuser123"
    assert fetched_user.email == "test@example.com"


@pytest.mark.asyncio
async def test_store_and_get_conversation():
    fs = FirestoreService()

    conv = Conversation(
        conversation_id="convtest123",
        user_id="testuser123",
        messages=[{"text": "hello"}],
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    await fs.store_conversation(conv)

    fetched_conv = await fs.get_conversation("convtest123")
    assert fetched_conv is not None
    assert fetched_conv.conversation_id == "convtest123"


@pytest.mark.asyncio
async def test_add_message_to_conversation():
    fs = FirestoreService()
    conv_id = "convtest123"

    message = {"text": "New message", "timestamp": datetime.now(UTC).isoformat()}
    await fs.add_message_to_conversation(conv_id, message)

    conv = await fs.get_conversation(conv_id)
    assert any(msg["text"] == "New message" for msg in conv.messages)
