import os
import asyncio
import logging
from app.services.gemini_ai import GeminiService
from app.services.crisis import CrisisService
from app.services.rag_service import RAGService
import pytest

@pytest.mark.asyncio
async def test_real_gemini_rag_and_crisis_escalation():
    """
    Integration test: RAG retrieval + Gemini risk scoring + crisis escalation.
    Debug print statements included for error diagnosis.
    """
    # Setup GeminiService and RAGService with real credentials
    # Assumes GOOGLE_APPLICATION_CREDENTIALS is set and rag_data/mitra_knowledge_base.jsonl exists
    gemini = GeminiService()
    rag = RAGService()
    crisis = CrisisService(gemini_service=gemini)

    # Example input: high-risk, culturally relevant
    user_id = "test_user_001"
    message = "Bohot ghabrahat ho rahi hai, mann nahi lagta, I want to give up."

    # Step 1: RAG retrieval (use correct method)
    try:
        rag_results = await rag.retrieve_with_metadata(
            query=message,
            language="hi",
            region="pan_india",
            tags=None,
            max_results=3,
            min_score=0.6,
        )
        print("RAG Results:", rag_results)
        assert rag_results, "RAG returned no results"
    except Exception as e:
        logging.error(f"RAG retrieval error: {e}")
        assert False, f"RAG retrieval failed: {e}"

    # Step 2: Gemini risk scoring
    try:
        risk_score = await gemini.analyze_risk(message)
        print("Gemini Risk Score:", risk_score)
        assert isinstance(risk_score, (int, float)), "Risk score not numeric"
    except Exception as e:
        logging.error(f"Gemini risk scoring error: {e}")
        assert False, f"Gemini risk scoring failed: {e}"

    # Step 3: Crisis escalation logic
    try:
        report = await crisis.assess_risk(user_id, message)
        print("Crisis Report:", report)
        assert "risk_score" in report and "risk_level" in report, "Report missing keys"
        result = await crisis.escalate(user_id, report)
        print("Escalation Result:", result)
        assert "action" in result or "status" in result, "Escalation result missing keys"
    except Exception as e:
        logging.error(f"Crisis escalation error: {e}")
        assert False, f"Crisis escalation failed: {e}"

