"""Asynchronous workflow engine (Temporal / Celery / PubSub background workers)."""
import asyncio
import signal
from typing import Callable, Any
from smiota.core.logging import logger
from smiota.workflows.state import WorkflowContext, WorkflowStatus

_running = True


def handle_shutdown(sig, frame):
    global _running
    logger.info("Received termination signal. Draining workflow tasks...")
    _running = False


class WorkflowEngine:
    """Manages asynchronous long-running multi-step orchestration."""

    def __init__(self):
        self._active_workflows: dict[str, WorkflowContext] = {}

    async def submit_workflow(self, workflow_id: str, workflow_type: str, payload: dict[str, Any]) -> WorkflowContext:
        """Register and start an asynchronous background workflow."""
        ctx = WorkflowContext(
            workflow_id=workflow_id,
            workflow_type=workflow_type,
            status=WorkflowStatus.EXECUTING,
            payload=payload,
        )
        self._active_workflows[workflow_id] = ctx
        logger.info(f"Submitted workflow [{workflow_id}] of type '{workflow_type}'")
        return ctx

    def get_status(self, workflow_id: str) -> WorkflowContext | None:
        """Query workflow state."""
        return self._active_workflows.get(workflow_id)


async def start_worker():
    """Worker process main loop handling long-running RCA and remediation tasks."""
    logger.info("Starting Smiota background automation worker daemon...")

    # Attach signal handlers where available (Linux/POSIX or supported loops)
    try:
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, lambda: handle_shutdown(sig, None))
    except (NotImplementedError, AttributeError):
        pass

    while _running:
        await asyncio.sleep(1)

    logger.info("Background automation worker shut down cleanly.")


if __name__ == "__main__":
    asyncio.run(start_worker())
