from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.services.rag_service import RAGService
from app.models.schemas import RAGQuery, RAGResponse
from fastapi import status

router = APIRouter()
rag_service = RAGService()

@router.post("/query", response_model=List[RAGResponse])
async def query_rag(
    query: str,
    language: str = "en",
    region: Optional[str] = None,
    tags: Optional[List[str]] = None,
    max_results: int = 5,
    min_score: float = 0.6
):
    """
    Query the RAG system with metadata filtering.
    
    - **query**: The search query
    - **language**: Filter by language (e.g., 'en', 'hi')
    - **region**: Filter by region (e.g., 'north_india', 'south_india')
    - **tags**: List of tags to filter by
    - **max_results**: Maximum number of results to return (default: 5)
    - **min_score**: Minimum relevance score (0-1, default: 0.6)
    """
    try:
        results = await rag_service.retrieve_with_metadata(
            query=query,
            language=language,
            region=region,
            tags=tags,
            max_results=max_results,
            min_score=min_score
        )
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error querying RAG system: {str(e)}"
        )
