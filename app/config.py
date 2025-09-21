import os
import json
from dotenv import load_dotenv
from pathlib import Path
from pydantic_settings import BaseSettings
import logging

logger = logging.getLogger(__name__)

load_dotenv()


class Settings(BaseSettings):
    # Declare fields so Pydantic knows them
    GOOGLE_CREDENTIALS_FILE: str = str(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
    GOOGLE_PROJECT_ID: str | None = str(os.getenv("GOOGLE_PROJECT_ID")) if os.getenv("GOOGLE_PROJECT_ID") else None
    GOOGLE_CLIENT_EMAIL: str | None = None

    GOOGLE_CLIENT_ID: str = str(os.getenv("GOOGLE_CLIENT_ID"))
    GOOGLE_CLIENT_SECRET: str = str(os.getenv("GOOGLE_CLIENT_SECRET"))
    REDIRECT_URI:str = str(os.getenv("REDIRECT_URI"))
    SECRET_KEY:str = str(os.getenv("SECRET_KEY"))
    CORPUS_NAME:str = str(os.getenv("CORPUS_NAME"))

    SUPPORTED_LANGUAGES: list[str] = [
        "en-US",  # English (US)
        "en-IN",  # English (IN)
        "hi-IN",  # Hindi (India)
        "ta-IN",
        "te-IN"
    ]
    DEFAULT_LANGUAGE: str = "en-IN"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_google_config()

    def _load_google_config(self):
        cred_path = Path(self.GOOGLE_CREDENTIALS_FILE)
        if cred_path.exists():
            try:
                with open(cred_path, "r") as f:
                    creds = json.load(f)
                object.__setattr__(self, "GOOGLE_PROJECT_ID", creds.get("project_id"))
                object.__setattr__(
                    self, "GOOGLE_CLIENT_EMAIL", creds.get("client_email")
                )
            except (IOError, json.JSONDecodeError) as e:
                logger.error(f"Failed to load Google credentials from {cred_path}: {e}")


settings = Settings()
