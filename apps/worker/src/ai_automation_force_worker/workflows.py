from __future__ import annotations

from datetime import timedelta

from temporalio import activity, workflow

SYNTHETIC_ACTIVITY_START_TO_CLOSE = timedelta(seconds=10)


@activity.defn
async def synthetic_echo(value: str) -> str:
    """Spend-free Activity proving the external-side-effect boundary."""

    return f"accepted:{value}"


@workflow.defn
class SyntheticControlWorkflow:
    """Minimal deterministic workflow used only to prove M02 durability plumbing."""

    @workflow.run
    async def run(self, value: str) -> str:
        return await workflow.execute_activity(
            synthetic_echo,
            value,
            start_to_close_timeout=SYNTHETIC_ACTIVITY_START_TO_CLOSE,
        )
