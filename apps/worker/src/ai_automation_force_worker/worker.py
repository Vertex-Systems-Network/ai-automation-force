from __future__ import annotations

from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.worker.workflow_sandbox import SandboxedWorkflowRunner

from .settings import WorkerSettings
from .workflows import (
    SyntheticApprovalWorkflow,
    SyntheticCancellationWorkflow,
    SyntheticControlWorkflow,
    SyntheticRetryWorkflow,
    synthetic_cancellable,
    synthetic_echo,
    synthetic_flaky,
)


def build_worker(client: Client, settings: WorkerSettings) -> Worker:
    return Worker(
        client,
        task_queue=settings.task_queue,
        workflows=[
            SyntheticControlWorkflow,
            SyntheticRetryWorkflow,
            SyntheticCancellationWorkflow,
            SyntheticApprovalWorkflow,
        ],
        activities=[synthetic_echo, synthetic_flaky, synthetic_cancellable],
        workflow_runner=SandboxedWorkflowRunner(),
    )
