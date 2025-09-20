"""Tests for Logging Service - Feature 5"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.logging_service import LoggingService
from app.models.db_models import AccessLog


@pytest.fixture
def mock_firestore_service():
    """Mock FirestoreService for testing."""
    mock_service = MagicMock()
    mock_service.db = MagicMock()
    mock_service.db.collection.return_value.document.return_value.set = AsyncMock()
    return mock_service


@pytest.fixture
def logging_service(mock_firestore_service):
    """Logging service with mocked dependencies."""
    return LoggingService(mock_firestore_service)


@pytest.mark.asyncio
async def test_log_access_success(logging_service, mock_firestore_service):
    """Test successful access logging."""
    result = await logging_service.log_access(
        user_id="user123",
        resource="moods",
        action="view",
        performed_by="admin456",
        performed_by_role="institution",
        metadata={"limit": "10"}
    )
    
    assert result is True
    
    # Verify Firestore was called
    mock_firestore_service.db.collection.assert_called_with("access_logs")


@pytest.mark.asyncio
async def test_log_access_minimal_params(logging_service, mock_firestore_service):
    """Test access logging with minimal parameters."""
    result = await logging_service.log_access(
        user_id="user123",
        resource="conversations",
        action="export",
        performed_by="admin456"
    )
    
    assert result is True
    mock_firestore_service.db.collection.assert_called_with("access_logs")


@pytest.mark.asyncio
async def test_get_access_logs_empty(logging_service, mock_firestore_service):
    """Test getting access logs when none exist."""
    # Mock empty result
    mock_query = MagicMock()
    mock_query.stream = AsyncMock()
    mock_query.stream.return_value.__aiter__ = AsyncMock(return_value=iter([]))
    
    mock_firestore_service.db.collection.return_value.where.return_value.\
        order_by.return_value.limit.return_value = mock_query
    
    result = await logging_service.get_access_logs("user123", 10)
    
    assert result == []


@pytest.mark.asyncio 
async def test_get_recent_access_logs(logging_service, mock_firestore_service):
    """Test getting recent access logs across all users."""
    # Mock empty result for simplicity
    mock_query = MagicMock()
    mock_query.stream = AsyncMock()
    mock_query.stream.return_value.__aiter__ = AsyncMock(return_value=iter([]))
    
    mock_firestore_service.db.collection.return_value.\
        order_by.return_value.limit.return_value = mock_query
    
    result = await logging_service.get_recent_access_logs(50)
    
    assert result == []
    mock_firestore_service.db.collection.assert_called_with("access_logs")
