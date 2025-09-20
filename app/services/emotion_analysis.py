# app/services/emotion_analysis.py
import json
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timezone

from app.services.gemini_ai import GeminiService
from app.services.mood_service import MoodService
from app.services.privacy_service import PrivacyService

logger = logging.getLogger(__name__)


class EmotionAnalysisService:
    """
    Service to analyze emotions from text and automatically infer moods.
    """

    def __init__(self):
        self.gemini_service = GeminiService()
        self.mood_service = MoodService()
        from app.services.firestore import FirestoreService
        firestore_service = FirestoreService()
        self.privacy_service = PrivacyService(firestore_service)

    async def analyze_text_emotion(self, text: str, language: str = "en") -> Dict[str, float]:
        """
        Analyze emotional content from text using Gemini AI.
        
        Args:
            text: The text to analyze
            language: Language code for the text
            
        Returns:
            Dictionary with emotion scores (0.0 to 1.0)
        """
        try:
            emotion_prompt = f"""
            Analyze the emotional content of this text and return ONLY a JSON object with emotion scores between 0.0 and 1.0:
            
            Text: "{text}"
            
            Return format (no other text):
            {{
                "happiness": 0.0,
                "sadness": 0.0,
                "anxiety": 0.0,
                "anger": 0.0,
                "fear": 0.0,
                "neutral": 0.0,
                "excitement": 0.0,
                "frustration": 0.0
            }}
            
            Consider cultural context and language nuances. For Hindi/Indian expressions like:
            - "ghabrahat" = anxiety
            - "pareshaan" = frustration/anxiety  
            - "khushi" = happiness
            - "udaas" = sadness
            """

            # Get emotion analysis from Gemini
            response = await self.gemini_service.process_cultural_conversation(
                text=emotion_prompt,
                options={"analysis_mode": "emotion", "language": language},
                language=language
            )

            # Extract JSON from response
            if isinstance(response, dict):
                raw_text = response.get("response", "{}")
            else:
                raw_text = str(response)

            # Parse the JSON response
            emotions = json.loads(raw_text)
            
            # Validate emotion scores are within 0.0-1.0 range
            validated_emotions = {}
            for emotion, score in emotions.items():
                validated_emotions[emotion] = max(0.0, min(1.0, float(score)))

            logger.info(f"Emotion analysis completed: {validated_emotions}")
            return validated_emotions

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse emotion JSON response: {e}")
            return self._fallback_emotion_analysis(text)
        except Exception as e:
            logger.error(f"Emotion analysis failed: {e}")
            return self._fallback_emotion_analysis(text)

    def _fallback_emotion_analysis(self, text: str) -> Dict[str, float]:
        """
        Fallback emotion analysis using keyword matching.
        """
        text_lower = text.lower()
        
        # Define emotion keywords (including Hindi/Indian terms)
        emotion_keywords = {
            "happiness": ["happy", "joy", "excited", "good", "great", "amazing", "khushi", "accha"],
            "sadness": ["sad", "depressed", "down", "upset", "cry", "udaas", "dukhi"],
            "anxiety": ["worried", "anxious", "nervous", "scared", "ghabrahat", "pareshan"],
            "anger": ["angry", "mad", "furious", "annoyed", "gussa", "naraz"],
            "fear": ["afraid", "terrified", "panic", "scared", "dar"],
            "frustration": ["frustrated", "annoyed", "irritated", "pareshan"],
            "excitement": ["excited", "thrilled", "pumped", "enthusiastic"],
            "neutral": ["okay", "fine", "normal", "usual", "theek"]
        }
        
        emotions = {}
        for emotion, keywords in emotion_keywords.items():
            score = sum(0.2 for keyword in keywords if keyword in text_lower)
            emotions[emotion] = min(1.0, score)
        
        # Default to neutral if no emotions detected
        if all(score < 0.1 for score in emotions.values()):
            emotions["neutral"] = 0.7
            
        return emotions

    def infer_mood_from_emotions(self, emotions: Dict[str, float]) -> Tuple[str, int, float]:
        """
        Infer mood state from emotion analysis.
        
        Args:
            emotions: Dictionary of emotion scores
            
        Returns:
            Tuple of (mood, intensity, confidence)
        """
        # Define mood mapping logic
        mood_rules = [
            # High confidence moods
            ("very_happy", lambda e: e.get("happiness", 0) > 0.7 and e.get("excitement", 0) > 0.5),
            ("happy", lambda e: e.get("happiness", 0) > 0.5),
            ("excited", lambda e: e.get("excitement", 0) > 0.6),
            
            ("very_sad", lambda e: e.get("sadness", 0) > 0.7),
            ("sad", lambda e: e.get("sadness", 0) > 0.5),
            ("depressed", lambda e: e.get("sadness", 0) > 0.6 and e.get("neutral", 0) < 0.3),
            
            ("very_anxious", lambda e: e.get("anxiety", 0) > 0.7 or e.get("fear", 0) > 0.6),
            ("anxious", lambda e: e.get("anxiety", 0) > 0.5),
            ("worried", lambda e: e.get("anxiety", 0) > 0.4 and e.get("fear", 0) > 0.3),
            
            ("angry", lambda e: e.get("anger", 0) > 0.5),
            ("frustrated", lambda e: e.get("frustration", 0) > 0.5),
            
            ("mixed", lambda e: sum(1 for v in e.values() if v > 0.4) >= 2),
            ("neutral", lambda e: e.get("neutral", 0) > 0.4 or max(e.values()) < 0.3),
        ]
        
        # Find the first matching mood rule
        for mood, rule in mood_rules:
            if rule(emotions):
                # Calculate intensity based on emotion strength
                max_emotion_score = max(emotions.values())
                intensity = max(1, min(10, int(max_emotion_score * 10)))
                
                # Calculate confidence based on how clear the emotions are
                confidence = max_emotion_score
                if sum(v for v in emotions.values() if v > 0.3) > 1:
                    confidence *= 0.8  # Lower confidence for mixed emotions
                
                return mood, intensity, confidence
        
        # Fallback to neutral
        return "neutral", 5, 0.5

    async def should_auto_update_mood(
        self, 
        user_id: str, 
        confidence: float, 
        min_confidence: float = 0.6
    ) -> bool:
        """
        Determine if mood should be automatically updated based on confidence and user preferences.
        
        Args:
            user_id: User ID
            confidence: Confidence score of mood inference
            min_confidence: Minimum confidence threshold
            
        Returns:
            True if mood should be auto-updated
        """
        # Check confidence threshold
        if confidence < min_confidence:
            return False
        
        # Check user privacy preferences
        try:
            privacy_result = await self.privacy_service.check_flags(user_id, "moods")
            return privacy_result.get("allowed", False)
        except Exception as e:
            logger.warning(f"Could not check privacy preferences for {user_id}: {e}")
            return False

    async def process_message_for_mood_inference(
        self, 
        user_id: str, 
        message_text: str, 
        language: str = "en",
        conversation_id: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Process a chat message for automatic mood inference and update.
        
        Args:
            user_id: User ID
            message_text: Text content of the message
            language: Language of the message
            conversation_id: Optional conversation ID for context
            
        Returns:
            Dictionary with mood inference results or None if no update made
        """
        try:
            # Skip very short messages (likely not emotionally significant)
            if len(message_text.strip()) < 10:
                return None

            # Analyze emotions in the text
            emotions = await self.analyze_text_emotion(message_text, language)
            
            # Infer mood from emotions
            mood, intensity, confidence = self.infer_mood_from_emotions(emotions)
            
            logger.info(
                f"Mood inference for user {user_id}: {mood} "
                f"(intensity: {intensity}, confidence: {confidence:.2f})"
            )
            
            # Check if we should auto-update
            should_update = await self.should_auto_update_mood(user_id, confidence)
            
            result = {
                "emotions": emotions,
                "inferred_mood": mood,
                "intensity": intensity,
                "confidence": confidence,
                "auto_updated": False,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            if should_update:
                # Auto-update the user's mood
                try:
                    mood_notes = f"Auto-inferred from chat (confidence: {confidence:.1%})"
                    await self.mood_service.update_mood(
                        user_id=user_id,
                        mood=mood,
                        intensity=intensity,
                        notes=mood_notes
                    )
                    result["auto_updated"] = True
                    logger.info(f"Auto-updated mood for user {user_id}: {mood}")
                    
                except Exception as e:
                    logger.error(f"Failed to auto-update mood for user {user_id}: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"Mood inference processing failed for user {user_id}: {e}")
            return None
