from __future__ import annotations

from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.worker.workflow_sandbox import SandboxedWorkflowRunner

from .recovery import SyntheticRecoveryWorkflow, synthetic_recovery_shot
from .settings import WorkerSettings
from .workflows import (
    SyntheticApprovalWorkflow,
    SyntheticCancellationWorkflow,
    SyntheticControlWorkflow,
    SyntheticProviderAsyncWorkflow,
    SyntheticRetryWorkflow,
    synthetic_cancellable,
    synthetic_echo,
    synthetic_flaky,
    synthetic_provider_poll,
    synthetic_provider_submit,
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
            SyntheticProviderAsyncWorkflow,
            SyntheticRecoveryWorkflow,
        ],
        activities=[
            synthetic_echo,
            synthetic_flaky,
            synthetic_cancellable,
            synthetic_provider_submit,
            synthetic_provider_poll,
            synthetic_recovery_shot,
        ],
        workflow_runner=SandboxedWorkflowRunner(),
    )
