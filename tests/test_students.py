# tests/test_students.py
import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.main import app
from app.services.student_service import StudentService
from app.models.db_models import User
from app.dependencies.auth import get_current_user_from_session
from fastapi.testclient import TestClient


@pytest.fixture
def mock_student_service():
    """Mock StudentService for testing."""
    return Mock(spec=StudentService)


@pytest.fixture
def mock_current_user():
    """Mock current user for authentication."""
    return User(
        user_id="test-user-123",
        email="test@example.com",
        name="Test User",
        role="institution",
        onboarding_completed=True
    )


@pytest.fixture
def test_client():
    """Test client for FastAPI."""
    return TestClient(app)


@pytest.fixture
def sample_students_data():
    """Sample student data for testing."""
    return [
        {
            "user_id": "student-1",
            "name": "John Doe",
            "email": "john@example.com",
            "institution_name": "Test University",
            "region": "North India",
            "age": "20",
            "language_preference": "en-US",
            "created_at": "2025-09-20T12:00:00Z"
        },
        {
            "user_id": "student-2",
            "name": "Jane Smith",
            "email": "jane@example.com",
            "institution_name": None,
            "region": "South India",
            "age": "21",
            "language_preference": "hi-IN",
            "created_at": "2025-09-20T11:00:00Z"
        }
    ]


@pytest.fixture
def sample_moods_data():
    """Sample mood data for testing."""
    return [
        {
            "mood_id": "mood-1",
            "mood": "happy",
            "notes": "Feeling great today!",
            "timestamp": "2025-09-20T15:00:00Z",
            "created_at": "2025-09-20T15:00:00Z"
        },
        {
            "mood_id": "mood-2",
            "mood": "anxious",
            "notes": "Worried about exams",
            "timestamp": "2025-09-20T14:00:00Z",
            "created_at": "2025-09-20T14:00:00Z"
        }
    ]


class TestListStudents:
    """Test cases for GET /api/v1/students endpoint."""
    
    @patch('app.routes.students.student_service')
    def test_list_students_success(
        self, mock_service, test_client,
        mock_current_user, sample_students_data
    ):
        """Test successful student listing."""
        # Setup dependency override
        app.dependency_overrides[get_current_user_from_session] = lambda: mock_current_user
        
        # Setup service mock
        mock_service.list_students = AsyncMock(
            return_value=sample_students_data
        )
        
        # Make request
        response = test_client.get("/api/v1/students")
        
        # Clean up dependency override
        app.dependency_overrides.clear()
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "students" in data
        assert "total_count" in data
        assert data["total_count"] == 2
        assert len(data["students"]) == 2
        assert data["students"][0]["name"] == "John Doe"
    
    @patch('app.routes.students.student_service')
    def test_list_students_empty(
        self, mock_service, test_client, mock_current_user
    ):
        """Test student listing when no students exist."""
        # Setup dependency override
        app.dependency_overrides[get_current_user_from_session] = lambda: mock_current_user
        
        # Setup service mock
        mock_service.list_students = AsyncMock(return_value=[])
        
        # Make request
        response = test_client.get("/api/v1/students")
        
        # Clean up dependency override
        app.dependency_overrides.clear()
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 0
        assert len(data["students"]) == 0
    
    @patch('app.routes.students.student_service')
    def test_list_students_service_error(
        self, mock_service, test_client, mock_current_user
    ):
        """Test student listing when service raises exception."""
        # Setup dependency override
        app.dependency_overrides[get_current_user_from_session] = lambda: mock_current_user
        
        # Setup service mock
        mock_service.list_students = AsyncMock(
            side_effect=Exception("Database error")
        )
        
        # Make request
        response = test_client.get("/api/v1/students")
        
        # Clean up dependency override
        app.dependency_overrides.clear()
        
        # Assertions
        assert response.status_code == 500
        assert "Failed to retrieve students" in response.json()["detail"]


class TestAddStudentMood:
    """Test cases for POST /api/v1/students/{student_id}/moods endpoint."""
    
    @patch('app.routes.students.student_service')
    def test_add_mood_success(
        self, mock_service, test_client, mock_current_user
    ):
        """Test successful mood addition."""
        # Setup dependency override
        app.dependency_overrides[get_current_user_from_session] = lambda: mock_current_user
        
        # Setup service mock
        mock_service.add_mood = AsyncMock(return_value={
            "mood_id": "mood-123",
            "mood": "happy",
            "notes": "Test note",
            "timestamp": "2025-09-20T15:00:00Z",
            "created_at": "2025-09-20T15:00:00Z"
        })
        
        # Make request
        response = test_client.post(
            "/api/v1/students/student-123/moods",
            json={"mood": "happy", "notes": "Test note"}
        )
        
        # Clean up dependency override
        app.dependency_overrides.clear()
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Mood entry added successfully"
        assert data["mood_entry"]["mood"] == "happy"
        assert data["mood_entry"]["notes"] == "Test note"
    
    @patch('app.routes.students.student_service')
    def test_add_mood_without_notes(
        self, mock_service, test_client, mock_current_user
    ):
        """Test mood addition without notes."""
        # Setup dependency override
        app.dependency_overrides[get_current_user_from_session] = lambda: mock_current_user
        
        # Setup service mock
        mock_service.add_mood = AsyncMock(return_value={
            "mood_id": "mood-456",
            "mood": "calm",
            "notes": None,
            "timestamp": "2025-09-20T15:00:00Z",
            "created_at": "2025-09-20T15:00:00Z"
        })
        
        # Make request
        response = test_client.post(
            "/api/v1/students/student-123/moods",
            json={"mood": "calm"}
        )
        
        # Clean up dependency override
        app.dependency_overrides.clear()
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["mood_entry"]["mood"] == "calm"
        assert data["mood_entry"]["notes"] is None
    
    @patch('app.routes.students.student_service')
    def test_add_mood_invalid_student(
        self, mock_service, test_client, mock_current_user
    ):
        """Test mood addition with invalid student ID."""
        # Setup dependency override
        app.dependency_overrides[get_current_user_from_session] = lambda: mock_current_user
        
        # Setup service mock
        mock_service.add_mood = AsyncMock(
            side_effect=ValueError("Student with ID invalid-id not found")
        )
        
        # Make request
        response = test_client.post(
            "/api/v1/students/invalid-id/moods",
            json={"mood": "happy"}
        )
        
        # Clean up dependency override
        app.dependency_overrides.clear()
        
        # Assertions
        assert response.status_code == 400
        detail = response.json()["detail"]
        assert "Student with ID invalid-id not found" in detail
    
    def test_add_mood_missing_mood(self, test_client, mock_current_user):
        """Test mood addition with missing mood field."""
        # Setup dependency override for auth
        app.dependency_overrides[get_current_user_from_session] = lambda: mock_current_user
        
        response = test_client.post(
            "/api/v1/students/student-123/moods",
            json={"notes": "Only notes"}
        )
        
        # Clean up dependency override
        app.dependency_overrides.clear()
        
        # Should fail validation
        assert response.status_code == 422


class TestGetStudentMoods:
    """Test cases for GET /api/v1/students/{student_id}/moods endpoint."""
    
    @patch('app.routes.students.student_service')
    @patch('app.routes.students.privacy_middleware')
    def test_get_moods_success(
        self, mock_privacy_middleware, mock_service, test_client,
        mock_current_user, sample_moods_data
    ):
        """Test successful mood retrieval."""
        # Setup dependency override
        app.dependency_overrides[get_current_user_from_session] = lambda: mock_current_user
        
        # Setup privacy middleware mock
        mock_privacy_middleware.check_and_log_access = AsyncMock()
        
        # Setup service mock
        mock_service.get_moods = AsyncMock(return_value=sample_moods_data)
        
        # Make request
        response = test_client.get("/api/v1/students/student-123/moods")
        
        # Clean up dependency override
        app.dependency_overrides.clear()
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["student_id"] == "student-123"
        assert len(data["moods"]) == 2
        assert data["total_count"] == 2
        assert data["moods"][0]["mood"] == "happy"
    
    @patch('app.routes.students.student_service')
    @patch('app.routes.students.privacy_middleware')
    def test_get_moods_with_limit(
        self, mock_privacy_middleware, mock_service, test_client, mock_current_user
    ):
        """Test mood retrieval with limit parameter."""
        # Setup dependency override
        app.dependency_overrides[get_current_user_from_session] = lambda: mock_current_user
        
        # Setup privacy middleware mock
        mock_privacy_middleware.check_and_log_access = AsyncMock()
        
        # Setup service mock
        mock_service.get_moods = AsyncMock(return_value=[])
        
        # Make request with limit
        response = test_client.get(
            "/api/v1/students/student-123/moods?limit=5"
        )
        
        # Clean up dependency override
        app.dependency_overrides.clear()
        
        # Assertions
        assert response.status_code == 200
        mock_service.get_moods.assert_called_once_with(
            student_id="student-123", limit=5
        )
    
    @patch('app.routes.students.student_service')
    @patch('app.routes.students.privacy_middleware')
    def test_get_moods_invalid_student(
        self, mock_privacy_middleware, mock_service, test_client, mock_current_user
    ):
        """Test mood retrieval with invalid student ID."""
        # Setup dependency override
        app.dependency_overrides[get_current_user_from_session] = lambda: mock_current_user
        
        # Setup privacy middleware mock
        mock_privacy_middleware.check_and_log_access = AsyncMock()
        
        # Setup service mock
        mock_service.get_moods = AsyncMock(
            side_effect=ValueError("Student with ID invalid-id not found")
        )
        
        # Make request
        response = test_client.get("/api/v1/students/invalid-id/moods")
        
        # Clean up dependency override
        app.dependency_overrides.clear()
        
        # Assertions
        assert response.status_code == 400
        detail = response.json()["detail"]
        assert "Student with ID invalid-id not found" in detail


class TestGetStudentInfo:
    """Test cases for GET /api/v1/students/{student_id} endpoint."""
    
    @patch('app.routes.students.student_service')
    def test_get_student_info_success(
        self, mock_service, test_client,
        mock_current_user, sample_students_data
    ):
        """Test successful student info retrieval."""
        # Setup dependency override
        app.dependency_overrides[get_current_user_from_session] = lambda: mock_current_user
        
        # Setup service mock
        mock_service.get_student_info = AsyncMock(
            return_value=sample_students_data[0]
        )
        
        # Make request
        response = test_client.get("/api/v1/students/student-1")
        
        # Clean up dependency override
        app.dependency_overrides.clear()
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "student-1"
        assert data["name"] == "John Doe"
        assert data["email"] == "john@example.com"
    
    @patch('app.routes.students.student_service')
    def test_get_student_info_not_found(
        self, mock_service, test_client, mock_current_user
    ):
        """Test student info retrieval when student not found."""
        # Setup dependency override
        app.dependency_overrides[get_current_user_from_session] = lambda: mock_current_user
        
        # Setup service mock
        mock_service.get_student_info = AsyncMock(return_value=None)
        
        # Make request
        response = test_client.get("/api/v1/students/nonexistent")
        
        # Clean up dependency override
        app.dependency_overrides.clear()
        
        # Assertions
        assert response.status_code == 404
        assert "Student not found" in response.json()["detail"]
