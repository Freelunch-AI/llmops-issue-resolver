from typing import Dict, List, Optional, Union, Any, Callable
import asyncio
import time
from functools import wraps
from pathlib import Path
import json
import logging
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import numpy as np

logger = logging.getLogger(__name__)

class Document:
    """Represents a document with its metadata."""
    def __init__(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        id: Optional[int] = None,
        embedding: Optional[List[float]] = None
    ):
        self.text = text
        self.metadata = metadata or {}
        self.id = id
        self.embedding = embedding

class DocumentStore:
    """High-level interface for storing and retrieving documents."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        collection_name: str = "documents",
        embedding_model: str = "all-MiniLM-L6-v2",
        vector_size: Optional[int] = None,
        connection_pool_size: int = 10,
        connection_timeout: float = 5.0,
        batch_embedding_size: int = 32
    ):
        def retry_with_backoff(retries=3, backoff_in_seconds=1):
            def decorator(operation: Callable):
                @wraps(operation)
                async def wrapper(*args, **kwargs):
                    last_exception = None
                    for attempt in range(retries):
                        try:
                            if asyncio.iscoroutinefunction(operation):
                                return await operation(*args, **kwargs)
                            return operation(*args, **kwargs)
                        except Exception as e:
                            last_exception = e
                            if attempt == retries - 1:
                                raise
                            wait_time = backoff_in_seconds * (2 ** attempt)
                            logger.warning(f"Operation failed, retrying in {wait_time}s: {str(e)}")
                            await asyncio.sleep(wait_time)
                    raise last_exception
                return wrapper
            return decorator

        # Initialize Qdrant client with retry
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.client = QdrantClient(
                    host=host,
                    port=port,
                    timeout=connection_timeout,
                    pool_size=connection_pool_size
                )
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
        self.collection_name = collection_name
        
        # Initialize embedding model
        self.model = SentenceTransformer(embedding_model)
        self.vector_size = vector_size or self.model.get_sentence_embedding_dimension()
        
        logger.info(
            f"Initialized DocumentStore with {embedding_model} "
            f"(vector_size: {self.vector_size})"
        )
        
        # Ensure collection exists
        self._ensure_collection()
    
    async def _ensure_collection(self) -> None:
        """Create collection if it doesn't exist and validate parameters."""
        try:
            collections = self.client.get_collections()
            exists = any(c.name == self.collection_name for c in collections.collections)
            
            if exists:
                # Validate existing collection parameters
                collection_info = self.client.get_collection(self.collection_name)
                current_params = collection_info.config.params
                
                if current_params.vectors.size != self.vector_size:
                    logger.warning(
                        f"Collection {self.collection_name} has different vector size "
                        f"({current_params.vectors.size} vs {self.vector_size})"
                    )
                    # Recreate collection with correct parameters
                    self.client.delete_collection(self.collection_name)
                    exists = False
                
                if current_params.vectors.distance != Distance.COSINE:
                    logger.warning(
                        f"Collection {self.collection_name} has different distance metric "
                        f"({current_params.vectors.distance} vs {Distance.COSINE})"
                    )
                    self.client.delete_collection(self.collection_name)
                    exists = False
            
            if not exists:
                logger.info(f"Creating collection {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
            raise
    
    def _embed_text(self, text: str) -> List[float]:
        """Generate embedding for text."""
        try:
            if isinstance(text, str):
                text = [text]
            embeddings = self.model.encode(
                text,
                batch_size=self.batch_embedding_size,
                show_progress_bar=False
            )
            embedding = embeddings[0] if len(text) == 1 else embeddings
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    async def add_documents(
        self,
        documents: List[Document],
        batch_size: int = 100,
        transaction_timeout: float = 30.0
    ) -> List[int]:
        """Add documents to the store."""
        try:
            points = []
            doc_ids = []
            
            # Batch embedding generation
            texts_to_embed = []
            docs_without_embedding = []
            
            for doc in documents:
                if doc.embedding is None:
                    texts_to_embed.append(doc.text)
                    docs_without_embedding.append(doc)
            
            if texts_to_embed:
                embeddings = self._embed_text(texts_to_embed)
                for doc, embedding in zip(docs_without_embedding, embeddings):
                    doc.embedding = embedding
                
                # Create point
                point = PointStruct(
                    id=doc.id or len(points),
                    vector=doc.embedding,
                    payload={
                        "text": doc.text,
                        "metadata": doc.metadata
                    }
                )
                points.append(point)
                doc_ids.append(point.id)
            
            # Insert in batches
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                try:
                    async with asyncio.timeout(transaction_timeout):
                        self.client.upsert(
                            collection_name=self.collection_name,
                            points=batch,
                            wait=True  # Ensure atomic operation
                        )
                except Exception as e:
                    # Cleanup failed batch
                    await self.delete_documents([p.id for p in batch])
                    raise
                logger.debug(f"Inserted batch of {len(batch)} documents")
            
            logger.info(f"Added {len(documents)} documents")
            return doc_ids
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    async def get_similar_documents(
        self,
        query: Union[str, Document],
        limit: int = 10,
        score_threshold: Optional[float] = 0.7
    ) -> List[Document]:
        """Find similar documents."""
        try:
            # Get query embedding
            if isinstance(query, str):
                query_embedding = self._embed_text(query)
            else:
                query_embedding = query.embedding or self._embed_text(query.text)
            
            # Search
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold
            )
            
            # Convert to documents
            documents = []
            for result in results:
                doc = Document(
                    text=result.payload["text"],
                    metadata=result.payload["metadata"],
                    id=result.id,
                    embedding=result.vector
                )
                documents.append(doc)
            
            logger.info(f"Found {len(documents)} similar documents")
            return documents
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise
    
    async def delete_documents(self, ids: List[int]) -> None:
        """Delete documents by their IDs."""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=ids
            )
            logger.info(f"Deleted {len(ids)} documents")
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            raise
    
    async def load_documents(self, file_path: Path) -> List[int]:
        """Load documents from a JSON file."""
        try:
            with open(file_path) as f:
                data = json.load(f)
            
            documents = []
            for item in data:
                doc = Document(
                    text=item["text"],
                    metadata=item.get("metadata", {}),
                    id=item.get("id")
                )
                documents.append(doc)
            
            return await self.add_documents(documents)
            
        except Exception as e:
            logger.error(f"Error loading documents: {e}")
            raise
    
    async def close(self) -> None:
        """Close connections and cleanup resources asynchronously."""
        try:
            # Create a timeout for the close operation
            async def close_with_timeout():
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self.client.close)

            try:
                await asyncio.wait_for(close_with_timeout(), timeout=5.0)
            except asyncio.TimeoutError:
                logger.error("Timeout while closing document store connection")
                raise

        except Exception as e:
            logger.error(f"Error closing document store: {e}")
            raise
        finally:
            self.client = None