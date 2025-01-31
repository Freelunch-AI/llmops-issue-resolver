from fastapi import FastAPI, HTTPException

from sandbox_toolkit.helpers.schema_models.networking_schemas import (
    HostGetResourcesRequest,
    HostGetResourcesResponse,
    HostGetResourceUsageRequest,
    HostGetResourceUsageResponse,
    ResourceAdjustmentRequest,
    SandboxCreateRequest,
    SandboxCreateResponse,
    SandboxGroupStartRequest,
    SandboxGroupStartResponse,
    SandboxGroupStatusRequest,
    SandboxGroupStatusResponse,
    SandboxGroupStopRequest,
    SandboxGroupStopResponse,
    SandboxStartRequest,
    SandboxStartResponse,
    SandboxStatusRequest,
    SandboxStatusResponse,
    SandboxStopRequest,
    SandboxStopResponse,
)
from sandbox_toolkit.infra.sandbox_orchestrator.sandbox_orchestrator import (
    SandboxOrchestrator,
    adjust_allocated_resources,
    get_host_resource_usage,
    get_host_resources,
    get_sandbox_group_status,
    get_sandbox_status,
    start_sandbox_group,
    stop_sandbox_group,
)
from sandbox_toolkit.logs.logging import logger

app = FastAPI()
sandbox_orchestrator = SandboxOrchestrator()

@app.post("/create_sandbox", response_model=SandboxCreateResponse)
async def create_sandbox_endpoint(request: SandboxCreateRequest):
    logger.info("API: create_sandbox_endpoint - Start")
    logger.debug(f"API: create_sandbox_endpoint - Inputs: {request}")
    try:
        response = await sandbox_orchestrator.create_sandbox(request)
        logger.info("API: create_sandbox_endpoint - End")
        logger.debug(f"API: create_sandbox_endpoint - Outputs: {response}")
        return response
    except Exception as e:
        logger.error(f"API: create_sandbox_endpoint - Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/start_sandbox", response_model=SandboxStartResponse)
async def start_sandbox_endpoint(request: SandboxStartRequest):
    logger.info("API: start_sandbox_endpoint - Start")
    logger.debug(f"API: start_sandbox_endpoint - Inputs: {request}")
    try:
        response = await sandbox_orchestrator.start_sandbox(request)
        logger.info("API: start_sandbox_endpoint - End")
        logger.debug(f"API: start_sandbox_endpoint - Outputs: {response}")
        return response
    except Exception as e:
        logger.error(f"API: start_sandbox_endpoint - Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stop_sandbox", response_model=SandboxStopResponse)
async def stop_sandbox_endpoint(request: SandboxStopRequest):
    logger.info("API: stop_sandbox_endpoint - Start")
    logger.debug(f"API: stop_sandbox_endpoint - Inputs: {request}")
    try:
        response = await sandbox_orchestrator.stop_sandbox(request)
        logger.info("API: stop_sandbox_endpoint - End")
        logger.debug(f"API: stop_sandbox_endpoint - Outputs: {response}")
        return response
    except Exception as e:
        logger.error(f"API: stop_sandbox_endpoint - Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get_host_resources", response_model=HostGetResourcesResponse)
async def get_host_resources_endpoint(request: HostGetResourcesRequest):
    logger.info("API: get_host_resources_endpoint - Start")
    logger.debug(f"API: get_host_resources_endpoint - Inputs: {request}")
    try:
        response = get_host_resources()
        host_resources_response = HostGetResourcesResponse(host_resources=response)
        logger.info("API: get_host_resources_endpoint - End")
        logger.debug(f"API: get_host_resources_endpoint - Outputs: {host_resources_response}")
        return host_resources_response
    except Exception as e:
        logger.error(f"API: get_host_resources_endpoint - Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get_host_resource_usage", response_model=HostGetResourceUsageResponse)
async def get_host_resource_usage_endpoint(request: HostGetResourceUsageRequest):
    logger.info("API: get_host_resource_usage_endpoint - Start")
    logger.debug(f"API: get_host_resource_usage_endpoint - Inputs: {request}")
    try:
        response = get_host_resource_usage()
        host_resource_usage_response = HostGetResourceUsageResponse(host_resource_usage=response)
        logger.info("API: get_host_resource_usage_endpoint - End")
        logger.debug(f"API: get_host_resource_usage_endpoint - Outputs: {host_resource_usage_response}")
        return host_resource_usage_response
    except Exception as e:
        logger.error(f"API: get_host_resource_usage_endpoint - Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/start_sandbox_group", response_model=SandboxGroupStartResponse)
async def start_sandbox_group_endpoint(request: SandboxGroupStartRequest):
    logger.info("API: start_sandbox_group_endpoint - Start")
    logger.debug(f"API: start_sandbox_group_endpoint - Inputs: {request}")
    try:
        response = await start_sandbox_group(request)
        logger.info("API: start_sandbox_group_endpoint - End")
        logger.debug(f"API: start_sandbox_group_endpoint - Outputs: {response}")
        return response
    except Exception as e:
        logger.error(f"API: start_sandbox_group_endpoint - Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stop_sandbox_group", response_model=SandboxGroupStopResponse)
async def stop_sandbox_group_endpoint(request: SandboxGroupStopRequest):
    logger.info("API: stop_sandbox_group_endpoint - Start")
    logger.debug(f"API: stop_sandbox_group_endpoint - Inputs: {request}")
    try:
        response = await stop_sandbox_group(request)
        logger.info("API: stop_sandbox_group_endpoint - End")
        logger.debug(f"API: stop_sandbox_group_endpoint - Outputs: {response}")
        return response
    except Exception as e:
        logger.error(f"API: stop_sandbox_group_endpoint - Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/adjust_allocated_resources", response_model=SandboxGroupStopResponse) # TODO: response model?
async def adjust_allocated_resources_endpoint(request: ResourceAdjustmentRequest):
    logger.info("API: adjust_allocated_resources_endpoint - Start")
    logger.debug(f"API: adjust_allocated_resources_endpoint - Inputs: {request}")
    try:
        response = await adjust_allocated_resources(request)
        logger.info("API: adjust_allocated_resources_endpoint - End")
        logger.debug(f"API: adjust_allocated_resources_endpoint - Outputs: {response}")
        return response
    except Exception as e:
        logger.error(f"API: adjust_allocated_resources_endpoint - Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sandbox_status", response_model=SandboxStatusResponse)
async def sandbox_status_endpoint(request: SandboxStatusRequest):
    logger.info("API: sandbox_status_endpoint - Start")
    logger.debug(f"API: sandbox_status_endpoint - Inputs: {request}")
    try:
        response = await get_sandbox_status(request)
        logger.info("API: sandbox_status_endpoint - End")
        logger.debug(f"API: sandbox_status_endpoint - Outputs: {response}")
        return response
    except Exception as e:
        logger.error(f"API: sandbox_status_endpoint - Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sandbox_group_status", response_model=SandboxGroupStatusResponse)
async def sandbox_group_status_endpoint(request: SandboxGroupStatusRequest):
    logger.info("API: sandbox_group_status_endpoint - Start")
    logger.debug(f"API: sandbox_group_status_endpoint - Inputs: {request}")
    try:
        response = await get_sandbox_group_status(request)
        logger.info("API: sandbox_group_status_endpoint - End")
        logger.debug(f"API: sandbox_group_status_endpoint - Outputs: {response}")
        return response
    except Exception as e:
        logger.error(f"API: sandbox_group_status_endpoint - Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
