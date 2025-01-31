# Sandbox Toolkit Package Specification

## Overview

This python package should let users create, manage and delete sandboxes.  We define sandboxes as isolated container environments that listen to action execution requests, executes the requested actions and return the gathered observation.

Actions execution requests: are requests to call some tools (python functions) with specified argument values.

Gathered Observations: Dict["<function_name>": (terminal output: str, process_still_running: bool)]

## Details

### Actions Execution format

The following format is used to specify the execution of actions:

{
    "foo": {
        "function_call_explanation": "<explanation_for_this_specific_foo_call_goes_here>",
        "args": {
            "<first_foo_argument_goes_here>": <first_foo_argument_value_goes_here>,
            "<second_foo_argument_goes_here>": <second_foo_argument_value_goes_here>
        }
    },

    "bar": {
        "function_call_explanation": "<explanation_for_this_specific_bar_call_goes_here>",
        "args": {
            "<first_bar_argument_goes_here>": <first_bar_argument_value_goes_here>,
            "<second_bar_argument_goes_here>": <second_bar_argument_value_goes_here>
        }
    },
}

where foo and bar are example function names. things written in between <> are variables which values cant be known a priori but will be known
when the action execution request is sent.

The ActionExecutionRequest Pydantic model will need to support this action execution format.

### Sandboxes are built dynamically

The toolkit allows the user to pass a list of tools (python functions) of type List[Callable] = None or pass a list of tool paths of type List[Path] = None.

- If the user passes List[Callable]: then only the specific tools the user provided are incorporated into the Sandbox.

- If the user passes List[Path]: then all tools under the specific paths the user provided (which must be under his local /tools drectory) are incorporated into the Sandbox.

- If the doesn passes nothing: the all tools of his local /tools directory are incorporated into the Sandbox.

These function are then incorporated into the Sandbox Dockerfile on top of the default tools. The directory structure the user used for defining functions is respected. The user is obligated to write his tools under his local /tools directory, but he can create whatever directory strcture and modules he like in it, to put his tools. Under the hood, the toolkit will recreate his entire tools folder in the sandobox's Dockerfile but stripping away not provided functions and stripping away modules that do not contain provided functions. Functions can be provided directly (via the functions themselves) or indirectly (via paths under /tools or when all tools are used which is the default case)

The way they are incorprated happens by the Sandbox Orchestrator dynamically modifying the DockerFile.sandboxbase file to add the new tools (respecting the user's directory structure). Then the sandbox orchestrator builds the sandbox image, Finally the sandbox orchestrator dynamically modifies the sandbox-docker-compose template to make a specific docker-compose for each sandbox which will reference the Dockerfile previosuly built and also define a new netowork of that specific sandbox which will contain the specific sandbox and its ttached databases. Each sandbox must have an id and each sandbox network must have the sandbox id in its name (e.g., sandbox_network_{id}).

Under the hood the SDK will have to build a tool directory object wich contains the directories containing suer specified tools. Each directory can contain directory objects and python module objects. Python module objects should contain one or more function objects; function object should contain the function name, and the entire function as a string. 

The SDK will send this built tool directory object to the sandbox_orchestrator so that the sandbox orchestrator knows exactly how to add tools to the Sandboxe's Dockerfile.

### the SDK should automatically start infra when ifra is needed

(e.g., it need to make a start_sandbox request to the orchestrator, therefore, it needs to first start infra so that the orchestrator is running.)

### Creating and starting sandboxes is decoupled

User first create the sandboxes (define its specification) then they start the sandbox (which will deploy the sandbx service)

### Sandbox Groups

Users can create multiple sandboxes in a single command by user the SandBoxGroup class to create either:

- multiple sandboxes with the same spcification
- multiple sandboxes, each with its own specification

### Snadbox Specification

Upon creation of a sandbox, users must provide the following config:

SandboxConfig:

- compute_config: ComputeConfig
- database_config: DatabaseConfig
- tools: Tools

-----------

ComputeConfig:
- cpu
- ram
- disk
- memory_bandwidth
- networking_bandwith
- unit=ResourceUnit.ABSOLUTE

where these resources can be provided in absolute values or % of the machine's 
resources

Note: the SDK cant let user create sandboxes which cause the total amount of compute reosurces requires to me more than the total amount available (int the machine ruunin the sandoxes).

-------------

DatabaseConfig

database_type=DatabaseType.VECTOR,
access_type=DatabaseAccessType.READ_WRITE,
namespaces=["default"]

--------------

Tools
- tools: Optional[Union[List[Callable], List[Path]]]

### Directory Semantic Search Built-in Tool

Need to build a Directory Semantic Search tool that will be a wrapper around the vector database. It will
allow users to store directories and retrive relevant pieces of files within specifiec directories fora given query.

Under the hod it is: (1) adding the file path at the top of the file and treating each file as a document; (2) hunking documents, 
(3) using an embedding model to embed chunks; (4) using the vector database to store the chunks long with their embeddings; (5) embedding query with embedding model;
(6) using vector databse to get relevant chunks; (7) builsding a search reuslt object with the chunks where each shunk has a file_name property 
and a file_path property where filereferes to the file the hcunk is in.

### Default tools

Sandboxes already come with deafult built-in tools:

### Filesystem Tools
- read_file
- create_file
- delete_file
- append_to_file
- overwrite_file
- edit_file_line_range
- move_file
- copy_file
- list_directory
- create_directory

### Terminal Tools
- execute_command
- change_directory
- get_current_directory
- uv_add_package
- uv_remove_package
- uv_sync_packages
- uv_run_python_script
- install_system_package
- get_total_available_and_used_compute_resources

### Web Tools
- scrape_website
- google_search
- get_most_voted_coding_forum_answers_to_similar_problems (e.g., of coding forum: stack overflow)

### Database Tools
- Semantic Search (on top of Qdrant vector db)
  - store_directory_of_files
  - given_a_query_and_dreictory_retrive_relevant_parts_of_files_within_the_directory

- Graph Database (Neo4j)
  - execute_query
  - create_node
  - create_relationship

### Error Handling

The Sandbox Toolkit uses exceptions to indicate errors:

- SandboxError: Base exception class
- DatabaseError: Database-related errors
- ResourceError: Resource allocation errors
- ToolError: Tool execution errors

## Disclaimer

The focus is to build a minimal python package, there is no need to worry about security and performance beyond implementing basic authentication and asynchronous python. Try to keep it as simple as possible. Improvements can bemade later.

## Interface

Example usage of the Sandbox Toolkit (The SDK needs to provide this interface):

```python

from sandbox_toolkit import SandboxGroup

# Configure the sandbox group (every sandbox that is created under this group will inherit this config)
sandbox_config = SandBoxConfig(
    ComputeConfig(cpu=2, ram=3, disk=50, memory_bandwith=10, networkng_bandwith=100, unit=ResourceUnit.ABSOLUTE),

    DatabaseConfig(database_type=DatabaseType.VECTOR, access_type=DatabaseAccessType.READ_WRITE, namespaces=["default"]),

    tools=[foo, bar]

)

# Create the sandbox group
sandbox_group = SandboxGroup(
    sandbox_config=sanbox_config
    tools=tools
)

# Start the group
await sandbox_group.start()

# Create a sandbox under the previously created sandbox group
sandbox = await sandbox_group.create_sandbox("sandbox1")

# Start the new sandbox
await sandbox.start()

# Execute actions
observations = await sandbox.send_actions({
    "read_file": {
        "description": "Read content of test.txt",
        "args": {
            "path": "test.txt"
        }
    },
    "execute_command": {
        "description": "List directory contents",
        "args": {
            "command": "ls -la"
        }
    }
})

# Process observations
for obs in observations:
    print(f"stdout: {obs.stdout}")
    print(f"stderr: {obs.stderr}")
    print(f"terminal running: {obs.terminal_still_running}")

# Cleanup
await sandbox.end()
await group.end_group()

# If the user doesnt clean-up, the SDK Toolkit will automatically end groups and sandoboxes if they are inactive for a while

##############################################

# The user can also use the sandbox context which cleans up the sandbox group or sandbox automatically (example below uses sandbox_group context)

with sandbox_context(sandbox_group) as sandbox_group:

    # Start the group
    await sandbox_group.start()

    # Create a sandbox under the previously created sandbox group
    sandbox = await sandbox_group.create_sandbox("sandbox1")

    await sandbox.start()

    # Execute actions
    observations = await sandbox.send_actions({
        "read_file": {
            "description": "Read content of test.txt",
            "args": {
                "path": "test.txt"
            }
        },
        "execute_command": {
            "description": "List directory contents",
            "args": {
                "command": "ls -la"
            }
        }
    })

    # Process observations
    for obs in observations:
        print(f"stdout: {obs.stdout}")
        print(f"stderr: {obs.stderr}")
        print(f"terminal running: {obs.terminal_still_running}")

```

## Capabilities

Sandoxes also support more capabilities like:
    - return history: List[(actions, observations)]
    - return list of tools available with api reference for each tool
    - return current resource usage (% of of sandboxe's resources that are being used)

Sandbox Orchestrator also supports:
    - lowering the amount of resources allocated to a specific sandbox or sandbox group by an x multiplier.
    - automatically lowering the amount of resources allocated to a specific sandbox or sandbox group to be the max(last 5 resource usage measurements)*x where x is a multipler and x > 1. This needs to be configured.
    - Clenaing up unused sandboxes if they are inactive for a while.

SDK also supports:
    - giving the user compute resource stats: available compute resources, resource used bt each sandbox and resources allocated to each sanbox.
    - giving the user history stats: for how long the sandbox is running, amount of actions sent to each sandbox

## Security

Tool executions cannot pass specific memory usage, time limit and processes started values. This enrues that no tool can crash the system.

## Architecture

SDK: Library
- provides users with functions and classes to create, manage, use and delete sandboxes
- starts the infrastrcture by deploying the docker-compose file. Will start orchestrator service and databases (vector database and graph database)
- Creates, Managed and deletes sandboxes by making requests to the orchestrator
- Uses sandboxes by making requests to specific sandboxes. It receives sandboxe's URLs from the orchestrator.

Sandbox Orchestrator: Service
- Creates, Manages and Deletes Sandboxes
- Listens to SDK requests
- Dunamically writes Sandbox Dockerfile my modifiyng the base sandbox dockerfile to include user provided tools
- Dyamically builds sandbox image
- Dynamically wirtes sandbox docker-compose file ensuring sandboxes cant communicate with each other, only with the databases they are attached to. Databases also cannot communicate eth each other.

Sanboxes: Services
- dynamically built and started by the orchestrator, each one with its URL
- used by the SDK to execute action, get observations, resource usage, etc

## Directory Structure Explanation

- docs
    - developer_docs: holds docuementaiton for package developers
    - user_docs: holds documentation for package users
        - api_reference: describes how to use each user-facing SDK class and function
        - tutorial: makes it easy for a new user to start using the package
- src
    - sandbox_toolkit: the package itself
        - helpers: project-specific helper code
            - exceptions: holds custom excetpions
            - schema_models: holds pydantic models for the entire package.
        - infra: holds the code for services necessary for the toolkit
            - databases: holds vector and graph database config and initial data to populate the databases. Third-party packages are used for the databases, thefore we dont write database code, just config and initial data.
            - sandbox_base: holds sandbox code and Dockerfile. The orchestrator will add user-specific tools on top of this code to actually build the final sandbox the user wants.
            - sandbox_orchestrator: holds orchestrator code and Dockerfile. The orchestrator dynamically writes Sandbox Dockerfile and then builds the sandbox, then dynamically wrties sandbox docker-compose (based on sandbox-docker-compose.yml.template) and deploys the each sandbox in its own netowork (with their attached databases inside the network as well)
        - logs: holds logs for the entire package
            - infra: holds infra logs
                - databases: holds databases logs
                - sandboxes: holds sandboxes logs
                - sandox orchestrator: holds orchestrator logs
            - sdk: holds sdk logs
        - sdk: holds the code the interacts with the user and makes request to the orchestrator (to manage sandboxes) and to sandboxes (to execute actions, ge thistory or list of tools)
            - core: holds the core code that doesnt interact with extenal components
            - infra_init: holds the code that start the infra by deploying the docker-compose at the root of the infra directory (deploys orchestrator and databases)
            - orchestrator_communication: holds the code that communciates with the orchestrator
            - sandbox_comunication: holds the code that communicates with sandboxes
        - utils: project-agnostic utilities
            - http: http utilities
    - tests:
        - integration_tests: tests pieces of code working together.
            - functional_tests: tests for functional bugs, these are the essential tests
            - performance_tests: tests the performance of pieces of code: dont need to implement now.
        - unit_tests: tests specific pieces of code in isolation
            - functional_tests: tests for functional bugs, these are the essential tests
            - performance_tests: tests the performance of pieces of code: dont need to implement now.

## Tech Stack

Python: programming language
uv: package manager
Docker: container engine
FastAPI + Uvicorn: for making http APIs
Httpx: for making http clients
Pydantic: for making data models
logging: for logging
asyncio: for aync python
Qdrant: as the vector database
Neo4j: as the graph database

## How to build it

- follow the directory structure I provided.
- make tests that allow to test each component (SDK, Orchestrator, Sandbox) in isolation, while mocking the others.
- only wirte documentation after you finished everyhting else, docuemntation is the last thing you should do.
