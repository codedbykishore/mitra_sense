# app/db/firestore.py
from typing import Optional, List
from google.cloud import firestore
from app.models.db_models import (
    User, Conversation, Message, PeerCircle, CrisisAlert, Institution
)
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class FirestoreService:
    def __init__(self):
        try:
            if settings.GOOGLE_PROJECT_ID:
                self.db = firestore.AsyncClient(
                    project=settings.GOOGLE_PROJECT_ID
                )
                logger.info(
                    f"Initialized Firestore with project: "
                    f"{settings.GOOGLE_PROJECT_ID}"
                )
            else:
                self.db = firestore.AsyncClient()
                logger.info("Initialized Firestore with default credentials")
        except Exception as e:
            logger.error(f"Failed to initialize Firestore client: {e}")
            raise

    # ---------- USER ----------
    async def create_user(self, user: User) -> None:
        await self.db.collection("users").document(user.user_id).set(user.model_dump())

    async def get_user(self, user_id: str) -> Optional[User]:
        doc = await self.db.collection("users").document(user_id).get()
        if doc.exists:
            return User(**doc.to_dict())
        return None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Fetch a user by their email address."""
        coll_ref = self.db.collection("users")
        query = coll_ref.where("email", "==", email)
        
        async for doc in query.stream():  # ✅ async for
            return User(**doc.to_dict())
        
        return None

    async def update_user(self, user_id: str, data: dict) -> None:
        await self.db.collection("users").document(user_id).update(data)

    async def delete_user(self, user_id: str) -> None:
        await self.db.collection("users").document(user_id).delete()

    async def complete_onboarding(
        self, user_id: str, role: str, profile: dict,
        institution_id: Optional[str] = None
    ) -> None:
        """Complete user onboarding with role and profile data."""
        update_data = {
            "onboarding_completed": True,
            "role": role,
            "profile": profile
        }
        
        # Add institution_id for students
        if role == "student":
            update_data["institution_id"] = institution_id
            
        await self.db.collection("users").document(user_id).update(update_data)

    # ---------- CONVERSATION ----------
    async def store_conversation(self, conversation: Conversation) -> None:
        await (
            self.db.collection("conversations")
            .document(conversation.conversation_id)
            .set(conversation.model_dump())
        )

    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        doc = await self.db.collection("conversations").document(conversation_id).get()
        if doc.exists:
            return Conversation(**doc.to_dict())
        return None

    async def update_conversation(self, conversation_id: str, data: dict) -> None:
        await self.db.collection("conversations").document(conversation_id).update(data)

    async def delete_conversation(self, conversation_id: str) -> None:
        await self.db.collection("conversations").document(conversation_id).delete()

    async def add_message_to_conversation(
        self, conversation_id: str, message: dict
    ) -> None:
        ref = self.db.collection("conversations").document(conversation_id)
        await ref.update({"messages": firestore.ArrayUnion([message])})

    async def create_or_update_conversation(self, user_id: str) -> str:
        """Create new conversation if none exists or return active one."""
        from datetime import datetime, timezone
        import uuid
        
        # Check for existing active conversation for user
        conversations_ref = self.db.collection("conversations")
        query = conversations_ref.where(
            "participants", "array_contains", user_id
        )
        
        # Get the most recent conversation
        recent_conversation = None
        async for doc in query.stream():
            conversation_data = doc.to_dict()
            last_active = conversation_data.get("last_active_at")
            if (not recent_conversation or
                    last_active > recent_conversation.get("last_active_at")):
                recent_conversation = conversation_data
                recent_conversation["conversation_id"] = doc.id
        
        if recent_conversation:
            # Update last_active_at and return existing conversation
            conversation_id = recent_conversation["conversation_id"]
            await self.update_conversation(conversation_id, {
                "last_active_at": datetime.now(timezone.utc)
            })
            return conversation_id
        
        # Create new conversation
        conversation_id = str(uuid.uuid4())
        conversation = Conversation(
            conversation_id=conversation_id,
            participants=[user_id],
            created_at=datetime.now(timezone.utc),
            last_active_at=datetime.now(timezone.utc)
        )
        
        await self.store_conversation(conversation)
        return conversation_id

    async def save_message(
        self, conversation_id: str, message_data: dict
    ) -> None:
        """Save message under conversations/{conversation_id}/messages."""
        from datetime import datetime, timezone
        
        # Update conversation's last_active_at
        await self.update_conversation(conversation_id, {
            "last_active_at": datetime.now(timezone.utc)
        })
        
        # Save message to subcollection
        message_ref = (
            self.db.collection("conversations")
            .document(conversation_id)
            .collection("messages")
            .document(message_data["message_id"])
        )
        await message_ref.set(message_data)

    async def get_messages(
        self, conversation_id: str, limit: int = 50
    ) -> List[dict]:
        """
        Get messages for a conversation, ordered by timestamp ascending.
        
        Args:
            conversation_id: The ID of the conversation
            limit: Maximum number of messages to return
            
        Returns:
            List of message dictionaries ordered by timestamp (oldest first)
        """
        try:
            messages_ref = (
                self.db.collection("conversations")
                .document(conversation_id)
                .collection("messages")
            )
            
            # Order by timestamp ascending (oldest first) and limit results
            query = messages_ref.order_by("timestamp").limit(limit)
            
            messages = []
            async for doc in query.stream():
                message_data = doc.to_dict()
                messages.append(message_data)
            
            logger.info(
                f"Retrieved {len(messages)} messages for "
                f"conversation {conversation_id}"
            )
            return messages
            
        except Exception as e:
            logger.error(
                f"Error retrieving messages for "
                f"conversation {conversation_id}: {e}"
            )
            return []

    async def get_user_conversations(self, user_id: str) -> List[dict]:
        """
        Get conversations where user_id is a participant,
        sorted by last_active_at descending.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            List of conversation dictionaries sorted by last activity
            (newest first)
        """
        try:
            conversations_ref = self.db.collection("conversations")
            
            # Query conversations where user_id is in participants array
            query = conversations_ref.where(
                "participants", "array_contains", user_id
            )
            
            conversations = []
            async for doc in query.stream():
                conversation_data = doc.to_dict()
                # Add the document ID as conversation_id for easier access
                conversation_data["conversation_id"] = doc.id
                conversations.append(conversation_data)
            
            # Sort by last_active_at descending (newest first)
            conversations.sort(
                key=lambda x: x.get("last_active_at", x.get("created_at")),
                reverse=True
            )
            
            logger.info(
                f"Retrieved {len(conversations)} conversations for "
                f"user {user_id}"
            )
            return conversations
            
        except Exception as e:
            logger.error(
                f"Error retrieving conversations for user {user_id}: {e}"
            )
            return []

    # ---------- PEER CIRCLE ----------
    async def create_peer_circle(self, circle: PeerCircle) -> None:
        await (
            self.db.collection("peer_circles")
            .document(circle.circle_id)
            .set(circle.model_dump())
        )

    async def get_peer_circle(self, circle_id: str) -> Optional[PeerCircle]:
        doc = await self.db.collection("peer_circles").document(circle_id).get()
        if doc.exists:
            return PeerCircle(**doc.to_dict())
        return None

    async def update_peer_circle(self, circle_id: str, data: dict) -> None:
        await self.db.collection("peer_circles").document(circle_id).update(data)

    async def delete_peer_circle(self, circle_id: str) -> None:
        await self.db.collection("peer_circles").document(circle_id).delete()

    # ---------- CRISIS ALERT ----------
    async def create_crisis_alert(self, alert: CrisisAlert) -> None:
        await (
            self.db.collection("crisis_alerts")
            .document(alert.alert_id)
            .set(alert.model_dump())
        )

    async def get_crisis_alert(self, alert_id: str) -> Optional[CrisisAlert]:
        doc = await self.db.collection("crisis_alerts").document(alert_id).get()
        if doc.exists:
            return CrisisAlert(**doc.to_dict())
        return None

    async def update_crisis_alert(self, alert_id: str, data: dict) -> None:
        await self.db.collection("crisis_alerts").document(alert_id).update(data)

    async def delete_crisis_alert(self, alert_id: str) -> None:
        await self.db.collection("crisis_alerts").document(alert_id).delete()

    # ---------- INSTITUTION ----------
    async def create_institution(self, institution: Institution) -> None:
        """Create a new institution."""
        try:
            name = institution.institution_name
            logger.info(f"Creating institution: {name}")
            await (
                self.db.collection("institutions")
                .document(institution.institution_id)
                .set(institution.model_dump())
            )
            logger.info(f"Successfully created institution: {name}")
        except Exception as e:
            name = institution.institution_name
            logger.error(f"Failed to create institution {name}: {e}")
            raise

    async def get_institution(self, institution_id: str) -> Optional[Institution]:
        """Get institution by ID."""
        doc = await (
            self.db.collection("institutions")
            .document(institution_id)
            .get()
        )
        if doc.exists:
            return Institution(**doc.to_dict())
        return None

    async def get_institution_by_name(self, name: str) -> Optional[Institution]:
        """Get institution by name (case-insensitive)."""
        coll_ref = self.db.collection("institutions")
        query = coll_ref.where("institution_name", "==", name)
        
        async for doc in query.stream():
            return Institution(**doc.to_dict())
        
        return None

    async def list_institutions(self) -> List[Institution]:
        """List all active institutions."""
        try:
            institutions = []
            coll_ref = self.db.collection("institutions")
            
            # Use a simple query without ordering to avoid index requirement
            # We'll sort in Python instead
            query = coll_ref.where("active", "==", True)
            
            logger.info("Querying institutions from Firestore...")
            async for doc in query.stream():
                try:
                    institution_data = doc.to_dict()
                    name = institution_data.get('institution_name')
                    logger.info(f"Found institution: {name}")
                    institutions.append(Institution(**institution_data))
                except Exception as e:
                    logger.error(f"Error parsing institution {doc.id}: {e}")
                    continue
            
            # Sort by institution name in Python
            institutions.sort(key=lambda x: x.institution_name)
            
            logger.info(f"Total institutions found: {len(institutions)}")
            return institutions
        except Exception as e:
            logger.error(f"Error listing institutions: {e}")
            return []

    async def update_institution(self, institution_id: str, data: dict) -> None:
        """Update institution data."""
        await (
            self.db.collection("institutions")
            .document(institution_id)
            .update(data)
        )

    async def increment_student_count(self, institution_id: str) -> None:
        """Increment the student count for an institution."""
        if institution_id:  # Only if institution exists
            await (
                self.db.collection("institutions")
                .document(institution_id)
                .update({"student_count": firestore.Increment(1)})
            )

    async def decrement_student_count(self, institution_id: str) -> None:
        """Decrement the student count for an institution."""
        if institution_id:  # Only if institution exists
            await (
                self.db.collection("institutions")
                .document(institution_id)
                .update({"student_count": firestore.Increment(-1)})
            )
