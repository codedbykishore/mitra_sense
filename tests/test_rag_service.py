"""Tests for the RAG service implementation."""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from app.services.rag_service import RAGService
import json

# Sample test data
SAMPLE_QUERY = "How to manage exam stress"
SAMPLE_LANGUAGE = "en"
SAMPLE_REGION = "north_india"
SAMPLE_TAGS = ["cultural", "coping"]
SAMPLE_MAX_RESULTS = 3
SAMPLE_MIN_SCORE = 0.6

# Mock response structure
from unittest.mock import Mock

class MockDocument:
    def __init__(self, metadata=None):
        self.metadata = metadata or {}
        self.name = "test_document"
        self.display_name = "Test Document"
        self.mime_type = "text/plain"

class MockRetrievalResult:
    def __init__(self, text, score=0.9, metadata=None):
        self.text = text
        self.document = MockDocument(metadata or {})
        self.relevance_score = score
        self.chunk_index = 0
        self.page_number = 1
        self.page_count = 1
        
        # Create a mock source
        self.source = Mock()
        self.source.file = self.document
        self.source.uri = "gs://test-bucket/test-doc.txt"
        self.source.mime_type = "text/plain"

# Create mock response
mock_chunks = [
    MockRetrievalResult(
        text="Test document content 1",
        score=0.95,
        metadata={"title": "Test Doc 1", "source": "test_source", "language": "en", "region": "north_india", "tags": ["cultural"], "sensitivity": "low"}
    ),
    MockRetrievalResult(
        text="Test document content 2",
        score=0.85,
        metadata={"title": "Test Doc 2", "source": "test_source", "language": "en", "region": "south_india", "tags": ["coping"], "sensitivity": "medium"}
    )
]

# Create a mock response object with contexts (not chunks)
MOCK_RESPONSE = Mock()
MOCK_RESPONSE.contexts = mock_chunks

@pytest.fixture
def rag_service():
    """Fixture providing a RAGService instance with mocked dependencies."""
    with patch('vertexai.init'):
        service = RAGService()
        # Mock the corpus name to avoid real API calls
        service.corpus_name = "projects/test-project/locations/test-region/ragCorpora/test-corpus"
        return service

@pytest.mark.asyncio
async def test_retrieve_with_metadata_basic(rag_service):
    """Test basic retrieval with minimal parameters."""
    with patch('vertexai.preview.rag.retrieval_query') as mock_retrieval:
        # Setup mock
        mock_retrieval.return_value = MOCK_RESPONSE
        
        # Call the method
        results = await rag_service.retrieve_with_metadata(
            query=SAMPLE_QUERY,
            language=SAMPLE_LANGUAGE,
            max_results=SAMPLE_MAX_RESULTS,
            min_score=SAMPLE_MIN_SCORE
        )
        
        # Assertions
        assert len(results) == 2
        assert results[0]["text"] == MOCK_RESPONSE.contexts[0].text
        assert results[0]["language"] == SAMPLE_LANGUAGE
        assert "relevance_score" in results[0]
        
        # Verify the retrieval was called with the right parameters
        mock_retrieval.assert_called_once()
        args, kwargs = mock_retrieval.call_args
        
        # Check rag_resources
        assert len(kwargs["rag_resources"]) == 1
        assert kwargs["rag_resources"][0].rag_corpus == rag_service.corpus_name
        
        # Check query text
        assert kwargs["text"] == SAMPLE_QUERY
        
        # Check retrieval config
        config = kwargs["rag_retrieval_config"]
        assert config.top_k == SAMPLE_MAX_RESULTS
        assert config.filter.vector_distance_threshold == pytest.approx(1.0 - SAMPLE_MIN_SCORE)

@pytest.mark.asyncio
async def test_retrieve_with_metadata_region_filter(rag_service):
    """Test retrieval with region filter."""
    with patch('vertexai.preview.rag.retrieval_query') as mock_retrieval:
        # Setup mock
        mock_retrieval.return_value = MOCK_RESPONSE
        
        # Call with region filter
        await rag_service.retrieve_with_metadata(
            query=SAMPLE_QUERY,
            language=SAMPLE_LANGUAGE,
            region=SAMPLE_REGION,
            max_results=SAMPLE_MAX_RESULTS
        )
        
        # Verify the retrieval was called with region filter
        args, kwargs = mock_retrieval.call_args
        config = kwargs["rag_retrieval_config"]
        assert config.filter.metadata_filter is not None
        assert f'region=\"{SAMPLE_REGION}\"' in config.filter.metadata_filter
        assert f'language=\"{SAMPLE_LANGUAGE}\"' in config.filter.metadata_filter

@pytest.mark.asyncio
async def test_retrieve_with_metadata_tags_filter(rag_service):
    """Test retrieval with tags filter."""
    with patch('vertexai.preview.rag.retrieval_query') as mock_retrieval:
        # Setup mock
        mock_retrieval.return_value = MOCK_RESPONSE
        
        # Call with tags filter
        await rag_service.retrieve_with_metadata(
            query=SAMPLE_QUERY,
            language=SAMPLE_LANGUAGE,
            tags=SAMPLE_TAGS,
            max_results=SAMPLE_MAX_RESULTS
        )
        
        # Verify the retrieval was called with tags filter
        args, kwargs = mock_retrieval.call_args
        config = kwargs["rag_retrieval_config"]
        assert config.filter.metadata_filter is not None
        assert 'tags:any(' in config.filter.metadata_filter
        assert all(f'"{tag}"' in config.filter.metadata_filter for tag in SAMPLE_TAGS)

@pytest.mark.asyncio
async def test_retrieve_with_metadata_empty_results(rag_service):
    """Test retrieval when no results are found."""
    with patch('vertexai.preview.rag.retrieval_query') as mock_retrieval:
        # Setup mock to return empty results
        mock_response = Mock()
        mock_response.contexts = []
        mock_retrieval.return_value = mock_response
        
        # Call the method
        results = await rag_service.retrieve_with_metadata(
            query="nonexistent query",
            language=SAMPLE_LANGUAGE
        )
        
        # Assertions
        assert results == []

@pytest.mark.asyncio
async def test_retrieve_with_metadata_error_handling(rag_service):
    """Test error handling during retrieval."""
    with patch('vertexai.preview.rag.retrieval_query') as mock_retrieval:
        # Setup mock to raise an exception
        mock_retrieval.side_effect = Exception("API Error")
        
        # Call the method and expect an exception
        with pytest.raises(Exception, match="API Error"):
            await rag_service.retrieve_with_metadata(
                query=SAMPLE_QUERY,
                language=SAMPLE_LANGUAGE
            )

@pytest.mark.asyncio
async def test_retrieve_with_metadata_result_formatting(rag_service):
    """Test the formatting of the result dictionary."""
    with patch('vertexai.preview.rag.retrieval_query') as mock_retrieval:
        # Setup mock
        mock_retrieval.return_value = MOCK_RESPONSE
        
        # Call the method
        results = await rag_service.retrieve_with_metadata(
            query=SAMPLE_QUERY,
            language=SAMPLE_LANGUAGE
        )
        
        # Verify the result format
        assert isinstance(results, list)
        assert len(results) > 0
        result = results[0]
        
        # Check all expected fields are present
        expected_fields = [
            "text", "title", "source", "language", 
            "region", "tags", "sensitivity", "relevance_score"
        ]
        for field in expected_fields:
            assert field in result
        
        # Check types
        assert isinstance(result["text"], str)
        assert isinstance(result["title"], str)
        assert isinstance(result["tags"], list)
        assert isinstance(result["relevance_score"], float)
