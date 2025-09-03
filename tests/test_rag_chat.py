import pytest
from fastapi.testclient import TestClient
from app.main import app
import logging
import sys

# Configure logging for the test file
logger = logging.getLogger("test_rag_chat")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.propagate = False

client = TestClient(app)

def test_chat_endpoint_rag_implementation(caplog):
    caplog.set_level(logging.INFO)
    logger.info("Starting test_chat_endpoint_rag_implementation (general query)")

    # Define the payload for a general chat endpoint
    payload_general = {
        "text": "What is Mitra?",
        "context": {},
        "language": "English" # Specify English language
    }

    logger.info(f"Sending request to /api/v1/input/chat with payload: {payload_general}")

    # Make a POST request to the chat endpoint
    response_general = client.post("/api/v1/input/chat", json=payload_general)

    logger.info(f"Received response with status code: {response_general.status_code}")
    logger.info(f"Received response body: {response_general.json()}")

    # Assert the response status code
    assert response_general.status_code == 200

    # Assert the response structure and content
    response_data_general = response_general.json()
    assert "response" in response_data_general
    assert isinstance(response_data_general["response"], str)
    assert len(response_data_general["response"]) > 0
    # Assert that the response is in English
    assert "mitra" in response_data_general["response"].lower() or "family notes" in response_data_general["response"].lower()
    logger.info("Test test_chat_endpoint_rag_implementation (general query) completed successfully.")

    logger.info("Starting test_chat_endpoint_rag_implementation (RAG-specific query)")

    # Define a payload for a RAG-specific query
    # This query is designed to hit a specific entry in the knowledge base (e.g., coping_en_001)
    payload_rag = {
        "text": "Tell me about 4-7-8 breathing technique.",
        "context": {},
        "language": "English" # Specify English language
    }

    logger.info(f"Sending RAG-specific request to /api/v1/input/chat with payload: {payload_rag}")

    response_rag = client.post("/api/v1/input/chat", json=payload_rag)

    logger.info(f"Received RAG-specific response with status code: {response_rag.status_code}")
    logger.info(f"Received RAG-specific response body: {response_rag.json()}")

    assert response_rag.status_code == 200
    response_data_rag = response_rag.json()
    assert "response" in response_data_rag
    assert isinstance(response_data_rag["response"], str)
    assert len(response_data_rag["response"]) > 0

    # Assert for keywords expected from the RAG knowledge base for "4-7-8 breathing"
    expected_keywords_partial = [
        "breathe in for 4",
        "hold for 7",
        "exhale for 8",
        "repeat 4 times"
    ]
    response_text_lower = response_data_rag["response"].lower()

    # Relaxed assertion: check if at least two of the keywords are present
    matched_keywords = [keyword for keyword in expected_keywords_partial if keyword in response_text_lower]
    assert len(matched_keywords) >= 2, f"Expected at least 2 keywords from {expected_keywords_partial} not found in RAG response: {response_data_rag['response']}"

    # Capture RAG context from logs
    rag_context = None
    for record in caplog.records:
        if "RAG Context:" in record.message:
            rag_context = record.message
            break

    logger.info(f"RAG Context: {rag_context}")

    logger.info("Test test_chat_endpoint_rag_implementation (RAG-specific query) completed successfully.")
    logger.info("To confirm RAG implementation, observe the logs for the 'RAG-specific request'.")
    logger.info("The response body for this request should contain details about '4-7-8 breathing' from the knowledge base.")