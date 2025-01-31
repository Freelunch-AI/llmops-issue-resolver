from sandbox_toolkit.helpers.schema_models.schema import SandboxConfig, SandboxCapabilities, SandboxResourceUsage, SandboxStats, ComputeResourceStats, TotalResourceUsage, TotalResources, TotalSandboxResources, SandboxComputeResourceStats, TotalComputeResourceStats, ToolAPIReference, ActionExecutionRequest, Observation, ActionsObservationsPair
from sandbox_toolkit.helpers.schema_models.internal_schema import *
import httpx

class OrchestratorClient:
    def __init__(self, orchestrator_url: str):
        self.orchestrator_url = orchestrator_url
        self.client = httpx.AsyncClient()

    async def create_sandbox(self, sandbox_config: SandboxConfig) -> str: # Returns sandbox_id
        request = SandboxCreateRequest(sandbox_config=sandbox_config)
        # Simulate response
        response = SandboxCreateResponse(sandbox_id="test_sandbox_id", sandbox_url="http://localhost:5000") 
        return response.sandbox_id

    async def start_sandbox(self, sandbox_id: str):
        request = SandboxStartRequest(sandbox_id=sandbox_id)
        # Simulate response
        response = SandboxStartResponse()

    async def stop_sandbox(self, sandbox_id: str):
        request = SandboxStopRequest(sandbox_id=sandbox_id)
        # Simulate response
        response = SandboxStopResponse()
    
    async def get_sandbox_url(self, sandbox_id: str) -> str: # Returns sandbox_url
        request = SandboxGetUrlRequest(sandbox_id=sandbox_id)
        # Simulate response
        response = SandboxGetUrlResponse(sandbox_url="http://localhost:5000")
        return response.sandbox_url

    async def get_sandbox_capabilities(self, sandbox_id: str) -> SandboxCapabilities:
        request = SandboxGetCapabilitiesRequest(sandbox_id=sandbox_id)
        # Simulate response
        response = SandboxGetCapabilitiesResponse(available_tools=[]) # Replace with actual capabilities if needed
        return response

    async def get_sandbox_resource_usage(self, sandbox_id: str) -> SandboxComputeResourceStats:
        request = SandboxGetResourceUsageRequest(sandbox_id=sandbox_id)
        # Simulate response
        response = SandboxComputeResourceStats(
            sandbox_name="test_sandbox",
            sandbox_id="test_sandbox_id",
            cpu_usage=0.1,
            cpu_unit="CPU %",
            ram_usage=0.2,
            ram_unit="GB",
            disk_usage=0.3,
            disk_unit="GB",
            memory_bandwidth_usage=0.4,
            memory_bandwidth_unit="Gbps",
            networking_bandwith_usage=0.5,
            networking_bandwith_unit="Gbps"
        ) # Simulate SandboxComputeResourceStats response
        return response

    async def get_sandbox_stats(self, sandbox_id: str) -> SandboxStats:
        request = SandboxGetStatsRequest(sandbox_id=sandbox_id)
        # Simulate response
        response = SandboxGetStatsResponse(sandbox_running_duration=10.0, actions_sent_count=5) # Replace with actual stats if needed
        return response

    async def get_total_resource_stats(self) -> TotalComputeResourceStats:
        request = GetTotalResourceStatsRequest()
        # Simulate response
        response = TotalComputeResourceStats(
            total_resource_usage=TotalResourceUsage(
                cpu_usage=0.25,
                cpu_unit="CPU %",
                ram_usage=0.25,
                ram_unit="GB",
                disk_usage=0.3,
                disk_unit="GB",
                memory_bandwidth_usage=0.1,
                memory_bandwidth_unit="Gbps",
                networking_bandwith_usage=0.2,
                networking_bandwith_unit="Gbps"
            ),
            total_resources=TotalResources(
                cpu_total=4,
                cpu_unit="CPU cores",
                ram_total=8,
                ram_unit="GB",
                disk_total=100,
                disk_unit="GB",
                memory_bandwidth_total=100,
                memory_bandwidth_unit="Gbps",
                networking_bandwith_total=1000,
                networking_bandwith_unit="Gbps"
            ),
            total_sandbox_resources=TotalSandboxResources(
                cpu_allocated=2,
                cpu_unit="CPU cores",
                ram_allocated=3,
                ram_unit="GB",
                disk_allocated=50,
                disk_unit="GB",
                memory_bandwidth_allocated=50,
                memory_bandwidth_unit="Gbps",
                networking_bandwith_allocated=500,
                networking_bandwith_unit="Gbps"
            ),
            sandbox_resource_usage={} # Empty for total stats
        ) # Simulate TotalComputeResourceStats response
        return response

    async def close(self):
        await self.client.aclose()
