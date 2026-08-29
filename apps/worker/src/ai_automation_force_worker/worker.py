from __future__ import annotations

from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.worker.workflow_sandbox import SandboxedWorkflowRunner

from .settings import WorkerSettings
from .workflows import SyntheticControlWorkflow, synthetic_echo


def build_worker(client: Client, settings: WorkerSettings) -> Worker:
    return Worker(
        client,
        task_queue=settings.task_queue,
        workflows=[SyntheticControlWorkflow],
        activities=[synthetic_echo],
        workflow_runner=SandboxedWorkflowRunner(),
    )
