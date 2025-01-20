import pytest
import numpy as np
import asyncio
import concurrent.futures
from unittest.mock import patch
from sandbox.tools.database_tools import VectorDBClient, GraphDBClient
from qdrant_client.models import PointStruct, Distance

@pytest.fixture
def vector_db_client(vector_db, db_config):
    """Create a vector database client for testing."""
    pytest.asyncio.fixture
    client = VectorDBClient(host="localhost", port=6333)
    yield client

@pytest.fixture
def graph_db_client(graph_db, db_config):
    """Create a graph database client for testing."""
    pytest.asyncio.fixture
    client = GraphDBClient(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="testpassword"
    )
    yield client
    client.close()

def test_vector_db_operations(vector_db_client):
    """Test vector database basic operations."""
    # Test collection creation
    collection_name = "test_collection"
    vector_size = 4
    vector_db_client.create_collection(
        collection_name=collection_name,
        vector_size=vector_size,
        distance=Distance.COSINE
    )
    
    # Test point insertion
    test_points = [
        PointStruct(
            id=1,
            vector=[0.1, 0.2, 0.3, 0.4],
            payload={"metadata": "test1"}
        ),
        PointStruct(
            id=2,
            vector=[0.2, 0.3, 0.4, 0.5],
            payload={"metadata": "test2"}
        )
    ]
    vector_db_client.insert_points(collection_name, test_points)
    
    # Test vector search
    query_vector = [0.1, 0.2, 0.3, 0.4]
    search_results = vector_db_client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=2
    )
    
    assert len(search_results) == 2
    assert search_results[0].payload["metadata"] in ["test1", "test2"]

def test_graph_db_operations(graph_db_client):
    """Test graph database basic operations."""
    # Test node creation
    person_props = {"name": "John Doe", "age": 30}
    result = graph_db_client.create_node("Person", person_props)
    assert len(result) == 1
    assert result[0]["n"]["name"] == "John Doe"
    
    # Create another node for relationship testing
    company_props = {"name": "ACME Corp"}
    company_result = graph_db_client.create_node("Company", company_props)
    assert len(company_result) == 1
    
    # Test relationship creation
    relationship_props = {"since": "2023"}
    relationship = graph_db_client.create_relationship(
        from_node_id=0,  # First node ID
        to_node_id=1,    # Second node ID
        relationship_type="WORKS_AT",
        properties=relationship_props
    )
    assert len(relationship) == 1
    
    # Test query execution
    query = """
    MATCH (p:Person)-[r:WORKS_AT]->(c:Company)
    RETURN p.name as person_name, c.name as company_name, r.since as start_date
    """
    result = graph_db_client.execute_query(query)
    assert len(result) == 1
    assert result[0]["person_name"] == "John Doe"
    assert result[0]["company_name"] == "ACME Corp"
    assert result[0]["start_date"] == "2023"

def test_vector_db_error_handling(vector_db_client):
    """Test vector database error handling."""
    with pytest.raises(Exception):
        # Try to search in non-existent collection
        vector_db_client.search(
            collection_name="nonexistent_collection",
            query_vector=[0.1, 0.2, 0.3, 0.4]
        )

def test_graph_db_error_handling(graph_db_client):
    """Test graph database error handling."""
    with pytest.raises(Exception):
        # Try to create relationship between non-existent nodes
        graph_db_client.create_relationship(
            from_node_id=999,
            to_node_id=998,
            relationship_type="INVALID_REL"
        )

@pytest.mark.asyncio
async def test_concurrent_vector_db_operations(vector_db_client):
    """Test concurrent vector database operations."""
    collection_name = "concurrent_test_collection"
    vector_size = 4
    
    await vector_db_client.create_collection(
        collection_name=collection_name,
        vector_size=vector_size,
        distance=Distance.COSINE
    )
    
    async def concurrent_insert(start_id):
        points = [
            PointStruct(
                id=i,
                vector=[0.1, 0.2, 0.3, 0.4],
                payload={"metadata": f"test{i}"}
            ) for i in range(start_id, start_id + 10)
        ]
        await vector_db_client.insert_points(collection_name, points)
        return start_id
    
    # Run 5 concurrent insert operations
    tasks = [concurrent_insert(i * 10) for i in range(5)]
    results = await asyncio.gather(*tasks)
    
    # Verify all inserts were successful
    search_results = await vector_db_client.search(
        collection_name=collection_name,
        query_vector=[0.1, 0.2, 0.3, 0.4],
        limit=50
    )
    assert len(search_results) == 50

@pytest.mark.asyncio
async def test_concurrent_graph_db_operations(graph_db_client):
    """Test concurrent graph database operations."""
    async def create_person_node(index):
        props = {"name": f"Person{index}", "age": 30 + index}
        return await graph_db_client.create_node("Person", props)
    
    # Create multiple nodes concurrently
    tasks = [create_person_node(i) for i in range(10)]
    persons = await asyncio.gather(*tasks)
    
    # Verify all nodes were created
    query = "MATCH (p:Person) RETURN count(p) as count"
    result = await graph_db_client.execute_query(query)
    assert result[0]["count"] == 10

@pytest.mark.asyncio
async def test_database_connection_recovery(vector_db_client, graph_db_client):
    """Test database recovery after connection interruption."""
    collection_name = "recovery_test_collection"
    vector_size = 4
    
    # Simulate network partition during vector DB operation
    with patch.object(vector_db_client, 'client', side_effect=ConnectionError):
        with pytest.raises(ConnectionError):
            await vector_db_client.create_collection(
                collection_name=collection_name,
                vector_size=vector_size
            )
    
    # Verify recovery after connection restored
    await vector_db_client.create_collection(
        collection_name=collection_name,
        vector_size=vector_size
    )
    
    # Test graph DB connection recovery
    with patch.object(graph_db_client, 'driver', side_effect=ConnectionError):
        with pytest.raises(ConnectionError):
            await graph_db_client.create_node("Person", {"name": "Test"})
    
    # Verify recovery
    result = await graph_db_client.create_node("Person", {"name": "Test"})
    assert result is not None

@pytest.mark.asyncio
async def test_data_consistency_under_load(vector_db_client):
    """Test data consistency under concurrent load."""
    collection_name = "consistency_test_collection"
    vector_size = 4
    
    await vector_db_client.create_collection(
        collection_name=collection_name,
        vector_size=vector_size
    )
    
    async def write_and_read(index):
        # Write operation
        point = PointStruct(
            id=index,
            vector=[0.1, 0.2, 0.3, 0.4],
            payload={"value": index}
        )
        await vector_db_client.insert_points(collection_name, [point])
        
        # Read operation
        results = await vector_db_client.search(
            collection_name=collection_name,
            query_vector=[0.1, 0.2, 0.3, 0.4],
            limit=1
        )
        return results[0].payload["value"]
    
    # Run multiple concurrent read/write operations
    tasks = [write_and_read(i) for i in range(20)]
    results = await asyncio.gather(*tasks)
    
    # Verify data consistency
    assert len(set(results)) == 20