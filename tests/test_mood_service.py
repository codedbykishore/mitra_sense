# test_mood_service.py
import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from app.services.mood_service import MoodService
from app.models.db_models import User


@pytest.fixture
def mood_service():
    """Create a MoodService instance with mocked dependencies."""
    with patch('app.services.mood_service.FirestoreService') as mock_fs, \
         patch('app.services.mood_service.PrivacyService') as mock_ps, \
         patch('app.services.mood_service.LoggingService') as mock_ls:
        
        service = MoodService()
        service.fs = mock_fs.return_value
        service.privacy_service = mock_ps.return_value
        service.logging_service = mock_ls.return_value
        
        return service


@pytest.fixture
def mock_student():
    """Create a mock student user."""
    return User(
        user_id="student123",
        email="student@test.com",
        name="Test Student",
        role="student",
        privacy_flags={"share_moods": True, "share_conversations": True},
        created_at=datetime.now(timezone.utc),
        last_active=datetime.now(timezone.utc)
    )


@pytest.fixture
def mock_current_user():
    """Create a mock current user."""
    return User(
        user_id="student123",  # Same as student for self-access
        email="student@test.com",
        name="Test Student",
        role="student",
        created_at=datetime.now(timezone.utc),
        last_active=datetime.now(timezone.utc)
    )


@pytest.fixture
def mock_other_user():
    """Create a mock other user (not the student)."""
    return User(
        user_id="other456",
        email="other@test.com",
        name="Other User",
        role="institution",
        created_at=datetime.now(timezone.utc),
        last_active=datetime.now(timezone.utc)
    )


class TestMoodServiceUpdateMood:
    """Test mood update functionality."""
    
    @pytest.mark.asyncio
    async def test_update_mood_success(self, mood_service, mock_student, mock_current_user):
        """Test successful mood update."""
        # Mock Firestore operations
        mood_service.fs.get_user = AsyncMock(return_value=mock_student)
        mood_ref_mock = AsyncMock()
        mood_service.fs.db.collection.return_value.document.return_value.collection.return_value.document.return_value = mood_ref_mock
        mood_service.logging_service.create_access_log = AsyncMock()
        
        # Test mood update
        result = await mood_service.update_mood(
            student_id="student123",
            mood="happy",
            intensity=8,
            notes="Feeling great today!",
            current_user=mock_current_user
        )
        
        # Verify result
        assert result["mood"] == "happy"
        assert result["intensity"] == 8
        assert result["notes"] == "Feeling great today!"
        assert "mood_id" in result
        assert "timestamp" in result
        
        # Verify Firestore calls
        mood_service.fs.get_user.assert_called_with("student123")
        mood_ref_mock.set.assert_called_once()
        mood_service.logging_service.create_access_log.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_mood_student_not_found(self, mood_service, mock_current_user):
        """Test mood update when student doesn't exist."""
        mood_service.fs.get_user = AsyncMock(return_value=None)
        
        with pytest.raises(ValueError, match="Student with ID nonexistent not found"):
            await mood_service.update_mood(
                student_id="nonexistent",
                mood="happy",
                current_user=mock_current_user
            )
    
    @pytest.mark.asyncio
    async def test_update_mood_not_student_role(self, mood_service, mock_current_user):
        """Test mood update when user is not a student."""
        non_student = User(
            user_id="institution123",
            email="inst@test.com",
            role="institution",
            created_at=datetime.now(timezone.utc),
            last_active=datetime.now(timezone.utc)
        )
        mood_service.fs.get_user = AsyncMock(return_value=non_student)
        
        with pytest.raises(ValueError, match="User institution123 is not a student"):
            await mood_service.update_mood(
                student_id="institution123",
                mood="happy",
                current_user=mock_current_user
            )
    
    @pytest.mark.asyncio
    async def test_update_mood_permission_denied(self, mood_service, mock_student, mock_other_user):
        """Test mood update permission denial for other users."""
        mood_service.fs.get_user = AsyncMock(return_value=mock_student)
        
        with pytest.raises(PermissionError, match="Students can only update their own mood"):
            await mood_service.update_mood(
                student_id="student123",
                mood="happy",
                current_user=mock_other_user
            )
    
    @pytest.mark.asyncio
    async def test_update_mood_invalid_intensity(self, mood_service, mock_student, mock_current_user):
        """Test mood update with invalid intensity."""
        mood_service.fs.get_user = AsyncMock(return_value=mock_student)
        
        # Test too low
        with pytest.raises(ValueError, match="Mood intensity must be between 1 and 10"):
            await mood_service.update_mood(
                student_id="student123",
                mood="happy",
                intensity=0,
                current_user=mock_current_user
            )
        
        # Test too high
        with pytest.raises(ValueError, match="Mood intensity must be between 1 and 10"):
            await mood_service.update_mood(
                student_id="student123",
                mood="happy",
                intensity=11,
                current_user=mock_current_user
            )


class TestMoodServiceGetCurrentMood:
    """Test get current mood functionality."""
    
    @pytest.mark.asyncio
    async def test_get_current_mood_success(self, mood_service, mock_student, mock_current_user):
        """Test successful current mood retrieval."""
        # Mock Firestore operations
        mood_service.fs.get_user = AsyncMock(return_value=mock_student)
        
        # Mock mood data
        mock_mood_data = {
            "mood_id": "mood123",
            "mood": "happy",
            "intensity": 8,
            "notes": "Great day!",
            "timestamp": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc)
        }
        
        # Mock query stream
        mock_doc = MagicMock()
        mock_doc.to_dict.return_value = mock_mood_data
        
        async def mock_stream():
            yield mock_doc
        
        mood_service.fs.db.collection.return_value.document.return_value.collection.return_value.order_by.return_value.limit.return_value.stream = mock_stream
        mood_service.logging_service.create_access_log = AsyncMock()
        
        # Test current mood retrieval
        result = await mood_service.get_current_mood(
            student_id="student123",
            current_user=mock_current_user
        )
        
        # Verify result
        assert result["mood_id"] == "mood123"
        assert result["mood"] == "happy"
        assert result["intensity"] == 8
        assert result["notes"] == "Great day!"
        
        # Verify logging
        mood_service.logging_service.create_access_log.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_current_mood_no_data(self, mood_service, mock_student, mock_current_user):
        """Test current mood retrieval when no mood data exists."""
        mood_service.fs.get_user = AsyncMock(return_value=mock_student)
        
        # Mock empty query stream
        async def mock_empty_stream():
            return
            yield  # This line will never execute
        
        mood_service.fs.db.collection.return_value.document.return_value.collection.return_value.order_by.return_value.limit.return_value.stream = mock_empty_stream
        
        # Test current mood retrieval
        result = await mood_service.get_current_mood(
            student_id="student123",
            current_user=mock_current_user
        )
        
        # Verify result is None
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_current_mood_privacy_denied(self, mood_service, mock_other_user):
        """Test current mood retrieval when privacy is disabled."""
        # Student with mood sharing disabled
        student_private = User(
            user_id="student123",
            email="student@test.com",
            role="student",
            privacy_flags={"share_moods": False, "share_conversations": True},
            created_at=datetime.now(timezone.utc),
            last_active=datetime.now(timezone.utc)
        )
        mood_service.fs.get_user = AsyncMock(return_value=student_private)
        
        with pytest.raises(PermissionError, match="Student has disabled mood sharing"):
            await mood_service.get_current_mood(
                student_id="student123",
                current_user=mock_other_user
            )


class TestMoodServiceGetMoodHistory:
    """Test mood history functionality."""
    
    @pytest.mark.asyncio
    async def test_get_mood_history_success(self, mood_service, mock_student, mock_current_user):
        """Test successful mood history retrieval."""
        mood_service.fs.get_user = AsyncMock(return_value=mock_student)
        
        # Mock mood history data
        mock_mood_data = [
            {
                "mood_id": "mood1",
                "mood": "happy",
                "intensity": 8,
                "notes": "Great day!",
                "timestamp": datetime.now(timezone.utc),
                "created_at": datetime.now(timezone.utc)
            },
            {
                "mood_id": "mood2",
                "mood": "sad",
                "intensity": 4,
                "notes": None,
                "timestamp": datetime.now(timezone.utc),
                "created_at": datetime.now(timezone.utc)
            }
        ]
        
        # Mock query stream
        async def mock_stream():
            for mood_data in mock_mood_data:
                mock_doc = MagicMock()
                mock_doc.to_dict.return_value = mood_data
                yield mock_doc
        
        mood_service.fs.db.collection.return_value.document.return_value.collection.return_value.order_by.return_value.limit.return_value.stream = mock_stream
        mood_service.logging_service.create_access_log = AsyncMock()
        
        # Test mood history retrieval
        result = await mood_service.get_mood_history(
            student_id="student123",
            limit=10,
            current_user=mock_current_user
        )
        
        # Verify result
        assert len(result) == 2
        assert result[0]["mood_id"] == "mood1"
        assert result[1]["mood_id"] == "mood2"
        
        # Verify logging
        mood_service.logging_service.create_access_log.assert_called_once()


class TestMoodServiceGetMoodStream:
    """Test mood stream functionality."""
    
    @pytest.mark.asyncio
    async def test_get_mood_stream_success(self, mood_service, mock_current_user):
        """Test successful mood stream retrieval."""
        # Mock users with mood sharing enabled
        mock_users = [
            {
                "user_id": "student1",
                "role": "student",
                "privacy_flags": {"share_moods": True},
                "profile": {"name": "Student One"}
            },
            {
                "user_id": "student2",
                "role": "student",
                "privacy_flags": {"share_moods": True},
                "profile": {"name": "Student Two"}
            }
        ]
        
        # Mock user query stream
        async def mock_user_stream():
            for user_data in mock_users:
                mock_doc = MagicMock()
                mock_doc.to_dict.return_value = user_data
                mock_doc.id = user_data["user_id"]
                yield mock_doc
        
        mood_service.fs.db.collection.return_value.where.return_value.stream = mock_user_stream
        
        # Mock mood query streams
        mock_mood_data = {
            "student1": [{"mood_id": "m1", "mood": "happy", "timestamp": datetime.now(timezone.utc)}],
            "student2": [{"mood_id": "m2", "mood": "sad", "timestamp": datetime.now(timezone.utc)}]
        }
        
        async def mock_mood_stream(user_id):
            for mood_data in mock_mood_data.get(user_id, []):
                mock_doc = MagicMock()
                mock_doc.to_dict.return_value = mood_data
                yield mock_doc
        
        # Mock the nested collection calls
        def mock_collection_chain(*args):
            if len(args) == 1 and args[0] == "users":
                # Return users collection mock
                mock_coll = MagicMock()
                mock_coll.where.return_value.stream = mock_user_stream
                return mock_coll
            elif len(args) == 1 and args[0] == "moods":
                # Return moods collection mock  
                return MagicMock()
            return MagicMock()
        
        mood_service.fs.db.collection.side_effect = mock_collection_chain
        mood_service.logging_service.create_access_log = AsyncMock()
        
        # Test mood stream retrieval
        result = await mood_service.get_mood_stream_data(
            current_user=mock_current_user,
            limit=50
        )
        
        # Verify logging
        mood_service.logging_service.create_access_log.assert_called_once()


class TestMoodServiceGetMoodAnalytics:
    """Test mood analytics functionality."""
    
    @pytest.mark.asyncio
    async def test_get_mood_analytics_success(self, mood_service, mock_current_user):
        """Test successful mood analytics retrieval."""
        # Mock user and mood data setup similar to stream test
        mock_users = [
            {
                "user_id": "student1",
                "role": "student",
                "privacy_flags": {"share_moods": True},
                "profile": {"name": "Student One"}
            }
        ]
        
        async def mock_user_stream():
            for user_data in mock_users:
                mock_doc = MagicMock()
                mock_doc.to_dict.return_value = user_data
                mock_doc.id = user_data["user_id"]
                yield mock_doc
        
        mood_service.fs.db.collection.return_value.where.return_value.stream = mock_user_stream
        mood_service.logging_service.create_access_log = AsyncMock()
        
        # Test analytics retrieval
        result = await mood_service.get_mood_analytics(current_user=mock_current_user)
        
        # Verify result structure
        assert "total_students" in result
        assert "students_with_mood_sharing" in result
        assert "mood_distribution" in result
        assert "mood_percentages" in result
        
        # Verify logging
        mood_service.logging_service.create_access_log.assert_called_once()


class TestMoodServiceHelpers:
    """Test helper methods."""
    
    def test_format_timestamp(self, mood_service):
        """Test timestamp formatting helper."""
        # Test with datetime object
        dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        result = mood_service._format_timestamp(dt)
        assert result == "2023-01-01T12:00:00+00:00"
        
        # Test with string
        string_val = "2023-01-01"
        result = mood_service._format_timestamp(string_val)
        assert result == "2023-01-01"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
