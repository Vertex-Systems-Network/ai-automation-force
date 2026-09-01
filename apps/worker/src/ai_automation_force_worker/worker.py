from __future__ import annotations

from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.worker.workflow_sandbox import SandboxedWorkflowRunner

from .media_probe import media_probe_quarantine
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
    # Derivative rendering pulls in filesystem/process-backed dependencies that must
    # never be imported while Temporal re-imports this package inside its workflow
    # sandbox. Resolve the activity only at worker construction time, outside the
    # deterministic workflow import boundary.
    from .derivative_render import render_media_derivative

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
            media_probe_quarantine,
            render_media_derivative,
        ],
        workflow_runner=SandboxedWorkflowRunner(),
    )
