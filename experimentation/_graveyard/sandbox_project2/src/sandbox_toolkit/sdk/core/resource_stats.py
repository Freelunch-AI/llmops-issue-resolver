from sandbox_toolkit.sdk.orchestrator_communication.orchestrator_communication import OrchestratorClient
from sandbox_toolkit.helpers.schema_models.schema import TotalComputeResourceStats

ORCHESTRATOR_URL = "http://localhost:8000" # TODO: Make configurable
orchestrator_client = OrchestratorClient(ORCHESTRATOR_URL)

async def get_total_resource_stats() -> TotalComputeResourceStats:
    """Returns the total compute resource stats for the machine."""
    return await orchestrator_client.get_total_resource_stats()