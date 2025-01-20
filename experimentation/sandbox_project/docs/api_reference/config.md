# Configuration Reference

## Database Configuration

### Vector Database (Qdrant)

```yaml
host: localhost
port: 6333
credentials:
  api_key: "your-api-key-here"
  user: "qdrant_user"
  password: "qdrant_password"

collections:
  - name: default
    vector_size: 768
    distance: cosine
    initial_data: []
  
  - name: documents
    vector_size: 1024
    distance: euclidean
    initial_data:
      - id: 1
        vector: [0.1, 0.2, 0.3]
        payload:
          text: "Example document 1"
          metadata:
            source: "test"

security:
  ssl_enabled: true
  ssl_cert_path: "/path/to/cert.pem"
  ssl_key_path: "/path/to/key.pem"

performance:
  max_concurrent_requests: 100
  batch_size: 100
  optimization_interval_sec: 3600
```

### Graph Database (Neo4j)

```yaml
host: localhost
port: 7687
credentials:
  user: "neo4j"
  password: "neo4j_password"

initial_data:
  nodes:
    - label: "Person"
      properties:
        name: "John Doe"
        age: 30
    
    - label: "Company"
      properties:
        name: "Tech Corp"
        industry: "Technology"
  
  relationships:
    - from_label: "Person"
      from_properties:
        name: "John Doe"
      to_label: "Company"
      to_properties:
        name: "Tech Corp"
      type: "WORKS_AT"
      properties:
        since: 2021

security:
  ssl_enabled: true
  ssl_cert_path: "/path/to/cert.pem"
  ssl_key_path: "/path/to/key.pem"
  encryption_enabled: true

performance:
  max_connections: 50
  connection_timeout_ms: 5000

backup:
  enabled: true
  schedule: "0 0 * * *"
  retention_days: 7
```

## Sandbox Configuration

### Initialization Config

```yaml
databases:
  vector_db:
    collections:
      - name: default
        vector_size: 768
        initial_data: []
  
  graph_db:
    nodes:
      - label: "TestNode"
        properties:
          name: "Test 1"
    relationships: []

sandbox_defaults:
  resources:
    cpu_cores: 1
    ram_gb: 2
    disk_gb: 10
    memory_bandwidth_gbps: 5
    unit: absolute
  
  security:
    network_isolation: true
    max_processes: 50
    read_only_root: true
    drop_capabilities:
      - NET_ADMIN
      - SYS_ADMIN
  
  environment:
    PYTHONPATH: /workspace
    PYTHONUNBUFFERED: "1"
```

## Configuration Models

### Database Models

```python
class DatabaseConfig(BaseModel):
    host: str
    port: int
    credentials: Dict[str, str]
    security: Dict[str, Union[bool, str]]
    performance: Dict[str, Union[int, float]]

class VectorDBConfig(DatabaseConfig):
    collections: List[Dict[str, Union[str, int, List]]]
    initial_data: Optional[List[Dict]]

class GraphDBConfig(DatabaseConfig):
    initial_data: Dict[str, List[Dict]]
    backup: Dict[str, Union[bool, str, int]]

class DatabasesConfig(BaseModel):
    vector_db: VectorDBConfig
    graph_db: GraphDBConfig
```

### Sandbox Models

```python
class ResourceConfig(BaseModel):
    cpu_cores: Union[int, float]
    ram_gb: Union[int, float]
    disk_gb: Union[int, float]
    memory_bandwidth_gbps: Union[int, float]
    unit: str  # "absolute" or "relative"

class SecurityConfig(BaseModel):
    network_isolation: bool
    max_processes: Optional[int]
    allowed_syscalls: Optional[List[str]]
    read_only_root: bool
    drop_capabilities: List[str]

class SandboxConfig(BaseModel):
    id: str
    resources: ResourceConfig
    security: SecurityConfig
    environment: Dict[str, str]
    tools: List[str]
    working_directory: Path
```