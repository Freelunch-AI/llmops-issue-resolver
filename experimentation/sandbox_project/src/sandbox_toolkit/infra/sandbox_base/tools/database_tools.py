import contextlib
import io
from pathlib import Path

from sandbox_toolkit.logs.logging import logger
from src.sandbox_toolkit.infra.sandbox_base.schema_models.internal_schemas import (
    ToolReturn,
)

from ..helpers.database_tools import *


async def store_directory_of_files(directory_path: str, collection_name: str) -> ToolReturn:
    """Stores a directory of files into the vector database for semantic search."""
    with io.StringIO() as stdout, io.StringIO() as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            logger.info(f"Starting store_directory_of_files with directory: {directory_path}, collection: {collection_name}")

            document_store = DocumentStore()
            return_value = await document_store.store_files(directory_path)

            log_file_path = "../logs/logs/tools/database_tools.log"
            logs = ""
            if Path(log_file_path).exists():
                try:
                    with open(log_file_path, "r") as f:
                        logs = f.read()
                except FileNotFoundError:
                    logs = ""
            logger.info(f"Finished store_directory_of_files, output: {return_value}")
            return ToolReturn(return_value=return_value, std_out=stdout.getvalue(), std_err=stderr.getvalue(), logs=logs)

async def given_a_query_and_directory_retrieve_relevant_parts_of_files_within_the_directory(query: str, directory_path: str, collection_name: str) -> ToolReturn:
    """Retrieves relevant parts of files within a directory from vector database based on a query."""
    logger.info(f"Starting given_a_query_and_directory_retrieve_relevant_parts_of_files_within_the_directory with query: {query}, directory: {directory_path}, collection: {collection_name}")
    with io.StringIO() as stdout, io.StringIO() as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            document_store = DocumentStore()
            return_value = await document_store.retrieve_relevant_parts(query)
            log_file_path = "../logs/logs/tools/database_tools.log"
            logs = ""
            if Path(log_file_path).exists():
                try:
                    with open(log_file_path, "r") as f:
                        logs = f.read()
                except FileNotFoundError:
                    logs = ""
            logger.info(f"Finished given_a_query_and_directory_retrieve_relevant_parts_of_files_within_the_directory, output: {return_value}")
            return ToolReturn(return_value=return_value, std_out=stdout.getvalue(), std_err=stderr.getvalue(), logs=logs)
