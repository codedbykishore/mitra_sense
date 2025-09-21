from typing import List, Optional, Dict, Any
from vertexai.preview import rag
from app.config import settings
import vertexai


class RAGService:
    def __init__(self):
        """Initialize RAG service with project configuration."""
        vertexai.init(project=settings.GOOGLE_PROJECT_ID, location="europe-west3")
        self.corpus_name = settings.CORPUS_NAME

    async def retrieve_with_metadata(
        self,
        query: str,
        language: str = "en",
        region: Optional[str] = None,
        tags: Optional[List[str]] = None,
        max_results: int = 5,
        min_score: float = 0.6,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents with metadata filtering.

        Args:
            query: User's query
            language: Language code (e.g., 'en', 'hi')
            region: Region filter (e.g., 'north_india', 'south_india')
            tags: List of tags to filter by
            max_results: Maximum number of results to return
            min_score: Minimum relevance score (0-1)

        Returns:
            List of relevant documents with metadata
        """
        # Normalize language to base code (e.g., "en" from "en-US") and build metadata filters
        try:
            base_lang = (language or "en").split('-')[0].lower().strip()
        except Exception:
            base_lang = (language or "en").lower().strip()

        metadata_filters = [f'language="{base_lang}"']

        if region:
            metadata_filters.append(f'region="{region}"')

        if tags:
            tags_filter = ",".join([f'"{tag}"' for tag in tags])
            metadata_filters.append(f"tags:any({tags_filter})")

        # Combine filters with AND condition
        filter_str = " AND ".join(metadata_filters) if metadata_filters else None
        
        # Debug logging
        print(f"\n[DEBUG] Applying filters: {filter_str}")
        print(f"[DEBUG] Requested region: {region}")

        # Perform the retrieval
        rag_resource = rag.RagResource(rag_corpus=self.corpus_name)
        rag_retrieval_config = rag.RagRetrievalConfig(
            top_k=max_results,
            filter=rag.Filter(
                metadata_filter=filter_str,
                vector_distance_threshold=1.0
                - min_score,  # Convert similarity to distance
            ),
        )

        # Call the retrieval API (synchronous call)
        response = rag.retrieval_query(
            rag_resources=[rag_resource],
            text=query,
            rag_retrieval_config=rag_retrieval_config,
        )
        
        # Access the contexts correctly - response.contexts.contexts contains the list
        contexts_obj = response.contexts if hasattr(response, 'contexts') else None
        results = contexts_obj.contexts if contexts_obj and hasattr(contexts_obj, 'contexts') else []

        # Debug log raw results
        print(f"[DEBUG] Raw results count: {len(results)}")
        for i, result in enumerate(results):
            print(f"[DEBUG] Result {i} text preview: {result.text[:100]}...")
            if hasattr(result, 'source_uri'):
                print(f"[DEBUG] Result {i} source: {result.source_uri}")

        # Format results with metadata
        formatted_results = []
        for result in results:
            # Extract metadata from the text content if available
            # The text might contain structured metadata
            text_content = result.text if hasattr(result, 'text') else ""
            
            # Parse metadata from text content (assuming it's in the format shown in error)
            metadata = {}
            if "title " in text_content:
                lines = text_content.split('\n')
                for line in lines:
                    if line.startswith('title '):
                        metadata['title'] = line.replace('title ', '').strip()
                    elif line.startswith('language '):
                        metadata['language'] = line.replace('language ', '').strip()
                    elif line.startswith('region '):
                        metadata['region'] = line.replace('region ', '').strip()
                    elif line.startswith('keywords '):
                        if 'tags' not in metadata:
                            metadata['tags'] = []
                        metadata['tags'].append(line.replace('keywords ', '').strip())
            
            formatted_results.append(
                {
                    "text": text_content,
                    "title": metadata.get("title", ""),
                    "source": result.source_uri if hasattr(result, 'source_uri') else "",
                    "source_display_name": result.source_display_name if hasattr(result, 'source_display_name') else "",
                    "language": metadata.get("language", language),
                    "region": metadata.get("region", "pan_india"),
                    "tags": metadata.get("tags", []),
                    "relevance_score": result.score if hasattr(result, "score") else 0.0,
                }
            )

        return formatted_results
