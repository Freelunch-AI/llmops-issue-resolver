# Database Components

This directory contains the database implementations used in the sandbox orchestrator for efficient storage and retrieval of data. The system utilizes both vector and graph databases to handle different aspects of data management.

## Directory Structure

```
databases/
├── vector_db/
│   └── vector_db.py
└── graph_db/
    └── graph_db.py
```

## Vector Database

The `vector_db` directory implements vector storage and similarity search capabilities:

- **Purpose**: Stores and manages high-dimensional vectors representing embeddings of code snippets, issue descriptions, and related metadata
- **Key Features**:
  - Efficient similarity search for finding related issues and code patterns
  - Batch processing for multiple embeddings
  - Customizable distance metrics for similarity calculations
  - Persistence and indexing of vector data

### Integration with Orchestrator

The vector database component interfaces with the orchestrator through:
- Embedding storage during issue analysis
- Similarity searches for pattern matching
- Retrieval of related historical issues

## Graph Database

The `graph_db` directory implements graph-based storage for relationship mapping:

- **Purpose**: Maintains relationships between issues, code components, and resolution patterns
- **Key Features**:
  - Relationship modeling between different entities
  - Query capabilities for traversing connected data
  - Pattern matching for identifying similar issue structures
  - Transaction support for maintaining data consistency

### Integration with Orchestrator

The graph database component interfaces with the orchestrator through:
- Storing issue-code relationships
- Tracking resolution patterns
- Query operations for finding connected components

## Usage in the Sandbox Environment

Both databases work together to provide comprehensive data management:

1. **Initial Processing**:
   - Vector DB stores embeddings of new issues
   - Graph DB creates initial relationship nodes

2. **Analysis Phase**:
   - Vector DB performs similarity searches
   - Graph DB traverses related patterns

3. **Resolution Phase**:
   - Vector DB identifies similar historical solutions
   - Graph DB maps resolution patterns

## Implementation Details

### Vector Database Implementation

The `vector_db.py` module provides:
- Vector storage and indexing
- Similarity search operations
- Batch processing capabilities
- Persistence management

### Graph Database Implementation

The `graph_db.py` module provides:
- Node and relationship management
- Query operations
- Pattern matching
- Transaction handling

## Integration Points

The databases integrate with other components through:

1. **Orchestrator Interface**:
   - Direct method calls for database operations
   - Async support for non-blocking operations
   - Transaction management

2. **Data Flow**:
   - Input processing pipeline
   - Query execution
   - Result aggregation

3. **Error Handling**:
   - Connection management
   - Query timeout handling
   - Data consistency checks