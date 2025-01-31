import io
from pathlib import Path

from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer

from sandbox_toolkit.logs.logging import logger
from src.sandbox_toolkit.infra.sandbox_base.schema_models.internal_schemas import (
    SimilaritySearchResult,
    ToolReturn,
)


def read_file(file_path: str) -> str:
    try:
        with open(file_path, "r") as file:
            return file.read()
    except Exception as e:
        return f"Error: {str(e)}"

class GraphDB:
    def __init__(self, config_path="src/sandbox_toolkit/infra/databases/graph_db/config/neo4j_config.yaml"):
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        self.driver = GraphDatabase.driver(
            config["database"]["host"],
            auth=(config["database"]["credentials"]["user"], config["database"]["credentials"]["password"]),
        )

    async def execute_query(self, query: str):
        logger.info(f"Executing query: {query}")
        async with self.driver.session() as session:
            result = await session.run(query)
        return result.data()

    async def create_node(self, label: str, properties: dict):
        logger.info(f"Creating node with label: {label}, properties: {properties}")
        async with self.driver.session() as session:
            result = await session.run(
                f"CREATE (n:{label} $properties) RETURN n", properties=properties
            )
        return result.data()

    async def create_relationship(self, from_node_label: str, from_node_properties: dict, to_node_label: str, to_node_properties: dict, relationship_type: str, relationship_properties: dict):
        logger.info(f"Creating relationship of type {relationship_type} between nodes with labels {from_node_label} and {to_node_label}")
        async with self.driver.session() as session:
            result = await session.run(
                f"""
                MATCH (a:{from_node_label}), (b:{to_node_label})
                WHERE a = $from_node_properties AND b = $to_node_properties
                CREATE (a)-[r:{relationship_type} $relationship_properties]->(b)
                RETURN r
                """,
                from_node_properties=from_node_properties,
                to_node_properties=to_node_properties,
                relationship_properties=relationship_properties
            )
        return result.data()


async def execute_query() -> ToolReturn:
    with io.StringIO() as stdout, io.StringIO() as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            logger.info(f"Starting execute_query")
            return_value = None

            graph_db = GraphDB()
            return_value = await graph_db.execute_query("MATCH (n) RETURN n LIMIT 10")

            log_file_path = "src/sandbox_toolkit/infra/sandbox_base/logs/logs/tools/database_tools.log"
            logs = ""
            if Path(log_file_path).exists():
                try:
                    with open(log_file_path, "r") as f:
                        logs = f.read()
                except FileNotFoundError:
                    logs = ""
            logger.info(f"Finished execute_query, output: {return_value}")
            return ToolReturn(return_value=return_value, std_out=stdout.getvalue(), std_err=stderr.getvalue(), logs=logs)
    

async def create_node() -> ToolReturn: # Placeholder for graph database tools
    with io.StringIO() as stdout, io.StringIO() as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            logger.info(f"Starting create_node")
  
            graph_db = GraphDB()
            return_value = await graph_db.create_node("TestNode", {"name": "Test Node"})

            log_file_path = "../logs/logs/tools/database_tools.log"
            logs = ""
            if Path(log_file_path).exists():
                try:
                    with open(log_file_path, "r") as f:
                        logs = f.read()
                except FileNotFoundError:
                    logs = ""
            logger.info(f"Finished create_node, output: {return_value}")
            return ToolReturn(return_value=return_value, std_out=stdout.getvalue(), std_err=stderr.getvalue(), logs=logs)

async def create_relationship() -> ToolReturn: # Placeholder for graph database tools
    logger.info(f"Starting create_relationship")
    with io.StringIO() as stdout, io.StringIO() as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):

            # Placeholder for creating relationship
            graph_db = GraphDB()
            return_value = await graph_db.create_relationship(
                "TestNode", {"name": "Test Node"}, "TestNode", {"name": "Test Node"}, "RELATED_TO", {"relation": "test"}
            )

            log_file_path = "../logs/logs/tools/database_tools.log"
            logs = ""
            if Path(log_file_path).exists():
                try:
                    with open(log_file_path, "r") as f:
                        logs = f.read()
                except FileNotFoundError:
                    logs = ""
            logger.info(f"Finished create_relationship, output: {return_value}")
            return ToolReturn(return_value=return_value, std_out=stdout.getvalue(), std_err=stderr.getvalue(), logs=logs)

class DocumentStore:
    def __init__(self, config_path="src/sandbox_toolkit/infra/databases/vector_db/config/qdrant_config.yaml"):
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        self.client = QdrantClient(host=config["database"]["host"], port=config["database"]["port"])
        self.embedding_model = SentenceTransformer('all-mpnet-base-v2')
        self.knowledge_files_path = "knowledge"  # TODO: make this configurable
        self.collection_name = config["collections"][0]["name"]  # TODO: make this configurable
        self.tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

    async def store_files(self, directory_path: Path) -> None:
        logger.info(f"Storing files from directory: {directory_path}")
        directory = Path(directory_path)
        if not directory.exists() or not directory.is_dir():
            return f"Error: Directory not found at path '{directory_path}'"

        file_paths = [f for f in directory.glob('*') if f.is_file()]
        for file_path in file_paths:
            file_content = read_file(str(file_path))
            if file_content.startswith("Error:"):
                return file_content

            # Chunk file content
            max_chunk_tokens = 500
            lines = file_content.splitlines()
            chunks = []
            current_chunk = ""
            for line in lines:
                line_tokens = self.tokenizer.tokenize(line)
                if len(self.tokenizer.tokenize(current_chunk) + line_tokens) <= max_chunk_tokens:
                    current_chunk += line + "\n"
                else:
                    chunks.append(current_chunk)
                    current_chunk = line + "\n"
            if current_chunk:
                chunks.append(current_chunk)

            # Embed chunks and store in Qdrant
            points = []
            for chunk_index, chunk in enumerate(chunks):
                embedding = self.embedding_model.encode(chunk)
                point_id = hash(str(file_path) + str(chunk_index))
                payload = {"file_path": str(file_path), "chunk_index": chunk_index}
                points.append(models.PointStruct(id=point_id, vector=embedding, payload=payload))

            # Create collection if not exists
            await self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=embedding.shape[0], distance=models.Distance.COSINE),
            )

            # Store embeddings in Qdrant collection
            await self.client.upsert(collection_name=self.collection_name, points=points)

            print(f"Stored {len(chunks)} chunks from file {file_path} to Qdrant collection {self.collection_name}")
        return

    async def retrieve_relevant_parts(self, query: str) -> List[SimilaritySearchResult]:
        logger.info(f"Retrieving relevant parts for query: {query}")
        logger.info(f"Input query: {query}")
        embedding = self.embedding_model.encode(query)
        search_result = await self.client.search(
            collection_name=self.collection_name,
            query_vector=embedding,
            limit=5,  # TODO: make this configurable
        )

        results = []
        for result in search_result:
            file_path = result.payload["file_path"]
            chunk_index = result.payload["chunk_index"]
            
            file_content = read_file(file_path)
            if file_content.startswith("Error:"):
                logger.error(f"Error reading file: {file_path}")
                continue
            
            lines = file_content.splitlines()
            chunks = []
            current_chunk = ""
            max_chunk_tokens = 500
            tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
            for line in lines:
                line_tokens = tokenizer.tokenize(line)
                if len(tokenizer.tokenize(current_chunk) + line_tokens) <= max_chunk_tokens:
                    current_chunk += line + "\\n"
                else:
                    chunks.append(current_chunk)
                    current_chunk = line + "\\n"
            if current_chunk:
                chunks.append(current_chunk)
            
            if chunk_index < len(chunks):
                chunk_content = chunks[chunk_index]
            else:
                logger.error(f"Chunk index {chunk_index} out of range for file {file_path}")
                continue

            results.append(SimilaritySearchResult(**{
                "file_content": file_content,
                "chunk_content": chunk_content,
                "score": result.score,
            }))
        logger.info(f"Finished retrieving relevant parts, output: {results}")
        return results
    