from typing import Dict, List, Optional
import asyncio
from qdrant_client import QdrantClient, AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import logging
import backoff
from contextlib import asynccontextmanager
from qdrant_client.http.exceptions import UnexpectedResponse, ResponseHandlingException
from aiohttp.client_exceptions import ClientError

logger = logging.getLogger(__name__)

class VectorDatabase:
    def __init__(self, host: str, port: int):
        self.client = None
        self.async_client = None
        self.host = host
        self.port = port
        self._connection_lock = asyncio.Lock()
        self._init_connection()

    def _init_connection(self) -> None:
        try:
            logger.info(f"Initializing vector database clients at {self.host}:{self.port}")
            self.client = QdrantClient(host=self.host, port=self.port)
            self.async_client = AsyncQdrantClient(host=self.host, port=self.port)
            logger.info(f"Initialized vector database clients at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to initialize vector database clients at {self.host}:{self.port}: {e}")
            if self.client:
                try:
                    self.client.close()
                except Exception as close_error:
                    logger.error(f"Error while closing failed connection: {close_error}")
            raise

    @backoff.on_exception(
        backoff.expo,
        (UnexpectedResponse, ResponseHandlingException, ClientError),
        max_tries=3
    )
    async def _ensure_connection(self) -> None:
        async with self._connection_lock:
            if self.async_client is None:
                self._init_connection()
            try:
                # Test connection with a lightweight operation
                await self.async_client.get_collections()
            except Exception as e:
                logger.error(f"Connection test failed: {e}")
                self._init_connection()
                raise

    async def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: Distance = Distance.COSINE
    ) -> None:
        """Create a new collection."""
        await self._ensure_connection()
        try:
            logger.info(f"Creating collection {collection_name}")
            await self.async_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=distance)
            )
            logger.info(f"Collection {collection_name} created successfully")
        except Exception as e:
            logger.error(f"Error creating collection {collection_name}: {e}")
            raise
    
    async def insert_points(
        self,
        collection_name: str,
        points: List[Dict],
        batch_size: int = 100
    ) -> None:
        """Insert points into collection in batches."""
        await self._ensure_connection()
        try:
            logger.info(f"Inserting {len(points)} points into {collection_name}")
            
            # Convert points to PointStruct format
            point_structs = []
            for point in points:
                point_struct = PointStruct(
                    id=point["id"],
                    vector=point["vector"],
                    payload=point["payload"]
                )
                point_structs.append(point_struct)
            
            # Insert in batches
            for i in range(0, len(point_structs), batch_size):
                batch = point_structs[i:i + batch_size]
                await self.async_client.upsert(
                    collection_name=collection_name,
                    points=batch
                )
                logger.debug(f"Inserted batch of {len(batch)} points")
            
            logger.info("Points inserted successfully")
        except Exception as e:
            logger.error(f"Error inserting points into {collection_name}: {e}")
            raise
    
    async def search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 10,
        filter: Optional[Dict] = None
    ) -> List[Dict]:
        """Search for similar vectors."""
        await self._ensure_connection()
        try:
            logger.info(f"Searching in collection {collection_name}")
            results = await self.async_client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                query_filter=filter
            )
            logger.info(f"Found {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Error searching in {collection_name}: {e}")
            raise
    
    async def delete_collection(self, collection_name: str) -> None:
        """Delete a collection."""
        await self._ensure_connection()
        try:
            logger.info(f"Deleting collection {collection_name}")
            await self.async_client.delete_collection(collection_name)
            logger.info(f"Collection {collection_name} deleted successfully")
        except Exception as e:
            logger.error(f"Error deleting collection {collection_name}: {e}")
            raise
    
    def close(self) -> None:
        """Close database connection."""
        try:
            logger.info("Closing vector database connections")
            if self.client:
                self.client.close()
            if self.async_client:
                self.async_client.close()
        except Exception as e:
            logger.error(f"Error closing vector database connection: {e}")
            raise

    async def aclose(self) -> None:
        """Async close database connection."""
        try:
            logger.info("Closing vector database connections")
            if self.client:
                self.client.close()
            if self.async_client:
                await self.async_client.close()
        except Exception as e:
            logger.error(f"Error closing vector database connection: {e}")
            raise

    async def __aenter__(self) -> 'VectorDatabase':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.aclose()