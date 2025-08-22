# app/services/gemini_ai.py
import asyncio
import os
import json
from typing import Optional, Any, Dict
from google import genai
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self, project_id: Optional[str] = None, location: str = "us-central1", model_name: str = "gemini-2.0-flash"):
        """
        GeminiService for Vertex AI (genai client).
        If project_id is not provided, try to auto-detect from settings or
        the GOOGLE_APPLICATION_CREDENTIALS JSON.
        """
        # first prefer explicit argument, then settings (loaded from credentials JSON), then env
        project_id = (
            project_id
            or getattr(settings, "GOOGLE_PROJECT_ID", None)
            or os.getenv("GOOGLE_PROJECT_ID")
            or os.getenv("GCLOUD_PROJECT")
            or os.getenv("GCP_PROJECT")
        )

        # If still not found, try to read the service account JSON pointed by GOOGLE_APPLICATION_CREDENTIALS
        if not project_id:
            cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or getattr(settings, "GOOGLE_CREDENTIALS_FILE", None)
            if cred_path and os.path.isfile(cred_path):
                try:
                    with open(cred_path, "r") as f:
                        creds = json.load(f)
                    project_id = creds.get("project_id")
                except Exception as e:
                    logger.warning("Failed to read project_id from credentials file: %s", e)

        if not project_id:
            raise ValueError("project_id not provided and could not be auto-detected from settings/credentials/env")

        self.project_id = project_id
        self.location = location
        self.model_name = model_name

        # Initialize genai client for Vertex AI usage
        # (this mirrors the working code you used previously)
        try:
            # genai.Client will use ADC (GOOGLE_APPLICATION_CREDENTIALS) for auth when vertexai=True
            self.client = genai.Client(vertexai=True, project=self.project_id, location=self.location)
        except Exception as e:
            logger.error("Failed to initialize genai Client: %s", e)
            raise

    
    async def analyze(self, text: str) -> Any:
        """
        Run the model.generate_content call in a thread and return the raw response.
        The genai response object often has a `.text` attribute, but that varies by client version.
        """
        def sync_call():
            # `contents` can be a single string or list depending on genai version; your working call used `contents=text`
            return self.client.models.generate_content(model=self.model_name, contents=text)

        return await asyncio.to_thread(sync_call)

    async def process_cultural_conversation(self, text: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Backwards-compatible wrapper expected by google_speech.process_voice_pipeline.
        Returns a dict of the form: {"response": "<generated text>"}.
        """
        resp = await self.analyze(text)

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
