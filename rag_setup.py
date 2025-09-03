import vertexai
from app.config import settings
from vertexai.preview import rag
import time

# Initialize Vertex AI
PROJECT_ID = getattr(settings, "GOOGLE_PROJECT_ID", None)
REGION = "europe-west3"
vertexai.init(project=PROJECT_ID, location=REGION)


def create_rag_corpus():
    """Create RAG corpus for MITRA knowledge base"""
    print("Creating RAG corpus...")

    rag_corpus = rag.create_corpus(
        display_name="mitra-mental-health-corpus",
        description="MITRA cultural mental health knowledge base for Indian youth",
    )

    print(f"Corpus created: {rag_corpus.name}")
    return rag_corpus


def import_knowledge_base(corpus_name, bucket_path):
    """Import knowledge base into RAG corpus"""
    print("Importing knowledge base...")

    # Start the import operation (pollable directly)
    operation = rag.import_files(
        corpus_name=corpus_name,
        paths=[bucket_path],
        chunk_size=512,
        chunk_overlap=100,
        max_embedding_requests_per_min=1000,
    )

    return operation


def wait_for_import_completion(operation):
    """Wait for import operation to complete"""
    print("Waiting for import to complete...")

    while not operation.done():
        print("Import in progress...")
        time.sleep(30)

    if operation.error:
        print(f"Import failed: {operation.error}")
        return False
    else:
        print("Import completed successfully!")
        return True


if __name__ == "__main__":
    # Step 1: Create corpus
    corpus = create_rag_corpus()

    # Step 2: Set bucket path
    bucket_path = (
        f"gs://mitra-sense-rag-bucket/rag_data/mitra_knowledge_base.jsonl"
    )

    # Step 3: Import data
    print("Importing knowledge base...")
    rag.import_files(
        corpus_name=corpus.name,
        paths=[bucket_path],
        chunk_size=512,
        chunk_overlap=100,
        max_embedding_requests_per_min=1000,
    )

    # Step 4: Wait a few minutes for import to complete
    print("Waiting for import to complete (approx. 5-10 minutes)...")
    import time

    time.sleep(600)  # 10 minutes; adjust based on KB size

    # Step 5: Verify files in corpus
    files = rag.list_files(corpus.name)
    print("Imported files:", files)

    print(f"\n✅ RAG Setup Complete!")
    print(f"Corpus Name: {corpus.name}")
    print("You can now use this corpus in your application.")
