# tests/test_onboarding.py
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.models.db_models import User, Institution
from app.models.schemas import OnboardingRequest, UserRole
from app.dependencies.auth import get_current_user_from_session

# Patch path for auth dependency
AUTH_PATCH = 'app.dependencies.auth.get_current_user_from_session'

client = TestClient(app)


class TestOnboardingMocks:
    """Test onboarding endpoints with mocked dependencies"""

    @patch('app.routes.users.fs')
    def test_complete_onboarding_student(self, mock_fs):
        """Test completing onboarding as a student"""
        # Mock user without onboarding
        test_user = User(
            user_id="test@example.com",
            email="test@example.com",
            
            onboarding_completed=False
        )
        mock_fs.get_user_by_email = AsyncMock(return_value=test_user)
        mock_fs.complete_onboarding = AsyncMock()
        mock_fs.get_institution = AsyncMock(return_value=Institution(
            institution_id="inst_123",
            institution_name="Test University",
            contact_person="Dr. Test",
            region="North India",
            email="admin@testuniv.edu",
            user_id="admin_123"
        ))
        mock_fs.increment_student_count = AsyncMock()

        # Override the auth dependency
        app.dependency_overrides[get_current_user_from_session] = lambda: test_user

        response = client.post("/api/v1/users/onboarding", json={
                "role": "student",
                "profile": {
                    "name": "Test Student",
                    "age": "20",
                    "region": "North India",
                    "language_preference": "hi-IN"
                },
                "institution_id": "inst_123"
            })

        # Clean up dependency override
        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "completed successfully" in data["message"]

    @patch('app.routes.users.fs')
    def test_complete_onboarding_institution(self, mock_fs):
        """Test completing onboarding as an institution"""
        # Mock user without onboarding
        test_user = User(
            user_id="admin@testuniv.edu",
            email="admin@testuniv.edu",
            
            onboarding_completed=False
        )
        mock_fs.get_user_by_email = AsyncMock(return_value=test_user)
        mock_fs.complete_onboarding = AsyncMock()
        mock_fs.get_institution_by_name = AsyncMock(return_value=None)
        mock_fs.create_institution = AsyncMock()

        # Override the auth dependency
        app.dependency_overrides[get_current_user_from_session] = lambda: test_user

        response = client.post("/api/v1/users/onboarding", json={
            "role": "institution",
            "profile": {
                "institution_name": "New Test University",
                "contact_person": "Dr. Admin",
                "region": "South India"
            }
        })

        # Clean up dependency override
        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @patch('app.routes.users.fs')
    def test_onboarding_already_completed(self, mock_fs):
        """Test onboarding when already completed"""
        # Mock user with completed onboarding
        test_user = User(
            user_id="test@example.com",
            email="test@example.com",
            
            onboarding_completed=True
        )
        mock_fs.get_user_by_email = AsyncMock(return_value=test_user)

        # Override the auth dependency
        app.dependency_overrides[get_current_user_from_session] = lambda: test_user

        response = client.post("/api/v1/users/onboarding", json={
            "role": "student",
            "profile": {"name": "Test"}
        })

        # Clean up dependency override
        app.dependency_overrides.clear()

        assert response.status_code == 400
        assert "already completed" in response.json()["detail"]

    @patch('app.routes.users.fs')
    def test_institution_name_already_exists(self, mock_fs):
        """Test institution registration with existing name"""
        test_user = User(
            user_id="admin@example.edu",
            email="admin@example.edu",
            
            onboarding_completed=False
        )
        existing_institution = Institution(
            institution_id="existing_123",
            institution_name="Existing University",
            contact_person="Dr. Existing",
            region="North India",
            email="admin@existing.edu",
            user_id="admin_existing"
        )
        
        mock_fs.get_user_by_email = AsyncMock(return_value=test_user)
        mock_fs.get_institution_by_name = AsyncMock(return_value=existing_institution)

        # Override the auth dependency
        app.dependency_overrides[get_current_user_from_session] = lambda: test_user

        response = client.post("/api/v1/users/onboarding", json={
            "role": "institution",
            "profile": {
                "institution_name": "Existing University",
                "contact_person": "New Admin",
                "region": "South India"
            }
        })

        # Clean up dependency override
        app.dependency_overrides.clear()

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    @patch('app.routes.users.fs')
    def test_get_user_profile(self, mock_fs):
        """Test getting user profile"""
        test_user = User(
            user_id="test@example.com",
            email="test@example.com",
            
            onboarding_completed=True,
            role="student",
            profile={"name": "Test User", "age": "20"}
        )
        mock_fs.get_user_by_email = AsyncMock(return_value=test_user)

        # Override the auth dependency
        app.dependency_overrides[get_current_user_from_session] = lambda: test_user

        response = client.get("/api/v1/users/profile")

        # Clean up dependency override
        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert data["onboarding_completed"] is True
        assert data["role"] == "student"
        assert data["email"] == "test@example.com"

    @patch('app.routes.users.fs')
    def test_get_institutions_list(self, mock_fs):
        """Test getting list of institutions"""
        institutions = [
            Institution(
                institution_id="inst_1",
                institution_name="University A",
                contact_person="Dr. A",
                region="North India",
                email="admin@univa.edu",
                user_id="admin_1",
                student_count=100,
                active=True
            ),
            Institution(
                institution_id="inst_2",
                institution_name="College B",
                contact_person="Dr. B",
                region="South India",
                email="admin@collegeb.edu",
                user_id="admin_2",
                student_count=50,
                active=True
            )
        ]
        mock_fs.list_institutions = AsyncMock(return_value=institutions)

        response = client.get("/api/v1/users/institutions")

        assert response.status_code == 200
        data = response.json()
        assert len(data["institutions"]) == 2
        assert data["institutions"][0]["institution_name"] == "University A"
        assert data["institutions"][1]["region"] == "South India"

    def test_onboarding_validation_errors(self):
        """Test onboarding request validation"""
        # Create a mock user for auth
        mock_user = User(
            user_id="test@example.com",
            email="test@example.com",
            onboarding_completed=False
        )
        
        # Override the auth dependency
        app.dependency_overrides[get_current_user_from_session] = lambda: mock_user

        # Missing profile data
        response = client.post("/api/v1/users/onboarding", json={
            "role": "student"
                # Missing profile
            })

        # Clean up dependency override
        app.dependency_overrides.clear()

        assert response.status_code == 422  # Validation error

    def test_onboarding_unauthenticated(self):
        """Test onboarding without authentication"""
        response = client.post("/api/v1/users/onboarding", json={
            "role": "student",
            "profile": {"name": "Test"}
        })

        assert response.status_code == 401


class TestOnboardingSchemas:
    """Test onboarding schema validation"""

    def test_user_role_enum(self):
        """Test UserRole enum validation"""
        # Valid roles
        student_role = UserRole.STUDENT
        institution_role = UserRole.INSTITUTION
        
        assert student_role.value == "student"
        assert institution_role.value == "institution"

    def test_onboarding_request_validation(self):
        """Test OnboardingRequest schema validation"""
        # Valid student request
        student_request = OnboardingRequest(
            role=UserRole.STUDENT,
            profile={
                "name": "Test Student",
                "age": "20",
                "region": "North India",
                "language_preference": "hi-IN"
            },
            institution_id="inst_123"
        )
        
        assert student_request.role == UserRole.STUDENT
        assert student_request.profile["name"] == "Test Student"
        assert student_request.institution_id == "inst_123"

        # Valid institution request
        institution_request = OnboardingRequest(
            role=UserRole.INSTITUTION,
            profile={
                "institution_name": "Test University",
                "contact_person": "Dr. Admin",
                "region": "South India"
            }
        )
        
        assert institution_request.role == UserRole.INSTITUTION
        assert institution_request.profile["institution_name"] == "Test University"
        assert institution_request.institution_id is None
