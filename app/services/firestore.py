from google.cloud import firestore
from app.models.db_models import AnonymousUser, Conversation, PeerCircle, CrisisAlert
from typing import Optional, List
from datetime import datetime, UTC


class FirestoreService:
    def __init__(self):
        self.db = firestore.Client()

    # ---------------------------
    # Anonymous User Operations
    # ---------------------------
    async def create_anonymous_user(self, user: AnonymousUser) -> str:
        doc_ref = self.db.collection("anonymous_users").document(user.user_id)
        doc_ref.set(user.model_dump())
        return user.user_id

    async def get_anonymous_user(self, user_id: str) -> Optional[AnonymousUser]:
        doc = self.db.collection("anonymous_users").document(user_id).get()
        if doc.exists:
            return AnonymousUser(**doc.to_dict())
        return None

    async def update_anonymous_user_last_active(
        self, user_id: str, last_active: datetime
    ):
        doc_ref = self.db.collection("anonymous_users").document(user_id)
        doc_ref.update({"last_active": last_active})

    # ---------------------------
    # Conversation Operations
    # ---------------------------
    async def store_conversation(self, conversation: Conversation):
        doc_ref = self.db.collection("conversations").document(
            conversation.conversation_id
        )
        doc_ref.set(conversation.model_dump())

    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        doc = self.db.collection("conversations").document(conversation_id).get()
        if doc.exists:
            return Conversation(**doc.to_dict())
        return None

    # Append a message to conversation messages list atomically
    async def add_message_to_conversation(self, conversation_id: str, message: dict):
        doc_ref = self.db.collection("conversations").document(conversation_id)
        doc_ref.update(
            {
                "messages": firestore.ArrayUnion([message]),
                "updated_at": datetime.now(UTC),
            }
        )

    # ---------------------------
    # Peer Circle Operations
    # ---------------------------
    async def create_peer_circle(self, circle: PeerCircle) -> str:
        doc_ref = self.db.collection("peer_circles").document(circle.circle_id)
        doc_ref.set(circle.dict())
        return circle.circle_id

    async def get_peer_circle(self, circle_id: str) -> Optional[PeerCircle]:
        doc = self.db.collection("peer_circles").document(circle_id).get()
        if doc.exists:
            return PeerCircle(**doc.to_dict())
        return None

    async def find_peer_matches(
        self, cultural_background: str, interests: List[str], limit: int = 10
    ) -> List[str]:
        # Example: query anonymous users who match cultural background (can be extended with interest filters)
        query = (
            self.db.collection("anonymous_users")
            .where("cultural_background", "==", cultural_background)
            .limit(limit)
        )
        users = query.stream()
        return [user.id for user in users]

    # ---------------------------
    # Crisis Alert Operations
    # ---------------------------
    async def store_crisis_alert(self, alert: CrisisAlert) -> str:
        doc_ref = self.db.collection("crisis_alerts").document(alert.alert_id)
        doc_ref.set(alert.dict())
        return alert.alert_id

    async def update_crisis_alert_status(
        self, alert_id: str, status: str, resolved_at: Optional[datetime] = None
    ):
        doc_ref = self.db.collection("crisis_alerts").document(alert_id)
        update_data = {"escalation_status": status}
        if resolved_at:
            update_data["resolved_at"] = resolved_at
        doc_ref.update(update_data)

    async def get_crisis_alert(self, alert_id: str) -> Optional[CrisisAlert]:
        doc = self.db.collection("crisis_alerts").document(alert_id).get()
        if doc.exists:
            return CrisisAlert(**doc.to_dict())
        return None

    # ---------------------------
    # Analytics (Optional)
    # ---------------------------
    # Add methods here to track anonymized usage patterns, cultural insights, feedback etc.
