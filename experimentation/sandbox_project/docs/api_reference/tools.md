# Sandbox Tools API Reference

## Filesystem Tools

### read_file
```python
def read_file(path: str) -> str
```
Read content of a file.

### create_file
```python
def create_file(path: str, content: str) -> None
```
Create a new file with content.

### delete_file
```python
def delete_file(path: str) -> None
```
Delete a file.

### append_to_file
```python
def append_to_file(path: str, content: str) -> None
```
Append content to a file.

### overwrite_file
```python
def overwrite_file(path: str, content: str) -> None
```
Overwrite content of a file.

### move_file
```python
def move_file(src: str, dst: str) -> None
```
Move a file from src to dst.

### copy_file
```python
def copy_file(src: str, dst: str) -> None
```
Copy a file from src to dst.

### list_directory
```python
def list_directory(path: str, pattern: Optional[str] = None) -> List[str]
```
List contents of a directory, optionally filtered by pattern.

### create_directory
```python
def create_directory(path: str, exist_ok: bool = True) -> None
```
Create a directory and its parents if they don't exist.

## Terminal Tools

### change_directory
```python
def change_directory(path: str) -> None
```
Change current working directory.

### execute_command
```python
def execute_command(
    command: str,
    timeout: Optional[int] = None
) -> Tuple[str, str, bool]
```
Execute a shell command and return stdout, stderr and if process is still running.

### uv_add_package
```python
def uv_add_package(package: str) -> Tuple[str, str, bool]
```
Add a package to requirements.txt using uv.

### uv_remove_package
```python
def uv_remove_package(package: str) -> Tuple[str, str, bool]
```
Remove a package using uv.

### run_python_script
```python
def run_python_script(script_path: str) -> Tuple[str, str, bool]
```
Run a Python script.

## Web Tools

### scrape_website
```python
async def scrape_website(url: str) -> str
```
Scrape entire website and return content as markdown.

### web_search
```python
async def web_search(
    query: str,
    api_key: str,
    cx: str
) -> List[str]
```
Perform web search using Google Custom Search API.

### extract_data_from_website
```python
async def extract_data_from_website(
    url: str,
    selectors: Dict[str, str]
) -> Dict[str, str]
```
Extract specific data from website using browser automation.

## Database Tools

### Vector Database

#### create_collection
```python
def create_collection(
    collection_name: str,
    vector_size: int,
    distance: Distance = Distance.COSINE
)
```
Create a new collection.

#### insert_points
```python
def insert_points(
    collection_name: str,
    points: List[PointStruct]
)
```
Insert points into collection.

#### search
```python
def search(
    collection_name: str,
    query_vector: List[float],
    limit: int = 10,
    filter: Optional[Dict] = None
)
```
Search for similar vectors.

### Graph Database

#### execute_query
```python
def execute_query(
    query: str,
    parameters: Optional[Dict] = None
) -> List[Dict]
```
Execute Cypher query.

#### create_node
```python
def create_node(
    label: str,
    properties: Dict
)
```
Create a new node.

#### create_relationship
```python
def create_relationship(
    from_node_id: int,
    to_node_id: int,
    relationship_type: str,
    properties: Optional[Dict] = None
)
```
Create relationship between nodes.