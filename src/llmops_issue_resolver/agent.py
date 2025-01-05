import os
import sys

sys.path.append(
    os.path.join("relative_path_to_llmops_issue_resolver", os.path.dirname(__file__))
)

import json
import shutil
from typing import Annotated, List, Literal, Sequence, TypedDict

import black
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage  # type: ignore
from langchain_core.tools import tool  # type: ignore
from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore
from langgraph.graph import (  # type: ignore
    END,
    START,
    MessagesState,
    StateGraph,
    add_messages,
)
from langgraph.prebuilt import ToolNode  # type: ignore

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

@tool
def get_directory_structure(path: str = ".") -> str:
    """
    Call to get a JSON representing the hierarchical structure of the
    directories and files starting from the given 'path' default = ".".
    """
    def build_structure(current_path: str) -> dict:
        node_name = os.path.basename(current_path) or current_path
        if os.path.isdir(current_path):
            structure = {
                "name": node_name,
                "nodeType": "directory",
                "children": []
            }
            for item in sorted(os.listdir(current_path)):
                if item in (".venv", "venv", ".git", "CURRENT-PROBLEMS.md"):
                    continue
                full_path = os.path.join(current_path, item)
                if os.path.isdir(full_path):
                    structure["children"].append(build_structure(full_path)) # type: ignore
                else:
                    structure["children"].append({ # type: ignore
                        "name": item,
                        "nodeType": "file"
                    })
        else:
            structure = {
                "name": node_name,
                "nodeType": "file"
            }
        return structure

    directory_structure = build_structure(path)
    return json.dumps(directory_structure)

@tool
def get_content_of_relevant_files(paths: List[str]) -> dict:
    """
    Call to get the full path, name of the file/folder and content (if it`s a file) 
    of all paths in the input list.
    """
    response = {}
    for path in paths:
        absolut_path = os.path.abspath(path)
        name = os.path.basename(path)
        if os.path.isfile(absolut_path):
            with open(absolut_path, "r", encoding="utf-8") as file:
                content = file.read()
        else:
            content = None
        response[path] = {
            'path': absolut_path,
            'name': name,
            'content': content
        }
    return response

@tool
def create_folder(path: str, folder_name: str):
    """Call to create a new folder."""
    os.mkdir(f"{path}/{folder_name}")
    return {"message": f"Folder {path}/{folder_name} created."}

@tool
def create_file(path: str, file_name: str):
    """Call to create a new file."""
    with open(f"{path}/{file_name}", "w", encoding="utf-8") as file:
        pass
    return {"message": f"File {path}/{file_name} created."}

@tool
def rename_folder(path: str, folder_name: str, new_folder_name: str):
    """Call to rename a specific folder."""
    os.rename(f"{path}/{folder_name}", f"{path}/{new_folder_name}")
    return {"message": f"Folder {path}/{folder_name} renamed to {path}/{new_folder_name}."}

@tool
def rename_file(path: str, file_name: str, new_file_name: str):
    """Call to rename a specific file."""
    os.rename(f"{path}/{file_name}", f"{path}/{new_file_name}")
    return {"message": f"File {path}/{file_name} renamed to {path}/{new_file_name}."}

@tool
def update_file(path: str, file_name: str, new_content: str):
    """Call to update a specific file."""
    try:
        formatted_content = new_content.replace("\\\"", "\"").replace("\\n", "\n")
        updated_content = black.format_str(formatted_content, mode=black.Mode())
    except Exception as e:
        raise ValueError(f"Erro ao formatar o código com Black: {e}")

    with open(f"{path}/{file_name}", "w", encoding="utf-8") as file:
        file.write(updated_content)
    return {"message": f"File {path}/{file_name} updated."}

@tool
def delete_folder(path: str, folder_name: str):
    """Call to delete a specific folder."""
    shutil.rmtree(f"{path}/{folder_name}")
    return {"message": f"Folder {path}/{folder_name} deleted."}

@tool
def delete_file(path: str, file_name: str):
    """Call to delete a specific file."""
    os.remove(f"{path}/{file_name}")
    return {"message": f"File {path}/{file_name} deleted."}

tools = [
    get_directory_structure,
    get_content_of_relevant_files,
    create_folder, 
    create_file,
    rename_folder,
    rename_file,
    update_file,
    delete_folder,
    delete_file
]

tool_node = ToolNode(tools)

model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0
).bind_tools(tools)

system_prompt = """
You are a Automated Software Engineer that need to update the codebase.
You are running in the root directory of the codebase.
Use the available tools to know the directory structure of the codebase, read and manipulate files and folders.
Follow these steps:
    1. Call tool get_directory_structure to access and understand the codebase;
    2. Find the path to issue.md file and get it's content using get_content_of_relevant_files tool;
    3. Based on issue details, use the tool get_directory_structure to get and analyze all the folders and file names;
    4. Generate a list of relevant file paths that you will want to analyze the content;
    5. Call get_content_of_relevant_files to get the content of the selected files;
    6. Understand the codebase and plan which files you'll need to update or create to fix the issue;
    7. Apply the diffs using the tools to create, rename, update and delete files and folders.
"""

def should_continue(state: MessagesState) -> Literal["tools", END]: # type: ignore
    messages = state['messages']
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

def call_model(state: MessagesState):
    messages = state['messages']
    messages = [
        {"role": "system", "content": system_prompt}
    ] + messages
    response = model.invoke(messages)
    return {"messages": [response]}

workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent", 
    should_continue, 
    ["tools", END]
)
workflow.add_edge("tools", 'agent')
graph = workflow.compile()
