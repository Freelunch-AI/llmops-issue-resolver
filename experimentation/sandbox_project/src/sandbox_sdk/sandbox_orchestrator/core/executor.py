from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from sandbox_sdk.sandbox_orchestrator.core.models.executor_models import (
    ExecutorConfig,
    ExecutorResponse,
    ExecutorStatus,
)


class ExecutorBase(ABC):
    """Base class for all executors."""

    def __init__(self, config: ExecutorConfig):
        self.config = config
        self._status = ExecutorStatus.NOT_STARTED

    @property
    def status(self) -> ExecutorStatus:
        """Get the current status of the executor."""
        return self._status

    @abstractmethod
    def execute(self, **kwargs) -> ExecutorResponse:
        """Execute the task."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop the execution."""
        pass


class LocalExecutor(ExecutorBase):
    """Executor for running tasks locally."""

    def execute(self, **kwargs) -> ExecutorResponse:
        self._status = ExecutorStatus.RUNNING
        try:
            # Implementation for local execution
            result: Dict[str, Any] = {"message": "Local execution completed"}
            self._status = ExecutorStatus.COMPLETED
            return ExecutorResponse(status=self._status, result=result)
        except Exception as e:
            self._status = ExecutorStatus.FAILED
            return ExecutorResponse(
                status=self._status,
                result={"error": str(e)},
            )

    def stop(self) -> None:
        if self._status == ExecutorStatus.RUNNING:
            self._status = ExecutorStatus.STOPPED


class RemoteExecutor(ExecutorBase):
    """Executor for running tasks remotely."""

    def execute(self, **kwargs) -> ExecutorResponse:
        self._status = ExecutorStatus.RUNNING
        try:
            # Implementation for remote execution
            result: Dict[str, Any] = {"message": "Remote execution completed"}
            self._status = ExecutorStatus.COMPLETED
            return ExecutorResponse(status=self._status, result=result)
        except Exception as e:
            self._status = ExecutorStatus.FAILED
            return ExecutorResponse(
                status=self._status,
                result={"error": str(e)},
            )

    def stop(self) -> None:
        if self._status == ExecutorStatus.RUNNING:
            self._status = ExecutorStatus.STOPPED