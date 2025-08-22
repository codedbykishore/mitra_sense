import os
import json
import pytest
from app.services.gemini_ai import GeminiService

@pytest.mark.asyncio
async def test_gemini_service_response():
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    assert cred_path, "Missing GOOGLE_APPLICATION_CREDENTIALS"
    assert os.path.isfile(cred_path), f"Credentials file not found: {cred_path}"

    with open(cred_path, "r") as f:
        creds = json.load(f)
    project_id = creds.get("project_id")
    assert project_id, "No project_id found in credentials!"

    service = GeminiService(project_id=project_id)

    response = await service.analyze("Hello Gemini, are you working?")
    print(response.text)
    assert response.text and len(response.text) > 0
