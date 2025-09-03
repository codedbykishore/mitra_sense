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
    def __init__(self, project_id: Optional[str] = None, location: str = "us-central1", model_name: str = "gemini-2.0-flash", rag_corpus_name: Optional[str] = None):
        """
        GeminiService for Vertex AI (GenerativeModel).
        If project_id is not provided, try to auto-detect from settings or
        the GOOGLE_APPLICATION_CREDENTIALS JSON.
        """
        # first prefer explicit argument, then settings (loaded from credentials JSON), then env
        project_id =  getattr(settings, "GOOGLE_PROJECT_ID", None)


        # # If still not found, try to read the service account JSON pointed by GOOGLE_APPLICATION_CREDENTIALS
        # if not project_id:
        #     cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or getattr(settings, "GOOGLE_CREDENTIALS_FILE", None)
        #     if cred_path and os.path.isfile(cred_path):
        #         try:
        #             with open(cred_path, "r") as f:
        #                 creds = json.load(f)
        #             project_id = creds.get("project_id")
        #         except Exception as e:
        #             logger.warning("Failed to read project_id from credentials file: %s", e)

        if not project_id:
            raise ValueError("project_id not provided and could not be auto-detected from settings/credentials/env")

        self.project_id = project_id
        self.location = location
        self.model_name = model_name
        self.rag_corpus_name = getattr(settings, "CORPUS_NAME", None) # Store RAG corpus name

        # Initialize Vertex AI
        try:
            vertexai.init(project=self.project_id, location=self.location)
            logger.info("Vertex AI API initialized successfully for GeminiService.")
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI API: {e}")
            raise

        # Initialize GenerativeModel with or without RAG
        if self.rag_corpus_name:
            rag_retrieval_config = rag.RagRetrievalConfig(top_k=3) # Default top_k
            rag_retrieval_tool = Tool.from_retrieval(
                retrieval=rag.Retrieval(
                    source=rag.VertexRagStore(
                        rag_resources=[rag.RagResource(rag_corpus=self.rag_corpus_name)],
                        rag_retrieval_config=rag_retrieval_config
                    ),
                )
            )
            self.model = GenerativeModel(model_name=self.model_name, tools=[rag_retrieval_tool])
            logger.info(f"GeminiService initialized with RAG corpus: {self.rag_corpus_name}")
        else:
            self.model = GenerativeModel(model_name=self.model_name)
            logger.info("GeminiService initialized without RAG.")

    async def analyze(self, text: str, language: Optional[str] = None) -> Any:
        """
        Run the model.generate_content call in a thread and return the raw response.
        """
        def sync_call():
            contents: List[Any] = [text]
            if language:
                contents.append(f"Please respond in {language}.")
            return self.model.generate_content(contents=contents) # Pass contents as a list
        
        return await asyncio.to_thread(sync_call)

    def detect_language(self, text: str) -> Tuple[str, float]:
        """
        Detect the language of the input text.
        
        Args:
            text: Input text to detect language from
            
        Returns:
            Tuple of (language_code, confidence)
        """
        try:
            # Get all possible languages with probabilities
            languages = detect_langs(text)
            if not languages:
                return 'en', 0.0
                
            # Get the most probable language
            best_match = languages[0]
            return best_match.lang, best_match.prob
            
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
            options: Additional options for the conversation
            language: Optional language code to force response in a specific language
            
        Returns:
            Dict with the response and metadata
        """
        # Detect language if not provided
        detected_lang = None
        confidence = 0.0
        if not language and text.strip():
            detected_lang, confidence = self.detect_language(text)
            logger.info(f"Detected language: {detected_lang} (confidence: {confidence:.2f})")
        
        # Use detected language if no language was explicitly provided
        response_language = language or detected_lang or 'en'
        
        # Log the language context
        logger.info(f"Processing with language: {response_language}, Detected: {detected_lang}, Confidence: {confidence:.2f}, Options: {options}")
        
        # Process the query with the detected language
        resp = await self.analyze(text, response_language)

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