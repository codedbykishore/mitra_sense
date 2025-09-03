# app/services/gemini_ai.py
import asyncio
import os
import json
from typing import Optional, Any, Dict, List
import vertexai # Use vertexai for initialization
from vertexai import rag # Import rag for RAG functionality
from vertexai.generative_models import GenerativeModel, Tool # For RAG-enabled model
from app.config import settings
import logging

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

    async def process_cultural_conversation(self, text: str, options: Optional[Dict] = None, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Backwards-compatible wrapper expected by google_speech.process_voice_pipeline.
        Returns a dict of the form: {"response": "<generated text>"}.
        """
        resp = await self.analyze(text, language)
        logger.info(f"RAG Context: {options}, Language: {language}")

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