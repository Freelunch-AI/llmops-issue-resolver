import asyncio
from sandbox_toolkit.infra.sandbox_orchestrator.sandbox_orchestrator import SandboxOrchestrator
from sandbox_toolkit.infra.sandbox_orchestrator.schema import StartSandboxRequest, StopSandboxRequest, GetSandboxUrlRequest, CreateSandboxRequest
from sandbox_toolkit.helpers.schema_models.internal_schemas import SandboxConfig, ComputeConfig, DatabaseConfig, ResourceUnit, Tools
from sandbox_toolkit.logs.logging import setup_logging

logger = setup_logging()

async def main():
    logger.debug("Starting example.py - Orchestrator Lifecycle Test")
    orchestrator = SandboxOrchestrator()

    sandbox_config = SandboxConfig(
        compute_config=ComputeConfig(cpu=1, ram=1, disk=10, memory_bandwidth=10, networking_bandwith=100, unit=ResourceUnit.ABSOLUTE),
        database_config=DatabaseConfig(),
        tools=Tools()
    )

    # Create sandbox
    create_request = CreateSandboxRequest(sandbox_config=sandbox_config)
    create_response = await orchestrator.create_sandbox(create_request)
    sandbox_id = create_response.sandbox_id
    sandbox_url = create_response.sandbox_url
    print(f"Create Sandbox Response: {create_response}")
    print(f"Sandbox URL: {sandbox_url}")

    # Start sandbox
    start_request = StartSandboxRequest(sandbox_id=sandbox_id)
    start_response = await orchestrator.start_sandbox(start_request)
    print(f"Start Sandbox Response: {start_response}")

    # Get sandbox URL
    get_url_request = GetSandboxUrlRequest(sandbox_id=sandbox_id)
    get_url_response = await orchestrator.get_sandbox_url(get_url_request)
    print(f"Sandbox URL Response: {get_url_response}")

    # Stop sandbox
    stop_request = StopSandboxRequest(sandbox_id=sandbox_id)
    stop_response = await orchestrator.stop_sandbox(stop_request)
    print(f"Stop Sandbox Response: {stop_response}")

if __name__ == "__main__":
    asyncio.run(main())
