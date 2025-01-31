from typing import Dict, List, Optional, Union
import time
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from neo4j import GraphDatabase
class VectorDBClient:
    def __init__(self, host: str, port: int, ssl_enabled: bool = False,
                 ssl_cert_path: Optional[str] = None,
                 ssl_key_path: Optional[str] = None):
        self.client = None
        self.host = host
        self.port = port
        self.ssl_enabled = ssl_enabled
        self.ssl_cert_path = ssl_cert_path
        self.ssl_key_path = ssl_key_path
        self.max_retries = 3
        self.retry_delay = 1
        self._connect()
    
    def _connect(self):
        """Establish connection with retry mechanism"""
        retries = 0
        while retries < self.max_retries:
            try:
                if self.ssl_enabled and self.ssl_cert_path and self.ssl_key_path:
                    self.client = QdrantClient(host=self.host, port=self.port,
                                             ssl=True, ca_cert=self.ssl_cert_path,
                                             client_cert=self.ssl_key_path)
                else:
                    self.client = QdrantClient(host=self.host, port=self.port)
                return
            except Exception as e:
                retries += 1
                if retries == self.max_retries:
                    raise Exception(f"Failed to connect after {self.max_retries} attempts: {e}")
                time.sleep(self.retry_delay)
    
    def _ensure_connection(self):
        """Ensure connection is active or reconnect"""
        if not self.client:
            self._connect()
    
    def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: Distance = Distance.COSINE
    ):
        """Create a new collection"""
        try:
            self._ensure_connection()
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=distance)
            )
        except Exception as e:
            # Attempt to clean up if collection was partially created
            try:
                self.client.delete_collection(collection_name)
            except:
                pass
            raise Exception(f"Failed to create collection: {e}")
    
    def insert_points(
        self,
        collection_name: str,
        points: List[PointStruct]
    ):
        """Insert points into collection"""
        try:
            self._ensure_connection()
            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
        except Exception as e:
            raise Exception(f"Failed to insert points: {e}")
    
    def search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 10,
        filter: Optional[Dict] = None
    ):
        """Search for similar vectors"""
        try:
            self._ensure_connection()
            return self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                query_filter=filter
            )
        except Exception as e:
            raise Exception(f"Failed to search vectors: {e}")
class GraphDBClient:
    def __init__(self, uri: str, user: str, password: str,
                 ssl_enabled: bool = False,
                 ssl_cert_path: Optional[str] = None,
                 ssl_key_path: Optional[str] = None):
        self.uri = uri
        self.user = user
        self.password = password
        self.ssl_enabled = ssl_enabled
        self.ssl_cert_path = ssl_cert_path
        self.ssl_key_path = ssl_key_path
        self.max_retries = 3
        self.retry_delay = 1
        self._connect()
    
    def _connect(self):
        """Establish connection with retry mechanism"""
        retries = 0
        while retries < self.max_retries:
            try:
                if self.ssl_enabled and self.ssl_cert_path and self.ssl_key_path:
                    self.driver = GraphDatabase.driver(
                        self.uri,
                        auth=(self.user, self.password),
                        encrypted=True,
                        trust=self.ssl_cert_path,
                        certificate_file=self.ssl_key_path)
                else:
                    self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
                return
            except Exception as e:
                retries += 1
                if retries == self.max_retries:
                    raise Exception(f"Failed to connect after {self.max_retries} attempts: {e}")
    
    def execute_query(
        self,
        query: str,
        parameters: Optional[Dict] = None
    ) -> List[Dict]:
        """Execute Cypher query"""
        retries = 0
        while retries < self.max_retries:
            try:
                with self.driver.session() as session:
                    try:
                        result = session.run(query, parameters or {})
                        return [record.data() for record in result]
                    except Exception as e:
                        raise Exception(f"Query execution failed: {e}")
            except Exception as e:
                retries += 1
                if retries == self.max_retries:
                    raise Exception(f"Failed after {self.max_retries} attempts: {e}")
                time.sleep(self.retry_delay)
    
    def create_node(
        self,
        label: str,
        properties: Dict
    ):
        """Create a new node"""
        query = f"CREATE (n:{label} $props) RETURN n"
        return self.execute_query(query, {"props": properties})
    
    def create_relationship(
        self,
        from_node_id: int,
        to_node_id: int,
        relationship_type: str,
        properties: Optional[Dict] = None
    ):
        """Create relationship between nodes"""
        query = """
        MATCH (a), (b)
        WHERE ID(a) = $from_id AND ID(b) = $to_id
        CREATE (a)-[r:$rel_type $props]->(b)
        RETURN r
        """
        return self.execute_query(query, {
            "from_id": from_node_id,
            "to_id": to_node_id,
            "rel_type": relationship_type,
            "props": properties or {}
        })
    
    def close(self):
        """Close database connection"""
        try:
            if self.driver:
                self.driver.close()
        except Exception as e:
            raise Exception(f"Failed to close database connection: {e}")
        finally:
            self.driver = None