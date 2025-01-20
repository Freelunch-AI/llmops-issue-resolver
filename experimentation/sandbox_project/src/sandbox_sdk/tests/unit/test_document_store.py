import pytest
import asyncio
from pathlib import Path
from sandbox_orchestrator.databases.document_store import DocumentStore, Document
import numpy as np

VECTOR_SIZE = 1536  # Standard size for embeddings

@pytest.fixture
async def document_store():
    store = DocumentStore(
        host="localhost",
        port=6333,
        collection_name="test_collection"
    )
    yield store
    await store.delete_collection()

@pytest.fixture
def sample_documents():
    return [
        Document(
            text="Python is a programming language",
            metadata={"category": "programming", "type": "language"},
            vector=np.random.rand(VECTOR_SIZE).tolist()
        ),
        Document(
            text="Docker is a containerization platform",
            metadata={"category": "devops", "type": "tool"},
            vector=np.random.rand(VECTOR_SIZE).tolist()
        ),
        Document(
            text="FastAPI is a Python web framework",
            metadata={"category": "programming", "type": "framework"},
            vector=np.random.rand(VECTOR_SIZE).tolist()
        )
    ]

@pytest.mark.asyncio
async def test_add_documents(document_store, sample_documents):
    # Add documents
    doc_ids = await document_store.add_documents(sample_documents)
    
    assert len(doc_ids) == 3
    assert all(isinstance(id, int) for id in doc_ids)

@pytest.mark.asyncio
async def test_get_similar_documents(document_store, sample_documents):
    # Add documents
    await document_store.add_documents(sample_documents)
    
    # Search by text
    similar_docs = await document_store.get_similar_documents(
        "What programming languages are good?",
        limit=2
    )
    
    assert len(similar_docs) == 2
    assert any("Python" in doc.text for doc in similar_docs)

@pytest.mark.asyncio
async def test_delete_documents(document_store, sample_documents):
    # Add documents
    doc_ids = await document_store.add_documents(sample_documents)
    
    # Delete one document
    await document_store.delete_documents([doc_ids[0]])
    
    # Search should return only remaining documents
    all_docs = await document_store.get_similar_documents("", limit=10)
    assert len(all_docs) == 2

@pytest.mark.asyncio
async def test_load_documents_from_file(document_store, tmp_path):
    # Create test data file
    data_file = tmp_path / "test_docs.json"
    data_file.write_text("""[
        {
            "text": "Test document 1",
            "metadata": {"source": "test"},
            "vector": [0.1] * VECTOR_SIZE
        },
        {
            "text": "Test document 2",
            "metadata": {"source": "test"},
            "vector": [0.2] * VECTOR_SIZE
        }
    ]""")
    
    # Load documents
    doc_ids = await document_store.load_documents(data_file)
    assert len(doc_ids) == 2
    
    # Verify documents were loaded
    docs = await document_store.get_similar_documents("test", limit=10)
    assert len(docs) == 2