#!/usr/bin/env python3
"""
Test script for Student and Mood API endpoints
This script tests the core functionality of the StudentService and routes.
"""

import asyncio
import uuid
from app.services.student_service import StudentService
from app.services.firestore import FirestoreService
from app.models.db_models import User
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_test_student():
    """Create a test student in Firestore for testing purposes."""
    fs = FirestoreService()
    
    # Create a test student user
    test_user_id = str(uuid.uuid4())
    test_user = User(
        user_id=test_user_id,
        email="test.student@example.com",
        name="Test Student",
        onboarding_completed=True,
        role="student",
        profile={
            "name": "Test Student",
            "age": "20",
            "region": "North India",
            "language_preference": "hi-IN"
        },
        institution_id=None  # No institution for this test
    )
    
    await fs.create_user(test_user)
    logger.info(f"Created test student with ID: {test_user_id}")
    return test_user_id


async def test_student_service():
    """Test the StudentService methods."""
    logger.info("Starting StudentService tests...")
    
    # Initialize service
    student_service = StudentService()
    
    try:
        # Test 1: Create a test student
        test_student_id = await create_test_student()
        
        # Test 2: List students
        logger.info("Testing list_students()...")
        students = await student_service.list_students()
        logger.info(f"Found {len(students)} students")
        
        # Find our test student
        test_student = None
        for student in students:
            if student["user_id"] == test_student_id:
                test_student = student
                break
        
        if test_student:
            logger.info(f"Test student found: {test_student['name']}")
        else:
            logger.error("Test student not found in list!")
            return
        
        # Test 3: Add mood entries
        logger.info("Testing add_mood()...")
        moods_to_add = [
            {"mood": "happy", "notes": "Feeling great today!"},
            {"mood": "anxious", "notes": "Worried about exams"},
            {"mood": "calm", "notes": None},
            {"mood": "excited", "notes": "Looking forward to weekend"}
        ]
        
        for mood_data in moods_to_add:
            result = await student_service.add_mood(
                student_id=test_student_id,
                mood=mood_data["mood"],
                notes=mood_data["notes"]
            )
            logger.info(
                f"Added mood: {result['mood']} (ID: {result['mood_id']})"
            )
        
        # Test 4: Get mood entries
        logger.info("Testing get_moods()...")
        moods = await student_service.get_moods(
            student_id=test_student_id,
            limit=10
        )
        logger.info(f"Retrieved {len(moods)} mood entries")
        
        for mood in moods:
            notes = mood.get('notes', 'No notes')
            logger.info(f"  - {mood['mood']} at {mood['created_at']}: {notes}")
        
        # Test 5: Get student info
        logger.info("Testing get_student_info()...")
        info = await student_service.get_student_info(test_student_id)
        if info:
            logger.info(f"Student info: {info['name']} ({info['email']})")
        else:
            logger.error("Failed to get student info!")
        
        logger.info("All StudentService tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()


async def test_error_cases():
    """Test error handling in StudentService."""
    logger.info("Testing error cases...")
    
    student_service = StudentService()
    
    try:
        # Test with non-existent student
        logger.info("Testing with non-existent student...")
        try:
            await student_service.add_mood(
                student_id="non-existent-id",
                mood="happy",
                notes="This should fail"
            )
            logger.error("Should have failed with non-existent student!")
        except ValueError as e:
            logger.info(f"Correctly caught error: {e}")
        
        # Test with invalid mood data
        logger.info("Testing with empty mood...")
        test_student_id = await create_test_student()
        try:
            await student_service.add_mood(
                student_id=test_student_id,
                mood="",  # Empty mood
                notes="This should fail"
            )
            logger.error("Should have failed with empty mood!")
        except Exception as e:
            logger.info(f"Correctly caught error: {e}")
        
        logger.info("Error case testing completed!")
        
    except Exception as e:
        logger.error(f"Error case testing failed: {e}")


async def main():
    """Main test function."""
    logger.info("=== MITRA Student & Mood API Testing ===")
    
    # Test the service layer
    await test_student_service()
    
    # Test error cases
    await test_error_cases()
    
    logger.info("=== Testing Complete ===")


if __name__ == "__main__":
    # Run the tests
    asyncio.run(main())
