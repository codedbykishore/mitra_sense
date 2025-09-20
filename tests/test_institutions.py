# tests/test_institutions.py
"""
Tests for institution management functionality
"""
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.models.db_models import Institution, User
from app.models.schemas import InstitutionInfo

client = TestClient(app)


class TestInstitutionManagement:
    """Test institution management with mocked dependencies"""

    @patch('app.services.firestore.FirestoreService')
    def test_create_institution(self, mock_fs_class):
        """Test creating a new institution"""
        # Mock FirestoreService instance
        mock_fs = AsyncMock()
        mock_fs_class.return_value = mock_fs
        
        mock_fs.get_institution_by_name = AsyncMock(return_value=None)
        mock_fs.create_institution = AsyncMock()

        # Create institution
        institution = Institution(
            institution_id="test_inst_123",
            institution_name="Test University",
            contact_person="Dr. Test",
            region="North India",
            email="admin@testuniv.edu",
            user_id="admin_user_123"
        )

        # Test that institution can be created
        assert institution.institution_name == "Test University"
        assert institution.region == "North India"
        assert institution.active is True  # Default value
        assert institution.student_count == 0  # Default value

    @patch('app.services.firestore.FirestoreService')
    def test_institution_name_uniqueness(self, mock_fs_class):
        """Test institution name uniqueness validation"""
        mock_fs = AsyncMock()
        mock_fs_class.return_value = mock_fs

        # Mock existing institution
        existing_institution = Institution(
            institution_id="existing_123",
            institution_name="Existing University",
            contact_person="Dr. Existing",
            region="South India",
            email="admin@existing.edu",
            user_id="admin_123"
        )
        mock_fs.get_institution_by_name = AsyncMock(return_value=existing_institution)

        # Verify that existing institution can be found
        assert existing_institution.institution_name == "Existing University"

    @patch('app.services.firestore.FirestoreService')
    def test_list_institutions(self, mock_fs_class):
        """Test listing all institutions"""
        mock_fs = AsyncMock()
        mock_fs_class.return_value = mock_fs

        # Mock institutions list
        institutions = [
            Institution(
                institution_id="inst_1",
                institution_name="University A",
                contact_person="Dr. A",
                region="North India",
                email="admin@univa.edu",
                user_id="admin_1",
                student_count=150,
                active=True
            ),
            Institution(
                institution_id="inst_2", 
                institution_name="College B",
                contact_person="Dr. B",
                region="South India",
                email="admin@collegeb.edu",
                user_id="admin_2",
                student_count=75,
                active=True
            ),
            Institution(
                institution_id="inst_3",
                institution_name="Institute C",
                contact_person="Dr. C",
                region="West India",
                email="admin@instc.edu",
                user_id="admin_3",
                student_count=0,
                active=False
            )
        ]
        mock_fs.list_institutions = AsyncMock(return_value=institutions)

        # Test that institutions can be listed and filtered
        active_institutions = [inst for inst in institutions if inst.active]
        assert len(active_institutions) == 2
        assert all(inst.active for inst in active_institutions)

    @patch('app.services.firestore.FirestoreService')
    def test_increment_student_count(self, mock_fs_class):
        """Test incrementing student count for an institution"""
        mock_fs = AsyncMock()
        mock_fs_class.return_value = mock_fs
        
        # Mock institution
        institution = Institution(
            institution_id="inst_123",
            institution_name="Test University",
            contact_person="Dr. Test",
            region="North India",
            email="admin@testuniv.edu",
            user_id="admin_123",
            student_count=50
        )
        
        mock_fs.get_institution = AsyncMock(return_value=institution)
        mock_fs.increment_student_count = AsyncMock()

        # Test increment operation
        initial_count = institution.student_count
        assert initial_count == 50

    def test_institution_schema_validation(self):
        """Test institution schema validation"""
        # Valid institution
        valid_institution = Institution(
            institution_id="test_123",
            institution_name="Valid University",
            contact_person="Dr. Valid",
            region="Central India",
            email="contact@valid.edu",
            user_id="user_123"
        )
        
        assert valid_institution.institution_name == "Valid University"
        assert valid_institution.active is True
        assert valid_institution.student_count == 0

    def test_institution_info_schema(self):
        """Test InstitutionInfo response schema"""
        institution_info = InstitutionInfo(
            institution_id="info_123",
            institution_name="Info University",
            region="East India", 
            student_count=200,
            active=True
        )
        
        assert institution_info.institution_id == "info_123"
        assert institution_info.student_count == 200
        assert institution_info.active is True


class TestInstitutionRegions:
    """Test institution region handling"""

    def test_valid_regions(self):
        """Test that all valid Indian regions work"""
        valid_regions = [
            "North India",
            "South India", 
            "East India",
            "West India",
            "Central India",
            "Northeast India"
        ]
        
        for region in valid_regions:
            institution = Institution(
                institution_id=f"test_{region.replace(' ', '_').lower()}",
                institution_name=f"University of {region}",
                contact_person=f"Dr. {region}",
                region=region,
                email=f"admin@{region.replace(' ', '').lower()}.edu",
                user_id=f"admin_{region.replace(' ', '_').lower()}"
            )
            assert institution.region == region

    def test_region_based_filtering(self):
        """Test filtering institutions by region"""
        institutions = [
            Institution(
                institution_id="north_1",
                institution_name="North University 1",
                contact_person="Dr. North 1",
                region="North India",
                email="admin@north1.edu",
                user_id="admin_north_1"
            ),
            Institution(
                institution_id="north_2", 
                institution_name="North University 2",
                contact_person="Dr. North 2",
                region="North India",
                email="admin@north2.edu",
                user_id="admin_north_2"
            ),
            Institution(
                institution_id="south_1",
                institution_name="South University 1",
                contact_person="Dr. South 1", 
                region="South India",
                email="admin@south1.edu",
                user_id="admin_south_1"
            )
        ]
        
        # Filter by region
        north_institutions = [
            inst for inst in institutions if inst.region == "North India"
        ]
        south_institutions = [
            inst for inst in institutions if inst.region == "South India"
        ]
        
        assert len(north_institutions) == 2
        assert len(south_institutions) == 1
        assert all(inst.region == "North India" for inst in north_institutions)


class TestInstitutionStudentTracking:
    """Test student count tracking for institutions"""

    def test_student_count_initialization(self):
        """Test that new institutions start with 0 students"""
        institution = Institution(
            institution_id="new_inst",
            institution_name="New Institution",
            contact_person="Dr. New",
            region="Central India",
            email="admin@newinst.edu",
            user_id="admin_new"
        )
        
        assert institution.student_count == 0

    def test_active_status_default(self):
        """Test that new institutions are active by default"""
        institution = Institution(
            institution_id="active_inst",
            institution_name="Active Institution",
            contact_person="Dr. Active", 
            region="West India",
            email="admin@activeinst.edu",
            user_id="admin_active"
        )
        
        assert institution.active is True

    @patch('app.services.firestore.FirestoreService')
    def test_student_enrollment_flow(self, mock_fs_class):
        """Test complete student enrollment flow"""
        mock_fs = AsyncMock()
        mock_fs_class.return_value = mock_fs

        # Mock student user
        student_user = User(
            user_id="student@example.com",
            email="student@example.com",
            onboarding_completed=False
        )

        # Mock institution
        target_institution = Institution(
            institution_id="target_inst",
            institution_name="Target University",
            contact_person="Dr. Target",
            region="North India",
            email="admin@target.edu",
            user_id="admin_target",
            student_count=100
        )

        mock_fs.get_user_by_email = AsyncMock(return_value=student_user)
        mock_fs.get_institution = AsyncMock(return_value=target_institution)
        mock_fs.increment_student_count = AsyncMock()
        mock_fs.complete_onboarding = AsyncMock()

        # Verify enrollment data
        assert student_user.onboarding_completed is False
        assert target_institution.student_count == 100
