"""Integration tests for RAG service with actual Vertex AI API calls."""
import os
import pytest
from app.services.rag_service import RAGService
from dotenv import load_dotenv
from app.config import settings

# Load environment variables
load_dotenv()

@pytest.fixture(scope="module")
def rag_service():
    """Fixture providing a RAGService instance configured for integration testing."""
    service = RAGService()
    # Use the corpus name from settings
    service.corpus_name = settings.CORPUS_NAME
    return service

@pytest.mark.integration
@pytest.mark.asyncio
async def test_retrieve_with_metadata_real_api(rag_service):
    """Test retrieval with actual Vertex AI API calls."""
    # Skip test if we're missing required environment variables
    if not settings.CORPUS_NAME:
        pytest.skip("CORPUS_NAME not set in settings")
    
    # Perform retrieval with actual API call
    results = await rag_service.retrieve_with_metadata(
        query="How to manage stress during exams",
        language="en",
        max_results=3,
        min_score=0.5
    )
    
    # Basic assertions about the response structure
    assert isinstance(results, list)
    if results:  # Results might be empty if no matches
        result = results[0]
        assert "text" in result
        assert "title" in result
        assert "source" in result
        assert "relevance_score" in result
        assert isinstance(result["relevance_score"], float)

@pytest.mark.integration
@pytest.mark.asyncio
async def test_retrieve_with_filters_real_api(rag_service):
    """Test retrieval with metadata filters using actual Vertex AI API."""
    if not settings.CORPUS_NAME:
        pytest.skip("CORPUS_NAME not set in settings")
    
    # Perform retrieval with region filter for north_india
    results = await rag_service.retrieve_with_metadata(
        query="How to tell parents you're overwhelmed",
        language="en",
        region="north_india",
        max_results=2
    )
    
    # Basic assertions
    assert isinstance(results, list)
    if results:
        assert "region" in results[0]
        # The region should be north_india or pan_india (since pan_india is a fallback)
        assert results[0]["region"] in ["north_india", "pan_india"]

# Add more integration tests as needed
