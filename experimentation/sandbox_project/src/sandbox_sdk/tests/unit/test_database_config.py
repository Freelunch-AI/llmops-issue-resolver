import pytest
from pathlib import Path
from sandbox_orchestrator.core.models.database import (
    DatabaseConfig,
    VectorDBConfig,
    GraphDBConfig,
    DatabasesConfig
)

@pytest.fixture
def vector_db_config():
    return {
        "host": "localhost",
        "port": 6333,
        "credentials": {
            "api_key": "test-key",
            "user": "test-user",
            "password": "test-pass"
        },
        "collections": [
            {
                "name": "test",
                "vector_size": 128,
                "distance": "cosine"
            }
        ]
    }

@pytest.fixture
def graph_db_config():
    return {
        "host": "localhost",
        "port": 7687,
        "credentials": {
            "user": "neo4j",
            "password": "test-pass"
        },
        "initial_data": {
            "nodes": [
                {
                    "label": "Test",
                    "properties": {"name": "test1"}
                }
            ],
            "relationships": []
        }
    }

def test_vector_db_config(vector_db_config):
    config = VectorDBConfig(**vector_db_config)
    assert config.host == "localhost"
    assert config.port == 6333
    assert len(config.collections) == 1
    assert config.collections[0]["name"] == "test"

def test_graph_db_config(graph_db_config):
    config = GraphDBConfig(**graph_db_config)
    assert config.host == "localhost"
    assert config.port == 7687
    assert len(config.initial_data["nodes"]) == 1
    assert len(config.initial_data["relationships"]) == 0

def test_invalid_vector_db_config(vector_db_config):
    # Remove required field
    del vector_db_config["collections"][0]["vector_size"]
    with pytest.raises(ValueError):
        VectorDBConfig(**vector_db_config)

def test_invalid_graph_db_config(graph_db_config):
    # Remove required field
    del graph_db_config["initial_data"]["relationships"]
    with pytest.raises(ValueError):
        GraphDBConfig(**graph_db_config)

def test_databases_config_from_yaml(tmp_path):
    # Create test config files
    vector_config = tmp_path / "vector.yml"
    vector_config.write_text("""
host: localhost
port: 6333
credentials:
  api_key: test-key
collections:
  - name: test
    vector_size: 128
""")
    
    graph_config = tmp_path / "graph.yml"
    graph_config.write_text("""
host: localhost
port: 7687
credentials:
  user: neo4j
  password: test
initial_data:
  nodes: []
  relationships: []
""")
    
    config = DatabasesConfig.from_yaml(vector_config, graph_config)
    assert isinstance(config.vector_db, VectorDBConfig)
    assert isinstance(config.graph_db, GraphDBConfig)