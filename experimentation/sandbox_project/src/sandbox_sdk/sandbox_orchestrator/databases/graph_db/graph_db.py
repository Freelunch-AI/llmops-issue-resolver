from typing import Dict, List, Optional
import asyncio
from neo4j import GraphDatabase
import logging

logger = logging.getLogger(__name__)

from neo4j import GraphDatabase as Neo4jDriver

class GraphDatabase:
    def __init__(self, uri: str, user: str, password: str):
        """Initialize a new Neo4j driver instance."""
        self.driver = Neo4jDriver.driver(uri, auth=(user, password))
        logger.info(f"Connected to graph database at {uri}")
    
    async def execute_query(
        self,
        query: str,
        parameters: Optional[Dict] = None
    ) -> List[Dict]:
        """Execute Cypher query."""
        try:
            logger.info("Executing query")
            logger.debug(f"Query: {query}")
            
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                records = [record.data() for record in result]
            
            logger.info(f"Query executed successfully, returned {len(records)} records")
            return records
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise
    
    async def create_node(
        self,
        label: str,
        properties: Dict
    ) -> Dict:
        """Create a new node."""
        try:
            logger.info(f"Creating node with label {label}")
            
            query = f"CREATE (n:{label} $props) RETURN n"
            with self.driver.session() as session:
                result = session.run(query, {"props": properties})
                node = result.single()["n"]
            
            logger.info(f"Node created successfully with ID {node.id}")
            return node
        except Exception as e:
            logger.error(f"Error creating node: {e}")
            raise
    
    async def create_relationship(
        self,
        from_node_id: int,
        to_node_id: int,
        relationship_type: str,
        properties: Optional[Dict] = None
    ) -> Dict:
        """Create relationship between nodes."""
        try:
            logger.info(f"Creating {relationship_type} relationship")
            
            query = """
            MATCH (a), (b)
            WHERE ID(a) = $from_id AND ID(b) = $to_id
            CREATE (a)-[r:$rel_type $props]->(b)
            RETURN r
            """
            
            with self.driver.session() as session:
                result = session.run(
                    query,
                    {
                        "from_id": from_node_id,
                        "to_id": to_node_id,
                        "rel_type": relationship_type,
                        "props": properties or {}
                    }
                )
                relationship = result.single()["r"]
            
            logger.info("Relationship created successfully")
            return relationship
        except Exception as e:
            logger.error(f"Error creating relationship: {e}")
            raise
    
    async def delete_all(self) -> None:
        """Delete all nodes and relationships."""
        try:
            logger.info("Deleting all nodes and relationships")
            
            with self.driver.session() as session:
                session.run("MATCH (n) DETACH DELETE n")
            
            logger.info("Database cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing database: {e}")
            raise
    
    def close(self) -> None:
        """Close database connection."""
        try:
            if self.driver:
                logger.info("Closing graph database connection")
                self.driver.close()
        except Exception as e:
            logger.error(f"Error closing graph database connection: {e}")
            raise