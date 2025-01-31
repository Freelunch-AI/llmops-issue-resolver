from typing import List
from sandbox_toolkit.helpers.schema_models.schema import ActionExecutionRequest, Observation, SandboxCapabilities, SandboxResourceUsage, SandboxStats, ActionsObservationsPair, ToolAPIReference
from sandbox_toolkit.helpers.schema_models.internal_schema import *

class SandboxClient:
    def __init__(self, sandbox_url: str):
        self.sandbox_url = sandbox_url

    async def send_actions(self, actions: ActionExecutionRequest) -> List[Observation]:
        request = SendActionsRequest(actions=actions)
        # Simulate response
        observations_list = []
        for function_name, action_details in actions.actions.items():
            if function_name == "execute_command":
                observations_list.append(Observation(function_name="execute_command", terminal_output="""total 0
drwxr-xr-x 1 root root 4096 Jun 20 15:57 .
drwxr-xr-x 1 root root 4096 Jun 20 15:57 ..
-rw-r--r-- 1 root root    0 Jun 20 15:57 file1.txt
-rw-r--r-- 1 root root    0 Jun 20 15:57 file2.txt
drwxr-xr-x 2 root root 4096 Jun 20 15:57 subdir
""", process_still_running=False)) # Simulate execute_command output
            elif function_name == "greet_tool":
                observations_list.append(Observation(function_name="greet_tool", terminal_output=f"Simulating greet_tool: Hello, {action_details['args']['name']}!", process_still_running=False)) # Simulate greet_tool output
            else:
                observations_list.append(Observation(function_name=function_name, terminal_output="Tool output not simulated yet.", process_still_running=False)) # Placeholder for other tools

        response = SendActionsResponse(observations=observations_list)
        return response.observations

    async def get_capabilities(self) -> SandboxCapabilities:
        request = GetCapabilitiesRequest()
        # Simulate response
        response = GetCapabilitiesResponse(available_tools=[
            ToolAPIReference(
                function_name="execute_command",
                signature="execute_command(command: str) -> str",
                description="Execute a terminal command inside the sandbox."
            )
        ]) # Simulate available tools
        return response

    async def get_resource_usage(self) -> SandboxResourceUsage:
        request = GetResourceUsageRequest()
        # Simulate response
        response = SandboxResourceUsage(
            sandbox_name="test_sandbox",
            sandbox_id="test_sandbox_id",
            cpu_usage=0.1,
            ram_usage=0.2,
            disk_usage=0.3,
            memory_bandwidth_usage=0.4,
            networking_bandwith_usage=0.5
        ) # Simulate sandbox resource usage
        return response

    async def get_stats(self) -> SandboxStats:
        request = GetStatsRequest()
        # Simulate response
        response = GetStatsResponse(sandbox_running_duration=10.0, actions_sent_count=1) # Replace with actual stats if needed
        return response

    async def get_history(self) -> List[ActionsObservationsPair]:
        request = GetHistoryRequest()
        # Simulate response
        response = GetHistoryResponse(history=[
            ActionsObservationsPair(
                actions=ActionExecutionRequest(actions={
                    "execute_command": {
                        "function_call_explanation": "List files in the sandbox",
                        "args": {
                            "command": "ls -la"
                        }
                    }
                }),
                observations=[
                    Observation(function_name="execute_command", terminal_output="ls -la output", process_still_running=False)
                ]
            )
        ]) # Replace with actual history if needed
        return response.history

    async def close(self):
        pass # No need to close client in simulation