"""Tests for Privacy Service - Feature 5"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.privacy_service import PrivacyService
from app.models.db_models import User


@pytest.fixture
def mock_firestore_service():
    """Mock FirestoreService for testing."""
    return MagicMock()


@pytest.fixture
def privacy_service(mock_firestore_service):
    """Privacy service with mocked dependencies."""
    return PrivacyService(mock_firestore_service)


@pytest.mark.asyncio
async def test_check_flags_user_not_found(privacy_service, mock_firestore_service):
    """Test privacy check when user doesn't exist."""
    mock_firestore_service.get_user = AsyncMock(return_value=None)
    
    result = await privacy_service.check_flags("nonexistent_user", "moods")
    
    assert result == {"allowed": False, "exists": False}
    mock_firestore_service.get_user.assert_called_once_with("nonexistent_user")


@pytest.mark.asyncio
async def test_check_flags_moods_allowed(privacy_service, mock_firestore_service):
    """Test privacy check for moods when sharing is allowed."""
    user = User(
        user_id="user123",
        email="test@example.com",
        privacy_flags={"share_moods": True, "share_conversations": False}
    )
    mock_firestore_service.get_user = AsyncMock(return_value=user)
    
    result = await privacy_service.check_flags("user123", "moods")
    
    assert result == {"allowed": True, "exists": True}


@pytest.mark.asyncio
async def test_check_flags_moods_denied(privacy_service, mock_firestore_service):
    """Test privacy check for moods when sharing is denied."""
    user = User(
        user_id="user123",
        email="test@example.com",
        privacy_flags={"share_moods": False, "share_conversations": True}
    )
    mock_firestore_service.get_user = AsyncMock(return_value=user)
    
    result = await privacy_service.check_flags("user123", "moods")
    
    assert result == {"allowed": False, "exists": True}


@pytest.mark.asyncio
async def test_check_flags_conversations_allowed(privacy_service, mock_firestore_service):
    """Test privacy check for conversations when sharing is allowed."""
    user = User(
        user_id="user123",
        email="test@example.com",
        privacy_flags={"share_moods": False, "share_conversations": True}
    )
    mock_firestore_service.get_user = AsyncMock(return_value=user)
    
    result = await privacy_service.check_flags("user123", "conversations")
    
    assert result == {"allowed": True, "exists": True}


@pytest.mark.asyncio
async def test_check_flags_default_values(privacy_service, mock_firestore_service):
    """Test privacy check with default privacy flags."""
    user = User(
        user_id="user123",
        email="test@example.com"
        # privacy_flags will use default factory values
    )
    mock_firestore_service.get_user = AsyncMock(return_value=user)
    
    result = await privacy_service.check_flags("user123", "moods")
    
    # Default should allow sharing
    assert result == {"allowed": True, "exists": True}


@pytest.mark.asyncio
async def test_check_flags_unknown_resource(privacy_service, mock_firestore_service):
    """Test privacy check for unknown resource type."""
    user = User(
        user_id="user123",
        email="test@example.com",
        privacy_flags={"share_moods": True, "share_conversations": True}
    )
    mock_firestore_service.get_user = AsyncMock(return_value=user)
    
    result = await privacy_service.check_flags("user123", "unknown_resource")
    
    assert result == {"allowed": False, "exists": True}


@pytest.mark.asyncio
async def test_update_privacy_flags_success(privacy_service, mock_firestore_service):
    """Test successful privacy flags update."""
    mock_firestore_service.update_user = AsyncMock()
    
    privacy_flags = {"share_moods": False, "share_conversations": True}
    result = await privacy_service.update_privacy_flags("user123", privacy_flags)
    
    assert result is True
    mock_firestore_service.update_user.assert_called_once_with(
        "user123", {"privacy_flags": privacy_flags}
    )


@pytest.mark.asyncio
async def test_update_privacy_flags_invalid_flags(privacy_service, mock_firestore_service):
    """Test privacy flags update with invalid flags."""
    invalid_flags = {"invalid_flag": True, "share_moods": False}
    result = await privacy_service.update_privacy_flags("user123", invalid_flags)
    
    assert result is False
    mock_firestore_service.update_user.assert_not_called()


@pytest.mark.asyncio
async def test_get_privacy_flags_success(privacy_service, mock_firestore_service):
    """Test getting privacy flags for existing user."""
    user = User(
        user_id="user123",
        email="test@example.com",
        privacy_flags={"share_moods": False, "share_conversations": True}
    )
    mock_firestore_service.get_user = AsyncMock(return_value=user)
    
    result = await privacy_service.get_privacy_flags("user123")
    
    assert result == {"share_moods": False, "share_conversations": True}


@pytest.mark.asyncio
async def test_get_privacy_flags_user_not_found(privacy_service, mock_firestore_service):
    """Test getting privacy flags for non-existent user."""
    mock_firestore_service.get_user = AsyncMock(return_value=None)
    
    result = await privacy_service.get_privacy_flags("nonexistent_user")
    
    assert result is None


@pytest.mark.asyncio
async def test_get_privacy_flags_default_values(privacy_service, mock_firestore_service):
    """Test getting privacy flags when user has default flags."""
    user = User(
        user_id="user123",
        email="test@example.com"
        # privacy_flags will use default factory values
    )
    mock_firestore_service.get_user = AsyncMock(return_value=user)
    
    result = await privacy_service.get_privacy_flags("user123")
    
    # Should return default values from the model
    expected = {"share_moods": True, "share_conversations": True}
    assert result == expected
