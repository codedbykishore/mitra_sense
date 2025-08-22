import os
import json
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GOOGLE_PROJECT_ID: str | None = None
    GOOGLE_CLIENT_EMAIL: str | None = None

    SUPPORTED_LANGUAGES: list[str] = [
        "en-US",  # English (US)
        "en-GB",  # English (UK)
        "es-ES",  # Spanish (Spain)
        "fr-FR",  # French
        "hi-IN",  # Hindi (India)
    ]
    DEFAULT_LANGUAGE: str = "en-US"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_google_config()

    def _load_google_config(self):
        creds_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
        if creds_json:
            creds = json.loads(creds_json)
            object.__setattr__(self, "GOOGLE_PROJECT_ID", creds.get("project_id"))
            object.__setattr__(self, "GOOGLE_CLIENT_EMAIL", creds.get("client_email"))


settings = Settings()
