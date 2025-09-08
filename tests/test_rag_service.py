import os
import logging
import asyncio
from app.services.rag_service import RAGService
import pytest
from app.services.rag_service import RAGService

@pytest.mark.asyncio
async def test_real_rag_integration():
	"""
	Real RAG integration test: retrieves documents using live RAGService and prints results.
	"""
	rag = RAGService()
	query = "How to manage exam stress?"
	language = "en"
	region = "north_india"
	tags = ["coping", "cultural"]
	try:
		results = await rag.retrieve_with_metadata(
			query=query,
			language=language,
			region=region,
			tags=tags,
			max_results=3,
			min_score=0.6,
		)
		print("RAG Results:", results)
		assert isinstance(results, list)
		assert len(results) > 0, "No RAG results returned for live query."
		for result in results:
			assert "text" in result
			assert "language" in result
			assert "region" in result
			assert "tags" in result
	except Exception as e:
		logging.error(f"RAG integration error: {e}")
		assert False, f"RAG integration failed: {e}"


