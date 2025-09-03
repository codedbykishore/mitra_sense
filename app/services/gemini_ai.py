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
        
        # Create the RAG resource with filters
        rag_resource = rag.RagResource(
            rag_corpus=self.rag_corpus_name,
            rag_filters=rag_filters or None
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
        
        # Format the prompt with RAG context if available
        rag_context = options.get('rag_context', '')
        if rag_context:
            prompt = f"""Context from knowledge base:
{rag_context}

User's question: {text}

Please provide a helpful response based on the context above. If the context doesn't contain relevant information, use your general knowledge."""
        else:
            prompt = text
        
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