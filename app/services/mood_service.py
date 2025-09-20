# app/services/mood_service.py
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from app.models.db_models import User
from app.services.firestore import FirestoreService
from app.services.privacy_service import PrivacyService
from app.services.logging_service import LoggingService
import logging

logger = logging.getLogger(__name__)


class MoodService:
    """Enhanced service for managing student moods with real-time updates."""
    
    def __init__(self):
        self.fs = FirestoreService()
        self.privacy_service = PrivacyService(self.fs)
        self.logging_service = LoggingService(self.fs)
    
    def _format_timestamp(self, ts_val) -> str:
        """Helper to format timestamp values consistently."""
        return (ts_val.isoformat() if hasattr(ts_val, "isoformat")
                else str(ts_val))
    
    async def update_mood(
        self,
        student_id: str,
        mood: str,
        intensity: Optional[int] = None,
        notes: Optional[str] = None,
        current_user: User = None
    ) -> Dict[str, Any]:
        """
        Update a student's mood with privacy enforcement and access logging.
        
        Args:
            student_id: The user_id of the student
            mood: The mood value (e.g., 'happy', 'sad', 'anxious')
            intensity: Mood intensity from 1-10 (optional)
            notes: Optional notes about the mood
            current_user: User making the request (for privacy check)
            
        Returns:
            Dictionary with mood entry data
            
        Raises:
            ValueError: If validation fails
            PermissionError: If privacy check fails
        """
        try:
            logger.info(f"Updating mood for student {student_id}")
            
            # Verify student exists and has student role
            user = await self.fs.get_user(student_id)
            if not user:
                raise ValueError(f"Student with ID {student_id} not found")
            
            if user.role != "student":
                raise ValueError(f"User {student_id} is not a student")
            
            # Privacy check: Only the student can update their own mood
            if current_user and current_user.user_id != student_id:
                raise PermissionError(
                    "Students can only update their own mood"
                )
            
            # Check privacy flags before saving
            privacy_flags = user.privacy_flags or {}
            if not privacy_flags.get("share_moods", True):
                logger.info(f"Student {student_id} has disabled mood sharing")
            
            # Validate intensity if provided
            if intensity is not None and not (1 <= intensity <= 10):
                raise ValueError("Mood intensity must be between 1 and 10")
            
            # Create mood entry with timestamp
            mood_id = str(uuid.uuid4())
            timestamp = datetime.now(timezone.utc)
            
            mood_data = {
                "mood_id": mood_id,
                "student_id": student_id,
                "mood": mood.strip().lower(),
                "intensity": intensity,
                "notes": notes.strip() if notes else None,
                "timestamp": timestamp,
                "created_at": timestamp  # Keep both for compatibility
            }
            
            # Store in Firestore under moods/{student_id}/entries
            mood_ref = (
                self.fs.db.collection("moods")
                .document(student_id)
                .collection("entries")
                .document(mood_id)
            )
            await mood_ref.set(mood_data)
            
            # Log the mood update
            if current_user:
                await self.logging_service.create_access_log(
                    user_id=student_id,
                    resource="moods",
                    action="update",
                    performed_by=current_user.user_id,
                    performed_by_role=current_user.role or "unknown",
                    metadata={
                        "mood": mood,
                        "intensity": str(intensity) if intensity else None,
                        "has_notes": str(bool(notes))
                    }
                )
            
            logger.info(
                f"Successfully updated mood {mood_id} for {student_id}"
            )
            
            return {
                "mood_id": mood_id,
                "mood": mood_data["mood"],
                "intensity": mood_data["intensity"],
                "notes": mood_data["notes"],
                "timestamp": timestamp.isoformat(),
                "created_at": timestamp.isoformat()
            }
            
        except (ValueError, PermissionError):
            raise
        except Exception as e:
            logger.error(f"Error updating mood for student {student_id}: {e}")
            raise Exception(f"Failed to update mood: {str(e)}")
    
    async def get_current_mood(
        self,
        student_id: str,
        current_user: User = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get the most recent mood entry for a student with privacy enforcement.
        
        Args:
            student_id: The user_id of the student
            current_user: User making the request (for privacy check)
            
        Returns:
            Most recent mood entry dictionary or None if not found
            
        Raises:
            PermissionError: If privacy check fails
        """
        try:
            logger.info(f"Getting current mood for student {student_id}")
            
            # Verify student exists
            user = await self.fs.get_user(student_id)
            if not user:
                raise ValueError(f"Student with ID {student_id} not found")
            
            if user.role != "student":
                raise ValueError(f"User {student_id} is not a student")
            
            # Check privacy flags
            privacy_flags = user.privacy_flags or {}
            share_moods = privacy_flags.get("share_moods", True)
            
            # Privacy enforcement: deny access if sharing disabled
            is_own_data = current_user and current_user.user_id == student_id
            if not share_moods and not is_own_data:
                raise PermissionError("Student has disabled mood sharing")
            
            # Query for the most recent mood entry
            moods_ref = (
                self.fs.db.collection("moods")
                .document(student_id)
                .collection("entries")
            )
            
            # Order by timestamp descending and limit to 1
            query = moods_ref.order_by(
                "timestamp", direction="DESCENDING"
            ).limit(1)
            
            mood_data = None
            async for doc in query.stream():
                mood_data = doc.to_dict()
                break
            
            if mood_data:
                # Log the access
                if current_user:
                    await self.logging_service.create_access_log(
                        user_id=student_id,
                        resource="moods",
                        action="view",
                        performed_by=current_user.user_id,
                        performed_by_role=current_user.role or "unknown",
                        metadata={"action_type": "get_current_mood"}
                    )
                
                # Format response
                def format_timestamp(ts_val):
                    return (ts_val.isoformat() if hasattr(ts_val, "isoformat")
                            else str(ts_val))
                
                timestamp_str = format_timestamp(mood_data["timestamp"])
                created_at_str = format_timestamp(
                    mood_data.get("created_at", mood_data["timestamp"])
                )
                
                return {
                    "mood_id": mood_data["mood_id"],
                    "mood": mood_data["mood"],
                    "intensity": mood_data.get("intensity"),
                    "notes": mood_data.get("notes"),
                    "timestamp": timestamp_str,
                    "created_at": created_at_str
                }
            
            return None
            
        except (ValueError, PermissionError):
            raise
        except Exception as e:
            logger.error(f"Error getting current mood for student {student_id}: {e}")
            raise Exception(f"Failed to get current mood: {str(e)}")
    
    async def get_mood_history(
        self, 
        student_id: str,
        limit: int = 10,
        current_user: User = None
    ) -> List[Dict[str, Any]]:
        """
        Get mood history for a student with privacy enforcement.
        
        Args:
            student_id: The user_id of the student
            limit: Maximum number of mood entries to return
            current_user: User making the request (for privacy check)
            
        Returns:
            List of mood entry dictionaries, ordered by timestamp descending
            
        Raises:
            PermissionError: If privacy check fails
        """
        try:
            logger.info(f"Getting mood history for student {student_id} (limit: {limit})")
            
            # Verify student exists
            user = await self.fs.get_user(student_id)
            if not user:
                raise ValueError(f"Student with ID {student_id} not found")
            
            if user.role != "student":
                raise ValueError(f"User {student_id} is not a student")
            
            # Check privacy flags
            privacy_flags = user.privacy_flags or {}
            share_moods = privacy_flags.get("share_moods", True)
            
            # Privacy enforcement
            if not share_moods and (not current_user or current_user.user_id != student_id):
                raise PermissionError("Student has disabled mood sharing")
            
            # Query moods collection
            moods_ref = (
                self.fs.db.collection("moods")
                .document(student_id)
                .collection("entries")
            )
            
            # Order by timestamp descending and limit results
            query = moods_ref.order_by(
                "timestamp", direction="DESCENDING"
            ).limit(limit)
            
            moods = []
            async for doc in query.stream():
                try:
                    mood_data = doc.to_dict()
                    mood_entry = {
                        "mood_id": mood_data["mood_id"],
                        "mood": mood_data["mood"],
                        "intensity": mood_data.get("intensity"),
                        "notes": mood_data.get("notes"),
                        "timestamp": mood_data["timestamp"].isoformat()
                        if hasattr(mood_data["timestamp"], "isoformat")
                        else str(mood_data["timestamp"]),
                        "created_at": mood_data.get("created_at", mood_data["timestamp"]).isoformat()
                        if hasattr(mood_data.get("created_at", mood_data["timestamp"]), "isoformat")
                        else str(mood_data.get("created_at", mood_data["timestamp"]))
                    }
                    moods.append(mood_entry)
                except Exception as e:
                    logger.error(f"Error parsing mood {doc.id}: {e}")
                    continue
            
            # Log the access
            if current_user:
                await self.logging_service.create_access_log(
                    user_id=student_id,
                    resource="moods",
                    action="view",
                    performed_by=current_user.user_id,
                    performed_by_role=current_user.role or "unknown",
                    metadata={
                        "action_type": "get_mood_history",
                        "limit": str(limit),
                        "results_count": str(len(moods))
                    }
                )
            
            logger.info(f"Retrieved {len(moods)} mood entries for {student_id}")
            return moods
            
        except (ValueError, PermissionError):
            raise
        except Exception as e:
            logger.error(f"Error getting mood history for student {student_id}: {e}")
            raise Exception(f"Failed to get mood history: {str(e)}")
    
    async def get_mood_stream_data(
        self, 
        current_user: User,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get recent mood updates from multiple students for real-time feed.
        Only returns data from students who have mood sharing enabled.
        
        Args:
            current_user: User requesting the stream (must be authenticated)
            limit: Maximum number of mood entries to return
            
        Returns:
            List of mood entries with student info from multiple students
        """
        try:
            logger.info(f"Getting mood stream for user {current_user.user_id}")
            
            # Get all students with mood sharing enabled
            users_ref = self.fs.db.collection("users")
            query = users_ref.where("role", "==", "student")
            
            mood_stream = []
            
            async for user_doc in query.stream():
                try:
                    user_data = user_doc.to_dict()
                    user_id = user_data["user_id"]
                    
                    # Check privacy flags
                    privacy_flags = user_data.get("privacy_flags", {})
                    if not privacy_flags.get("share_moods", True):
                        continue  # Skip students who disabled mood sharing
                    
                    # Get recent moods for this student
                    moods_ref = (
                        self.fs.db.collection("moods")
                        .document(user_id)
                        .collection("entries")
                    )
                    
                    recent_moods_query = moods_ref.order_by(
                        "timestamp", direction="DESCENDING"
                    ).limit(5)  # Get last 5 moods per student
                    
                    async for mood_doc in recent_moods_query.stream():
                        mood_data = mood_doc.to_dict()
                        
                        # Add student info to mood data
                        profile = user_data.get("profile", {})
                        mood_entry = {
                            "mood_id": mood_data["mood_id"],
                            "student_id": user_id,
                            "student_name": profile.get("name", "Anonymous"),
                            "mood": mood_data["mood"],
                            "intensity": mood_data.get("intensity"),
                            "timestamp": mood_data["timestamp"].isoformat()
                            if hasattr(mood_data["timestamp"], "isoformat")
                            else str(mood_data["timestamp"]),
                            # Don't include notes for privacy
                        }
                        mood_stream.append(mood_entry)
                        
                except Exception as e:
                    logger.warning(f"Error processing mood data for user {user_doc.id}: {e}")
                    continue
            
            # Sort all mood entries by timestamp descending and limit
            mood_stream.sort(
                key=lambda x: x["timestamp"], 
                reverse=True
            )
            mood_stream = mood_stream[:limit]
            
            # Log the stream access
            await self.logging_service.create_access_log(
                user_id=current_user.user_id,
                resource="moods",
                action="stream",
                performed_by=current_user.user_id,
                performed_by_role=current_user.role or "unknown",
                metadata={
                    "stream_size": str(len(mood_stream)),
                    "limit": str(limit)
                }
            )
            
            logger.info(f"Retrieved {len(mood_stream)} mood entries for stream")
            return mood_stream
            
        except Exception as e:
            logger.error(f"Error getting mood stream: {e}")
            raise Exception(f"Failed to get mood stream: {str(e)}")
    
    async def get_mood_analytics(self, current_user: User) -> Dict[str, Any]:
        """
        Get aggregated mood analytics across students with mood sharing enabled.
        
        Args:
            current_user: User requesting analytics
            
        Returns:
            Dictionary with mood analytics data
        """
        try:
            logger.info(f"Getting mood analytics for user {current_user.user_id}")
            
            # Get all students
            users_ref = self.fs.db.collection("users")
            query = users_ref.where("role", "==", "student")
            
            total_students = 0
            students_with_sharing = 0
            mood_distribution = {}
            total_mood_entries = 0
            recent_moods = []  # Last 24 hours
            
            from datetime import timedelta
            yesterday = datetime.now(timezone.utc) - timedelta(days=1)
            
            async for user_doc in query.stream():
                try:
                    user_data = user_doc.to_dict()
                    user_id = user_data["user_id"]
                    total_students += 1
                    
                    # Check privacy flags
                    privacy_flags = user_data.get("privacy_flags", {})
                    if not privacy_flags.get("share_moods", True):
                        continue  # Skip students who disabled mood sharing
                    
                    students_with_sharing += 1
                    
                    # Get recent moods for analytics
                    moods_ref = (
                        self.fs.db.collection("moods")
                        .document(user_id)
                        .collection("entries")
                    )
                    
                    # Get all moods for distribution
                    all_moods_query = moods_ref.order_by(
                        "timestamp", direction="DESCENDING"
                    ).limit(50)  # Last 50 moods per student for distribution
                    
                    async for mood_doc in all_moods_query.stream():
                        mood_data = mood_doc.to_dict()
                        mood = mood_data["mood"]
                        
                        mood_distribution[mood] = mood_distribution.get(mood, 0) + 1
                        total_mood_entries += 1
                        
                        # Check if mood is recent (last 24 hours)
                        mood_timestamp = mood_data["timestamp"]
                        if hasattr(mood_timestamp, 'timestamp'):
                            mood_datetime = datetime.fromtimestamp(
                                mood_timestamp.timestamp(), tz=timezone.utc
                            )
                        else:
                            mood_datetime = mood_timestamp
                        
                        if mood_datetime >= yesterday:
                            recent_moods.append(mood)
                        
                except Exception as e:
                    logger.warning(f"Error processing analytics for user {user_doc.id}: {e}")
                    continue
            
            # Calculate analytics
            mood_percentages = {}
            if total_mood_entries > 0:
                for mood, count in mood_distribution.items():
                    mood_percentages[mood] = round((count / total_mood_entries) * 100, 1)
            
            recent_mood_count = len(recent_moods)
            
            analytics = {
                "total_students": total_students,
                "students_with_mood_sharing": students_with_sharing,
                "total_mood_entries": total_mood_entries,
                "recent_mood_entries_24h": recent_mood_count,
                "mood_distribution": mood_distribution,
                "mood_percentages": mood_percentages,
                "average_moods_per_student": round(
                    total_mood_entries / students_with_sharing, 1
                ) if students_with_sharing > 0 else 0,
                "most_common_mood": max(mood_distribution, key=mood_distribution.get)
                if mood_distribution else None
            }
            
            # Log analytics access
            await self.logging_service.create_access_log(
                user_id=current_user.user_id,
                resource="moods",
                action="analytics",
                performed_by=current_user.user_id,
                performed_by_role=current_user.role or "unknown",
                metadata={
                    "total_entries_analyzed": str(total_mood_entries),
                    "students_analyzed": str(students_with_sharing)
                }
            )
            
            logger.info(f"Generated mood analytics with {total_mood_entries} entries")
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting mood analytics: {e}")
            raise Exception(f"Failed to get mood analytics: {str(e)}")
