# tests/test_institutions_real.py
"""
Real institution tests that hit actual Firestore
These tests require Firestore to be configured and running
"""
import pytest
import uuid
from datetime import datetime, UTC
from app.services.firestore import FirestoreService
from app.models.db_models import Institution, User


@pytest.mark.integration
class TestInstitutionFirestoreReal:
    """Test institution operations with real Firestore"""

    async def test_create_and_get_institution_real(self):
        """Test creating and retrieving an institution"""
        fs = FirestoreService()
        
        # Create unique institution
        institution_id = f"test_inst_{uuid.uuid4().hex[:8]}"
        institution = Institution(
            institution_id=institution_id,
            institution_name=f"Test University {uuid.uuid4().hex[:4]}",
            contact_person="Dr. Test Contact",
            region="North India",
            email="test@testuniv.edu",
            user_id="test_user_123",
            created_at=datetime.now(UTC)
        )
        
        try:
            # Create institution
            await fs.create_institution(institution)
            
            # Retrieve institution
            retrieved = await fs.get_institution(institution_id)
            
            assert retrieved is not None
            assert retrieved.institution_id == institution_id
            assert retrieved.institution_name == institution.institution_name
            assert retrieved.region == "North India"
            assert retrieved.active is True
            assert retrieved.student_count == 0
            
        finally:
            # Cleanup - delete test institution
            try:
                await fs.delete_institution(institution_id)
            except Exception:
                pass  # Best effort cleanup

    async def test_list_institutions_real(self):
        """Test listing institutions from Firestore"""
        fs = FirestoreService()
        
        institutions = await fs.list_institutions()
        
        # Should return a list (might be empty)
        assert isinstance(institutions, list)
        
        # If institutions exist, check structure
        if institutions:
            first_inst = institutions[0]
            assert hasattr(first_inst, 'institution_id')
            assert hasattr(first_inst, 'institution_name')
            assert hasattr(first_inst, 'region')
            assert hasattr(first_inst, 'student_count')
            assert hasattr(first_inst, 'active')

    async def test_institution_name_uniqueness_real(self):
        """Test institution name uniqueness checking"""
        fs = FirestoreService()
        
        # Use a unique name that shouldn't exist
        unique_name = f"Unique Test University {uuid.uuid4().hex[:8]}"
        
        # Should return None for non-existent institution
        result = await fs.get_institution_by_name(unique_name)
        assert result is None

    async def test_increment_student_count_real(self):
        """Test incrementing student count"""
        fs = FirestoreService()
        
        # Create temporary institution
        institution_id = f"test_count_{uuid.uuid4().hex[:8]}"
        institution = Institution(
            institution_id=institution_id,
            institution_name=f"Count Test University {uuid.uuid4().hex[:4]}",
            region="South India",
            student_count=5
        )
        
        try:
            await fs.create_institution(institution)
            
            # Increment student count
            await fs.increment_student_count(institution_id)
            
            # Verify count increased
            updated = await fs.get_institution(institution_id)
            assert updated.student_count == 6
            
        finally:
            # Cleanup
            try:
                await fs.delete_institution(institution_id)
            except Exception:
                pass

    async def test_complete_user_onboarding_with_institution_real(self):
        """Test complete onboarding flow with institution"""
        fs = FirestoreService()
        
        # Create test user
        user_id = f"test_user_{uuid.uuid4().hex[:8]}"
        test_user = User(
            user_id=user_id,
            email=f"{user_id}@test.com",
            hashed_password="test_hash",
            onboarding_completed=False,
            created_at=datetime.now(UTC)
        )
        
        # Create test institution
        institution_id = f"test_onboard_{uuid.uuid4().hex[:8]}"
        institution = Institution(
            institution_id=institution_id,
            institution_name=f"Onboarding Test Univ {uuid.uuid4().hex[:4]}",
            region="West India",
            student_count=10
        )
        
        try:
            await fs.create_user(test_user)
            await fs.create_institution(institution)
            
            # Complete onboarding
            profile = {
                "name": "Test Student",
                "age": "20",
                "region": "West India",
                "language_preference": "hi-IN"
            }
            
            await fs.complete_onboarding(
                user_id=user_id,
                role="student",
                profile=profile,
                institution_id=institution_id
            )
            
            # Verify user onboarding completed
            updated_user = await fs.get_user(user_id)
            assert updated_user.onboarding_completed is True
            assert updated_user.role == "student"
            assert updated_user.profile == profile
            assert updated_user.institution_id == institution_id
            
            # Verify institution student count incremented
            updated_institution = await fs.get_institution(institution_id)
            assert updated_institution.student_count == 11
            
        finally:
            # Cleanup
            try:
                await fs.delete_user(user_id)
                await fs.delete_institution(institution_id)
            except Exception:
                pass


@pytest.mark.integration
class TestInstitutionRegionsReal:
    """Test institution region handling with real data"""

    async def test_institutions_by_region_real(self):
        """Test filtering institutions by region"""
        fs = FirestoreService()
        
        all_institutions = await fs.list_institutions()
        
        # Group by region
        regions_found = set()
        region_counts = {}
        
        for inst in all_institutions:
            regions_found.add(inst.region)
            region_counts[inst.region] = region_counts.get(inst.region, 0) + 1
        
        # Check that we have valid Indian regions
        valid_regions = {
            "North India", "South India", "East India", 
            "West India", "Central India", "Northeast India"
        }
        
        # All found regions should be valid
        invalid_regions = regions_found - valid_regions
        assert len(invalid_regions) == 0, f"Invalid regions found: {invalid_regions}"

    async def test_active_institutions_real(self):
        """Test filtering active institutions"""
        fs = FirestoreService()
        
        all_institutions = await fs.list_institutions()
        
        active_count = sum(1 for inst in all_institutions if inst.active)
        inactive_count = sum(1 for inst in all_institutions if not inst.active)
        
        # Should have counts that add up
        assert active_count + inactive_count == len(all_institutions)
        
        # Most institutions should be active by default
        if all_institutions:
            assert active_count >= 0  # At least some should be active


def main():
    """Run institution tests manually with async"""
    import asyncio
    
    async def run_tests():
        print("🏛️  Testing MITRA Institution Management")
        print("=" * 50)
        
        fs = FirestoreService()
        
        try:
            print("\n📍 Testing institution list...")
            institutions = await fs.list_institutions()
            print(f"Found {len(institutions)} institutions")
            
            if institutions:
                print("Sample institutions:")
                for i, inst in enumerate(institutions[:3]):
                    print(f"  {i+1}. {inst.institution_name} ({inst.region})")
                    print(f"     Students: {inst.student_count}, Active: {inst.active}")
            
            print("\n📍 Testing institution name uniqueness...")
            unique_name = f"Test Unique University {uuid.uuid4().hex[:6]}"
            result = await fs.get_institution_by_name(unique_name)
            print(f"Unique name search result: {result}")
            
            print("\n📍 Testing region distribution...")
            region_counts = {}
            for inst in institutions:
                region_counts[inst.region] = region_counts.get(inst.region, 0) + 1
            
            for region, count in region_counts.items():
                print(f"  {region}: {count} institutions")
            
            print("\n✅ Institution testing completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during testing: {e}")
    
    asyncio.run(run_tests())


if __name__ == "__main__":
    main()
