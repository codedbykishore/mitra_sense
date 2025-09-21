# app/services/gemini_ai.py
import asyncio
import os
import json
from typing import Optional, Any, Dict, List, Tuple
import vertexai # Use vertexai for initialization
from vertexai import rag # Import rag for RAG functionality
from vertexai.generative_models import GenerativeModel, Tool # For RAG-enabled model
from langdetect import detect, detect_langs, DetectorFactory, LangDetectException
# LANGUAGES is not directly importable in newer versions, we'll define our own mapping
from app.config import settings
import logging

# Ensure consistent results for language detection
DetectorFactory.seed = 0

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self, project_id: Optional[str] = None, location: str = "us-central1", 
                 model_name: str = "gemini-2.0-flash", rag_corpus_name: Optional[str] = None):
        """
        GeminiService for Vertex AI (GenerativeModel) with RAG support and language awareness.
        
        Args:
            project_id: Google Cloud project ID
            location: GCP region (default: us-central1)
            model_name: Name of the Gemini model to use (default: gemini-2.0-flash)
            rag_corpus_name: Name of the RAG corpus to use for retrieval
        """
        # First prefer explicit argument, then settings, then environment
        project_id = project_id or getattr(settings, "GOOGLE_PROJECT_ID", None)
        
        if not project_id:
            raise ValueError("project_id not provided and could not be auto-detected from settings/credentials")

        self.project_id = project_id
        self.location = location
        self.model_name = model_name
        self.rag_corpus_name = rag_corpus_name or getattr(settings, "CORPUS_NAME", None)

        # Initialize Vertex AI
        try:
            vertexai.init(project=self.project_id, location=self.location)
            logger.info("Vertex AI API initialized successfully for GeminiService.")
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI API: {e}")
            raise

        # Initialize the base model
        self.model = GenerativeModel(model_name=self.model_name)
        self.rag_enabled = bool(self.rag_corpus_name)
        
        if self.rag_enabled:
            # We'll create the RAG tool dynamically in the analyze method
            # to support language-specific filtering
            logger.info(f"RAG support enabled with corpus: {self.rag_corpus_name}")
        else:
            logger.info("RAG support not enabled (no corpus name provided)")

    def _create_rag_tool(self, language: Optional[str] = None) -> Tool:
        """
        Create a RAG tool with optional language filtering.
        
        Args:
            language: Optional language code to filter RAG results
            
        Returns:
            Configured Tool instance for RAG
        """
        # Base retrieval config
        rag_retrieval_config = rag.RagRetrievalConfig(top_k=3)
        
        # Add language filter if specified
        rag_filters = []
        if language:
            rag_filters.append(f"language='{language}'")
            logger.debug(f"Adding language filter: {language}")
        
        # Create the RAG resource (without filters for now - filter format issue)
        rag_resource = rag.RagResource(
            rag_corpus=self.rag_corpus_name
            # Note: rag_filters parameter format needs verification
        )
        
        return Tool.from_retrieval(
            retrieval=rag.Retrieval(
                source=rag.VertexRagStore(
                    rag_resources=[rag_resource],
                    rag_retrieval_config=rag_retrieval_config
                ),
            )
        )
        
    async def analyze(self, text: str, language: Optional[str] = None) -> Any:
        """
        Run the model.generate_content call with optional RAG and language filtering.
        
        Args:
            text: The input text to process
            language: Optional language code to filter RAG results and set response language
            
        Returns:
            The raw response from the model
        """
        def sync_call():
            contents: List[Any] = [text]
            tools = []
            
            # Add language instruction if specified
            if language:
                lang_name = self.get_language_name(language)
                contents.append(f"Please respond in {lang_name}.")
            
            # Add RAG tool if enabled
            if self.rag_enabled:
                rag_tool = self._create_rag_tool(language)
                tools.append(rag_tool)
            
            # Generate content with tools if RAG is enabled
            return self.model.generate_content(
                contents=contents,
                tools=tools if tools else None
            )
        
        try:
            return await asyncio.to_thread(sync_call)
        except Exception as e:
            logger.error(f"Error in analyze: {str(e)}")
            # Fallback to non-RAG response if RAG fails
            if self.rag_enabled:
                logger.warning("Falling back to non-RAG response due to error")
                self.rag_enabled = False
                return await self.analyze(text, language)
            raise
    

    async def analyze_risk(self, text: str, language: Optional[str] = None) -> int:
        """
        Analyze the input text for crisis risk using Gemini and return a risk score (0-10).
        Attempts to extract a risk score from the model's response; defaults to 0 if not found.
        Includes debug logging to inspect Gemini's raw response.
        """
        import re

        prompt = (
            f"You are a mental health risk assessment AI. "
            f"Given the following message, return ONLY a single integer risk score (0-10) for crisis risk. "
            f"0 = no risk, 10 = immediate crisis.\n"
            f"Message: {text}\nRisk score:"
        )
        try:
            resp = await self.analyze(prompt, language)
            logger.debug(f"[GeminiService] Raw Gemini response for risk prompt: {repr(resp)}")

            score = None
            # Try to extract score from common response shapes
            if isinstance(resp, dict):
                for key in ("response", "output", "content"):
                    val = resp.get(key)
                    if val is not None:
                        logger.debug(f"[GeminiService] Found key '{key}' in response: {repr(val)}")
                        score = val
                        break
            elif hasattr(resp, "text"):
                logger.debug(f"[GeminiService] Found .text in response: {repr(resp.text)}")
                score = resp.text
            else:
                logger.debug(f"[GeminiService] Fallback: using str(resp): {repr(str(resp))}")
                score = str(resp)

            # Extract integer from score string
            match = re.search(r"\b(\d{1,2})\b", str(score))
            if match:
                value = int(match.group(1))
                logger.info(f"[GeminiService] Extracted risk score: {value} from response: {repr(score)}")
                return max(0, min(10, value))
            else:
                logger.warning(f"[GeminiService] Could not extract risk score from Gemini response: {repr(score)}")
                return 0
        except Exception as e:
            logger.error(f"[GeminiService] Gemini risk analysis failed: {e}")
            return 0


    def detect_language(self, text: str) -> Tuple[str, float]:
        """
        Detect the language of the input text.
        
        Args:
            text: Input text to detect language from
            
        Returns:
            Tuple of (language_code, confidence)
        """
        try:
            # Clean and normalize text
            text = text.strip()
            
            # For very short text, use English bias with common English patterns
            if len(text.split()) <= 3:
                english_patterns = [
                    "let's", "let us", "i'm", "i am", "you're", "you are", "can't", "cannot",
                    "don't", "do not", "won't", "will not", "that's", "that is",
                    "i", "you", "we", "they", "the", "and", "or", "but", "plan", "help"
                ]
                text_lower = text.lower()
                if any(pattern in text_lower for pattern in english_patterns):
                    return 'en', 0.95
            
            # Get all possible languages with probabilities
            languages = detect_langs(text)
            if not languages:
                return 'en', 0.0
                
            # Get the most probable language
            best_match = languages[0]
            
            # Additional confidence adjustment for short text
            confidence = best_match.prob
            if len(text.split()) <= 3 and best_match.lang != 'en':
                confidence *= 0.7  # Reduce confidence for non-English detection on short phrases
                
            return best_match.lang, confidence
            
        except LangDetectException:
            return 'en', 0.0
            
    def get_language_name(self, lang_code: str) -> str:
        """Get full language name from language code."""
        # Common language code to name mapping
        LANGUAGE_NAMES = {
            'en': 'English',
            'hi': 'Hindi',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'ar': 'Arabic',
            'bn': 'Bengali',
            'pa': 'Punjabi',
            'ta': 'Tamil',
            'te': 'Telugu',
            'mr': 'Marathi',
            'gu': 'Gujarati',
            'kn': 'Kannada',
            'ml': 'Malayalam',
            'or': 'Odia',
        }
        return LANGUAGE_NAMES.get(lang_code, 'English')

    async def process_cultural_conversation(self, text: str, options: Optional[Dict] = None, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Process conversation with cultural context awareness and language detection.
        
        Args:
            text: The input text from the user
            options: Additional options for the conversation, including RAG context
            language: Optional language code to force response in a specific language
            
        Returns:
            Dict with the response and metadata
        """
        options = options or {}
        
        # Detect language if not provided
        detected_lang = None
        confidence = 0.0
        if not language and text.strip():
            detected_lang, confidence = self.detect_language(text)
            logger.info(f"Detected language: {detected_lang} (confidence: {confidence:.2f})")
        
        # Use detected language if no language was explicitly provided
        response_language = language or detected_lang or 'en'
        
        # Log the language context
        logger.info(f"Processing with language: {response_language}, Detected: {detected_lang}, Confidence: {confidence:.2f}")
        
        # Format the prompt with conversation context and RAG context
        conversation_context = options.get('conversation_context', '')
        rag_context = options.get('rag_context', '')
        
        # Build the context section
        context_parts = []
        if conversation_context.strip():
            context_parts.append(f"Previous conversation:\n{conversation_context}")
        
        if rag_context.strip():
            context_parts.append(f"Relevant knowledge:\n{rag_context}")
        
        if context_parts:
            full_context = "\n\n".join(context_parts)
            prompt = f"""You are MITRA, a compassionate mental health companion for Indian youth. Use the following context to provide a direct, caring response that builds on the conversation.

{full_context}

User says: "{text}"

Respond naturally and compassionately as MITRA would, incorporating both the conversation history and relevant knowledge. Stay on topic and build on what was previously discussed.

FORMATTING RULES:
- Use proper paragraphs with double line breaks between different topics
- Use bullet points (• ) for lists and advice
- Put final questions on separate lines
- Keep sentences clear and readable
- Be warm and encouraging

Give a direct response without explaining your process or referencing the context explicitly."""
        else:
            prompt = f"""You are MITRA, a compassionate mental health companion for Indian youth.

User says: "{text}"

Respond naturally and compassionately. 

FORMATTING RULES:
- Use proper paragraphs with double line breaks between different topics
- Use bullet points (• ) for lists and advice  
- Put final questions on separate lines
- Keep sentences clear and readable
- Be warm and encouraging"""
        
        # Process the query with the detected language and RAG context
        resp = await self.analyze(prompt, response_language)

        # Try to extract text in common shapes:
        # 1. genai response object with `.text`
        text_out = getattr(resp, "text", None)

        # 2. some genai versions return a dict-like object with 'response'/'output'/'content'
        if not text_out and isinstance(resp, dict):
            text_out = resp.get("response") or resp.get("output") or resp.get("content")

        # 3. fallback: stringify the resp
        if not text_out:
            try:
                # If response has choices or predictions, attempt to find a text field
                if hasattr(resp, "responses"):
                    # some clients return list-like responses
                    first = resp.responses[0] if resp.responses else None
                    text_out = getattr(first, "text", None) if first else None
            except Exception:
                text_out = None

        return {"response": text_out or str(resp)}

    async def process_voice_conversation(self, text: str, options: Optional[Dict] = None, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Voice-optimized conversation processing for TTS output.
        
        Returns shorter, TTS-friendly responses without formatting symbols.
        
        Args:
            text: The input text from the user
            options: Additional options for the conversation, including RAG context
            language: Optional language code to force response in a specific language
            
        Returns:
            Dict with the response optimized for voice output
        """
        options = options or {}
        
        # Check if we have STT language information to avoid incorrect text-based detection
        stt_language = options.get('stt_language')
        force_response_language = options.get('force_response_language')
        
        # Debug: Print all options received
        logger.info(f"Voice conversation options: {options}")
        logger.info(f"STT language from options: {stt_language}")
        logger.info(f"Force response language: {force_response_language}")
        
        # Detect language if not provided, but prioritize STT language and apply confidence threshold
        detected_lang = None
        confidence = 0.0
        
        if stt_language:
            # Trust STT language detection over text-based detection for voice input
            # Normalize STT language code (e.g., "en-us" -> "en")
            detected_lang = stt_language.split('-')[0].lower()
            confidence = 0.95  # High confidence for STT
            logger.info(f"Voice mode - Using STT language: {detected_lang} (normalized from {stt_language}, STT confidence: {confidence:.2f})")
        elif not language and text.strip():
            detected_lang, confidence = self.detect_language(text)
            logger.info(f"Voice mode - Detected language: {detected_lang} (confidence: {confidence:.2f})")
            
            # For voice input, apply stricter confidence threshold and English bias for short phrases
            if confidence < 0.85 or len(text.strip().split()) <= 3:
                logger.info(f"Low confidence ({confidence:.2f}) or short phrase, defaulting to English for voice input")
                detected_lang = 'en'
                confidence = 0.9
        
        # If we have STT language, skip text-based detection entirely
        if stt_language:
            logger.info(f"Voice mode - Skipping text-based language detection, using STT: {detected_lang}")
        
        # Use forced language, then detected language, then default to English
        response_language = force_response_language or language or detected_lang or 'en'
        logger.info(f"Final response language: {response_language}")
        
        # Format the prompt for voice-optimized responses
        conversation_context = options.get('conversation_context', '')
        rag_context = options.get('rag_context', '')
        
        # Build the context section
        context_parts = []
        if conversation_context.strip():
            context_parts.append(f"Previous conversation:\n{conversation_context}")
        
        if rag_context.strip():
            context_parts.append(f"Relevant knowledge:\n{rag_context}")
        
        if context_parts:
            full_context = "\n\n".join(context_parts)
            prompt = f"""You are MITRA, a compassionate mental health companion for Indian youth. Use the following context to provide a brief, caring voice response.

{full_context}

User says: "{text}"

Respond as MITRA would in a natural voice conversation. Keep it conversational and supportive.

VOICE RESPONSE RULES:
- Keep response under 15 seconds when spoken (about 30-40 words maximum)
- Use simple, conversational language that sounds natural when spoken
- NO asterisks, bullet points, or formatting symbols
- NO bullet points or lists - speak naturally instead
- End with a gentle question or supportive statement
- Be warm but concise
- Avoid complex sentences or multiple topics

Give a brief, direct voice response that sounds natural when spoken aloud."""
        else:
            prompt = f"""You are MITRA, a compassionate mental health companion for Indian youth.

User says: "{text}"

Respond naturally in a brief voice conversation. 

VOICE RESPONSE RULES:
- Keep response under 15 seconds when spoken (about 30-40 words maximum)
- Use simple, conversational language that sounds natural when spoken
- NO asterisks, bullet points, or formatting symbols  
- NO bullet points or lists - speak naturally instead
- End with a gentle question or supportive statement
- Be warm but concise
- Avoid complex sentences or multiple topics"""
        
        # Process the query with the detected language and RAG context
        resp = await self.analyze(prompt, response_language)

        # Extract text response
        text_out = getattr(resp, "text", None)
        
        if not text_out and isinstance(resp, dict):
            text_out = resp.get("response") or resp.get("output") or resp.get("content")
        
        if not text_out:
            try:
                if hasattr(resp, "responses"):
                    first = resp.responses[0] if resp.responses else None
                    text_out = getattr(first, "text", None) if first else None
            except Exception:
                text_out = None

        # Clean the response for TTS
        cleaned_response = self._clean_for_voice(text_out or str(resp))
        
        return {"response": cleaned_response}

    def _clean_for_voice(self, text: str) -> str:
        """
        Clean text for voice/TTS output by removing formatting symbols.
        
        Args:
            text: Raw text that may contain formatting
            
        Returns:
            Cleaned text suitable for TTS
        """
        if not text:
            return "I understand. How can I help you today?"
        
        # Remove asterisks and formatting symbols
        cleaned = text.replace('*', '')  # Remove all asterisks
        cleaned = cleaned.replace('•', '')  # Remove bullet points
        cleaned = cleaned.replace('◦', '')  # Remove sub-bullets
        cleaned = cleaned.replace('▪', '')  # Remove square bullets
        cleaned = cleaned.replace('–', '-')  # Replace em dash with regular dash
        cleaned = cleaned.replace('—', '-')  # Replace en dash with regular dash
        
        # Remove multiple spaces and clean up
        import re
        cleaned = re.sub(r'\s+', ' ', cleaned)  # Multiple spaces to single space
        cleaned = re.sub(r'\n\s*\n', '. ', cleaned)  # Multiple newlines to period
        cleaned = cleaned.replace('\n', '. ')  # Single newlines to periods
        
        # Remove extra periods
        cleaned = re.sub(r'\.{2,}', '.', cleaned)  # Multiple periods to single
        cleaned = re.sub(r'\.\s*\.', '.', cleaned)  # Period space period to single period
        
        # Clean up spaces around punctuation
        cleaned = re.sub(r'\s+([.!?])', r'\1', cleaned)  # Remove space before punctuation
        cleaned = re.sub(r'([.!?])\s+', r'\1 ', cleaned)  # Single space after punctuation
        
        # Trim and ensure it ends properly
        cleaned = cleaned.strip()
        if cleaned and not cleaned.endswith(('.', '!', '?')):
            cleaned += '.'
            
        return cleaned