# app/services/student_service.py
import uuid
from typing import List, Optional
from datetime import datetime, timezone
from app.models.db_models import User, Mood
from app.services.firestore import FirestoreService
import logging

logger = logging.getLogger(__name__)


class StudentService:
    """Service for managing students and their mood tracking."""
    
    def __init__(self):
        self.fs = FirestoreService()
    
    async def list_students(self) -> List[dict]:
        """
        Fetch all registered students from Firestore.
        
        Returns:
            List of student dictionaries with user info and profile data.
        """
        try:
            logger.info("Fetching all students from Firestore")
            
            # Query users collection where role is "student"
            coll_ref = self.fs.db.collection("users")
            query = coll_ref.where("role", "==", "student")
            
            students = []
            async for doc in query.stream():
                try:
                    user_data = doc.to_dict()
                    user = User(**user_data)
                    
                    # Extract profile information
                    profile = user.profile or {}
                    
                    # Get institution name if institution_id exists
                    institution_name = None
                    if user.institution_id:
                        institution = await self.fs.get_institution(
                            user.institution_id
                        )
                        if institution:
                            institution_name = institution.institution_name
                    
                    student_info = {
                        "user_id": user.user_id,
                        "name": profile.get("name", "Unknown"),
                        "email": user.email,
                        "institution_name": institution_name,
                        "region": profile.get("region"),
                        "age": profile.get("age"),
                        "language_preference": profile.get(
                            "language_preference"
                        ),
                        "created_at": user.created_at.isoformat()
                    }
                    students.append(student_info)
                    
                except Exception as e:
                    logger.error(f"Error parsing student {doc.id}: {e}")
                    continue
            
            # Sort by name
            students.sort(key=lambda x: x.get("name", "").lower())
            
            logger.info(f"Retrieved {len(students)} students")
            return students
            
        except Exception as e:
            logger.error(f"Error listing students: {e}")
            raise Exception(f"Failed to list students: {str(e)}")
    
    async def add_mood(
        self, student_id: str, mood: str, notes: Optional[str] = None
    ) -> dict:
        """
        Add a new mood entry for a student.
        
        Args:
            student_id: The user_id of the student
            mood: The mood value (e.g., 'happy', 'sad', 'anxious')
            notes: Optional notes about the mood
            
        Returns:
            Dictionary with mood entry data
        """
        try:
            logger.info(f"Adding mood entry for student {student_id}")
            
            # Verify student exists and has student role
            user = await self.fs.get_user(student_id)
            if not user:
                raise ValueError(f"Student with ID {student_id} not found")
            
            if user.role != "student":
                raise ValueError(f"User {student_id} is not a student")
            
            # Create mood entry
            mood_id = str(uuid.uuid4())
            mood_entry = Mood(
                mood_id=mood_id,
                student_id=student_id,
                mood=mood.strip().lower(),
                notes=notes.strip() if notes else None,
                created_at=datetime.now(timezone.utc)
            )
            
            # Store in Firestore under students/{student_id}/moods
            mood_ref = (
                self.fs.db.collection("students")
                .document(student_id)
                .collection("moods")
                .document(mood_id)
            )
            await mood_ref.set(mood_entry.model_dump())
            
            logger.info(
                f"Successfully added mood entry {mood_id} for {student_id}"
            )
            
            return {
                "mood_id": mood_id,
                "mood": mood_entry.mood,
                "notes": mood_entry.notes,
                "created_at": mood_entry.created_at.isoformat()
            }
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error adding mood for student {student_id}: {e}")
            raise Exception(f"Failed to add mood entry: {str(e)}")
    
    async def get_moods(
        self, student_id: str, limit: int = 10
    ) -> List[dict]:
        """
        Fetch recent mood entries for a student.
        
        Args:
            student_id: The user_id of the student
            limit: Maximum number of mood entries to return (default: 10)
            
        Returns:
            List of mood entry dictionaries, ordered by created_at descending
        """
        try:
            logger.info(
                f"Fetching moods for student {student_id} (limit: {limit})"
            )
            
            # Verify student exists
            user = await self.fs.get_user(student_id)
            if not user:
                raise ValueError(f"Student with ID {student_id} not found")
            
            if user.role != "student":
                raise ValueError(f"User {student_id} is not a student")
            
            # Query moods subcollection
            moods_ref = (
                self.fs.db.collection("students")
                .document(student_id)
                .collection("moods")
            )
            
            # Order by created_at descending (newest first) and limit results
            query = moods_ref.order_by(
                "created_at", direction="DESCENDING"
            ).limit(limit)
            
            moods = []
            async for doc in query.stream():
                try:
                    mood_data = doc.to_dict()
                    mood_entry = {
                        "mood_id": mood_data["mood_id"],
                        "mood": mood_data["mood"],
                        "notes": mood_data.get("notes"),
                        "created_at": mood_data["created_at"].isoformat()
                        if hasattr(mood_data["created_at"], "isoformat")
                        else str(mood_data["created_at"])
                    }
                    moods.append(mood_entry)
                except Exception as e:
                    logger.error(f"Error parsing mood {doc.id}: {e}")
                    continue
            
            logger.info(
                f"Retrieved {len(moods)} mood entries for {student_id}"
            )
            return moods
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error getting moods for student {student_id}: {e}")
            raise Exception(f"Failed to get mood entries: {str(e)}")
    
    async def get_student_info(self, student_id: str) -> Optional[dict]:
        """
        Get detailed information about a specific student.
        
        Args:
            student_id: The user_id of the student
            
        Returns:
            Student information dictionary or None if not found
        """
        try:
            user = await self.fs.get_user(student_id)
            if not user or user.role != "student":
                return None
            
            # Get institution name if institution_id exists
            institution_name = None
            if user.institution_id:
                institution = await self.fs.get_institution(
                    user.institution_id
                )
                if institution:
                    institution_name = institution.institution_name
            
            profile = user.profile or {}
            
            return {
                "user_id": user.user_id,
                "name": profile.get("name", "Unknown"),
                "email": user.email,
                "institution_name": institution_name,
                "region": profile.get("region"),
                "age": profile.get("age"),
                "language_preference": profile.get("language_preference"),
                "created_at": user.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting student info for {student_id}: {e}")
            return None
