import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from app.services import gemini_ai
from app.models.db_models import User
from app.models.db_models import CrisisAlert

logger = logging.getLogger(__name__)

class CrisisService:
    """
    Student-first crisis detection and escalation service for MITRA.
    Combines keyword and Gemini-based risk scoring, logs all escalations,
    and supports Tele MANAS and optional WhatsApp parent alerts.
    """

    DEFAULT_KEYWORDS = {
        "en": [
            ("suicide", 6), ("kill myself", 6), ("self-harm", 5), ("depressed", 4),
            ("hopeless", 4), ("panic", 3), ("anxious", 3), ("crying", 2),
            ("can't cope", 4), ("overwhelmed", 3), ("worthless", 4),
        ],
        "hi": [
            ("aatmahatya", 6), ("marna hai", 6), ("dukhi", 4), ("ghabrahat", 3),
            ("mann nahi lagta", 3), ("nirash", 4),
        ],
        "ta": [
            ("uyir kollikiren", 6), ("thuyaram", 4), ("bayam", 3),
        ],
        "te": [
            ("aatmahatya", 6), ("chavu", 6), ("badha", 4),
        ],
    }

    RISK_LEVELS = [
        (0, 3, "low"),
        (4, 6, "medium"),
        (7, 10, "high"),
    ]

    def __init__(
        self,
        firestore_client=None,
        gemini_service: Optional[Any] = None,
        twilio_client: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Args:
            firestore_client: Firestore client (async)
            gemini_service: GeminiService instance
            twilio_client: Twilio client (optional)
            config: dict for config overrides
        """
        self.firestore = firestore_client
        self.gemini_service = gemini_service
        self.twilio_client = twilio_client
        self.config = config or {}
        self.cooldown_hours = int(self.config.get("CRISIS_COOLDOWN_HOURS", os.getenv("CRISIS_COOLDOWN_HOURS", 24)))
        self.whatsapp_enabled = bool(self.config.get("WHATSAPP_ENABLED", os.getenv("WHATSAPP_ENABLED", False)))
        self.firestore_collection = self.config.get("FIRESTORE_COLLECTION", "crisis_escalations")
        self.telemanas_collection = self.config.get("TELEMANAS_COLLECTION", "telemanas_attempts")
        self.twilio_from = self.config.get("TWILIO_WHATSAPP_FROM", os.getenv("TWILIO_WHATSAPP_FROM", None))

    def detect_keywords(self, text: str) -> int:
        """
        Deterministic keyword-based risk scoring.
        Returns score 0–6.
        """
        score = 0
        text_lower = text.lower()
        for lang, kwlist in self.DEFAULT_KEYWORDS.items():
            for phrase, weight in kwlist:
                if phrase in text_lower:
                    score = max(score, weight)
        logger.info(f"Keyword risk score: {score} for text: {text[:40]}...")
        return score

    async def assess_with_gemini(self, text: str) -> int:
        """
        Use Gemini to assess risk (0–10). Returns 0 if Gemini unavailable.
        """
        if not self.gemini_service:
            logger.warning("Gemini service not provided, returning safe default risk score 0.")
            return 0
        try:
            score = await self.gemini_service.analyze_risk(text)
            logger.info(f"Gemini risk score: {score} for text: {text[:40]}...")
            return max(0, min(10, score))
        except Exception as e:
            logger.error(f"Gemini risk analysis failed: {e}")
            return 0

    def combine_scores(self, kw_score: int, gemini_score: int) -> int:
        """
        Weighted combination: final = round(0.6*gemini + 0.4*keyword), clamp 0–10.
        """
        final = round(0.6 * gemini_score + 0.4 * kw_score)
        final = max(0, min(10, final))
        logger.info(f"Combined risk score: {final} (kw={kw_score}, gemini={gemini_score})")
        return final

    async def assess_risk(
        self,
        user_id: str,
        text: str,
        gemini_response: Optional[dict] = None,
    ) -> Dict[str, Any]:
        """
        Returns dict: { "risk_score": int, "risk_level": str, "reason": str }
        """
        # Fetch user profile (age, parent_escalation, parent_contact)
        user_profile = await self._get_user_profile(user_id)
        kw_score = self.detect_keywords(text)
        if gemini_response and "risk_score" in gemini_response:
            gemini_score = gemini_response.get("risk_score")
        else:
            gemini_score = await self.assess_with_gemini(text)
        risk_score = self.combine_scores(kw_score, gemini_score)
        risk_level = self._risk_level_from_score(risk_score)
        reason = f"keyword:{kw_score}; gemini_score:{gemini_score}; parent_contact:{'present' if user_profile.get('parent_contact') else 'absent'}"
        logger.info(f"Risk assessment for user {user_id}: score={risk_score}, level={risk_level}, reason={reason}")
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "reason": reason,
            "user_profile": user_profile,
        }

    async def escalate(self, user_id: str, risk_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Escalate based on risk report. Logs to Firestore, calls Tele MANAS stub,
        and optionally sends WhatsApp to parent.
        """
        if await self.is_under_cooldown(user_id):
            logger.warning(f"Escalation blocked by cooldown for user {user_id}.")
            return {"status": "cooldown", "action": "none"}

        user_profile = risk_report.get("user_profile") or await self._get_user_profile(user_id)
        risk_score = risk_report["risk_score"]
        risk_level = risk_report["risk_level"]
        consent = user_profile.get("parent_escalation")
        parent_contact = user_profile.get("parent_contact")
        age = user_profile.get("age")
        timestamp = datetime.now(timezone.utc).isoformat()
        action = "none"
        notes = risk_report.get("reason", "")

        escalate_parent = self.should_escalate_to_parent(user_profile, risk_score)
        escalate_telemanas = risk_level == "high"

        # Compose escalation action
        if escalate_telemanas and escalate_parent and parent_contact:
            action = "tele_manas+parent"
        elif escalate_telemanas:
            action = "tele_manas"
        elif escalate_parent and parent_contact:
            action = "parent_whatsapp"
        else:
            action = "none"

        # Log escalation to Firestore
        escalation_doc = {
            "user_id": user_id,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "action": action,
            "timestamp": timestamp,
            "consent": consent,
            "notes": notes,
        }
        await self._log_escalation(escalation_doc)

        # Tele MANAS stub
        telemanas_result = None
        if "tele_manas" in action:
            telemanas_result = await self._telemanas_notify_stub(user_id, escalation_doc)

        # WhatsApp parent (Twilio placeholder)
        whatsapp_result = None
        if "parent" in action and parent_contact and self.whatsapp_enabled:
            whatsapp_result = self._send_whatsapp_to_parent(
                parent_contact,
                f"MITRA Alert: Your child ({user_id}) has a {risk_level.upper()} risk score ({risk_score}) as of {timestamp}. Please contact Tele MANAS (14416) if needed.",
            )

        logger.warning(f"Escalation performed for user {user_id}: action={action}")
        return {
            "status": "escalated",
            "action": action,
            "telemanas_result": telemanas_result,
            "whatsapp_result": whatsapp_result,
            "escalation_doc": escalation_doc,
        }

    def should_escalate_to_parent(self, user_profile: dict, risk_score: int) -> bool:
        """
        Minor: always escalate to parent if contact exists and high risk.
        Adult: only if parent_escalation consent is True.
        """
        age = user_profile.get("age")
        parent_contact = user_profile.get("parent_contact")
        consent = user_profile.get("parent_escalation")
        if age is None:
            logger.warning("User age missing, defaulting to no parent escalation.")
            return False
        if age < 18 and parent_contact and risk_score >= 7:
            return True
        if age >= 18 and consent and parent_contact and risk_score >= 7:
            return True
        return False

    async def _telemanas_notify_stub(self, user_id, risk_report) -> dict:
        """
        Stub for Tele MANAS integration.
        Writes a Firestore entry and returns status.
        # TODO: replace with real Tele MANAS API integration.
        """
        doc = {
            "user_id": user_id,
            "risk_level": risk_report.get("risk_level"),
            "risk_score": risk_report.get("risk_score"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "stub_logged",
        }
        if self.firestore:
            await self.firestore.collection(self.telemanas_collection).document(f"{user_id}_{doc['timestamp']}").set(doc)
        logger.info(f"Tele MANAS stub logged for user {user_id}.")
        return {"status": "stub_logged"}

    def _send_whatsapp_to_parent(self, phone_number: str, message: str, simulate: bool = False) -> dict:
        """
        Twilio WhatsApp placeholder. Only sends minimal context.
        """
        if simulate or not self.twilio_client:
            logger.info(f"Simulated WhatsApp to {phone_number}: {message}")
            return {"status": "simulated", "to": phone_number}
        try:
            msg = self.twilio_client.messages.create(
                body=message,
                from_=self.twilio_from,
                to=phone_number,
            )
            logger.info(f"WhatsApp sent to {phone_number}: SID={msg.sid}")
            return {"status": "sent", "sid": msg.sid}
        except Exception as e:
            logger.error(f"WhatsApp send failed: {e}")
            raise

    async def is_under_cooldown(self, user_id: str) -> bool:
        """
        Returns True if an escalation exists within the cooldown window.
        """
        if not self.firestore:
            logger.warning("Firestore client not provided, skipping cooldown check.")
            return False
        cutoff = datetime.now(timezone.utc) - timedelta(hours=self.cooldown_hours)
        query = (
            self.firestore.collection(self.firestore_collection)
            .where("user_id", "==", user_id)
            .where("timestamp", ">", cutoff.isoformat())
        )
        docs = []
        async for doc in query.stream():
            docs.append(doc)
        under_cooldown = len(docs) > 0
        logger.info(f"Cooldown check for user {user_id}: {under_cooldown}")
        return under_cooldown

    def _risk_level_from_score(self, score: int) -> str:
        for low, high, label in self.RISK_LEVELS:
            if low <= score <= high:
                return label
        return "low"

    async def _get_user_profile(self, user_id: str) -> dict:
        """
        Fetch minimal user profile from Firestore.
        """
        if not self.firestore:
            logger.warning("Firestore client not provided, returning default user profile.")
            return {"age": None, "parent_escalation": None, "parent_contact": None}
        doc = await self.firestore.collection("users").document(user_id).get()
        if doc.exists:
            data = doc.to_dict()
            return {
                "age": data.get("age"),
                "parent_escalation": data.get("parent_escalation"),
                "parent_contact": data.get("parent_contact"),
            }
        return {"age": None, "parent_escalation": None, "parent_contact": None}

    async def _log_escalation(self, escalation_doc: dict):
        """
        Write escalation event to Firestore.
        """
        if not self.firestore:
            logger.warning("Firestore client not provided, escalation not logged.")
            return
        doc_id = f"{escalation_doc['user_id']}_{escalation_doc['timestamp']}"
        await self.firestore.collection(self.firestore_collection).document(doc_id).set(escalation_doc)
        logger.info(f"Escalation logged for user {escalation_doc['user_id']}.")


# Example usage:
# crisis = CrisisService(firestore_client=firestore, gemini_service=gemini, twilio_client=twilio)
# risk_report = crisis.assess_risk(user_id, user_message)
# if risk_report["risk_level"] in ("medium", "high"):
#     result = crisis.escalate(user_id, risk_report)