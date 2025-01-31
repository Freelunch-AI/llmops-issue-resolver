import pytest
from sandbox_orchestrator.databases.graph_db import GraphDatabase

@pytest.fixture
async def graph_db():
    db = GraphDatabase(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="test"
    )
    yield db
    await db.delete_all()
    db.close()

@pytest.mark.asyncio
async def test_create_and_query_nodes(graph_db):
    # Create test nodes
    person = await graph_db.create_node(
        label="Person",
        properties={"name": "John", "age": 30}
    )
    company = await graph_db.create_node(
        label="Company",
        properties={"name": "Tech Corp"}
    )
    
    # Query nodes
    result = await graph_db.execute_query(
        "MATCH (p:Person) WHERE p.name = $name RETURN p",
        {"name": "John"}
    )
    
    assert len(result) == 1
    assert result[0]["p"]["name"] == "John"

@pytest.mark.asyncio
async def test_create_and_query_relationships(graph_db):
    # Create nodes
    person = await graph_db.create_node(
        label="Person",
        properties={"name": "John"}
    )
    company = await graph_db.create_node(
        label="Company",
        properties={"name": "Tech Corp"}
    )
    
    # Create relationship
    rel = await graph_db.create_relationship(
        from_node_id=person.id,
        to_node_id=company.id,
        relationship_type="WORKS_AT",
        properties={"since": 2020}
    )
    
    # Query relationship
    result = await graph_db.execute_query("""
        MATCH (p:Person)-[r:WORKS_AT]->(c:Company)
        WHERE p.name = $name
        RETURN r.since as since
    """, {"name": "John"})
    
    assert len(result) == 1
    assert result[0]["since"] == 2020

@pytest.mark.asyncio
async def test_complex_query(graph_db):
    # Create test data
    await graph_db.create_node(
        label="Person",
        properties={"name": "John", "skill": "Python"}
    )
    await graph_db.create_node(
        label="Person",
        properties={"name": "Jane", "skill": "Java"}
    )
    
    # Complex query with aggregation
    result = await graph_db.execute_query("""
        MATCH (p:Person)
        WITH p.skill as skill, count(*) as count
        RETURN skill, count
        ORDER BY count DESC
    """)
    
    assert len(result) == 2
    assert all("skill" in r and "count" in r for r in result)

@pytest.mark.asyncio
async def test_delete_nodes(graph_db):
    # Create node
    node = await graph_db.create_node(
        label="Test",
        properties={"name": "test"}
    )
    
    # Delete all nodes
    await graph_db.delete_all()
    
    # Verify deletion
    result = await graph_db.execute_query(
        "MATCH (n) RETURN count(n) as count"
    )
    assert result[0]["count"] == 0