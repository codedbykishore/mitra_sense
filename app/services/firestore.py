# app/db/firestore.py
from typing import Optional
from google.cloud import firestore
from app.models.db_models import User, Conversation, PeerCircle, CrisisAlert


class FirestoreService:
    def __init__(self):
        self.db = firestore.AsyncClient()  # <-- async client

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
