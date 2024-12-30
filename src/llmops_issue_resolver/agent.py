import json
import os
import shutil
from typing import Annotated, Any, List, Literal, Sequence, TypedDict

import black
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, MessagesState, StateGraph, add_messages
from langgraph.prebuilt import ToolNode

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

@tool
def get_directory_structure(path: str = "."):
    """
    Call to get a JSON representing the hierarchical structure of the
    directories and files starting from the given 'path' default = ".".
    """
    node_name = os.path.basename(path)
    if not node_name:
        node_name = path

    structure = {
        "name": node_name,
        "nodeType": "directory",
        "children": []
    }

    if os.path.isdir(path):
        for item in sorted(os.listdir(path)):
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                structure["children"].append(get_directory_structure(full_path))
            else:
                structure["children"].append({
                    "name": item,
                    "nodeType": "file"
                })
    else:
        structure = {
            "name": node_name,
            "nodeType": "file"
        }
    return json.dumps(structure)

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
You are an AI agent that resolves issues on codebases.
Use the available tools to get directory structure, file contents and manipulate files and folder in the directory.
Follow these steps:
    1. Get the directory structure and understand it.
    2. Find the path to issue.md file and get it's content.
    3. Based on issue details, analyze the folders and file names to generate a list of relevant file paths that you will want to analyze the content.
    4. Get the content of the files based on the list of paths generated.
    5. Find the problem(s) and generated the diffs.
    7. Apply changes in the environment.
"""

def should_continue(state: MessagesState) -> Literal["tools", END]:
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