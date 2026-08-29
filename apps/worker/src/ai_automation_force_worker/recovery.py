from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import Any

from temporalio import activity, workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ApplicationError

RECOVERY_ACTIVITY_START_TO_CLOSE = timedelta(seconds=5)
RECOVERY_ACTIVITY_SCHEDULE_TO_CLOSE = timedelta(seconds=20)
RECOVERY_MAX_SHOTS = 1000
RECOVERY_INPUT_KEYS = frozenset(
    {
        "project_key",
        "shot_count",
        "fail_first_indexes",
        "approval_after",
        "expected_approval_revision",
        "completed_results",
        "approval_received",
        "seen_signal_keys",
    }
)


@activity.defn
async def synthetic_recovery_shot(payload: dict[str, Any]) -> dict[str, Any]:
    """Spend-free shot Activity with deterministic retry injection and stable terminal identity."""

    shot_index = int(payload["shot_index"])
    project_key = str(payload["project_key"]).strip()
    fail_first = bool(payload["fail_first"])
    if not project_key:
        raise ApplicationError(
            "project key is blank",
            type="SyntheticRecoveryInput",
            non_retryable=True,
        )
    if shot_index < 0:
        raise ApplicationError(
            "shot index must be non-negative",
            type="SyntheticRecoveryInput",
            non_retryable=True,
        )
    attempt = activity.info().attempt
    if fail_first and attempt == 1:
        raise ApplicationError(
            f"synthetic recovery retry for shot {shot_index}",
            type="SyntheticRecoveryTransient",
        )
    await asyncio.sleep(0.01)
    return {
        "shot_index": shot_index,
        "terminal_key": f"{project_key}:shot:{shot_index:03d}:terminal",
        "activity_attempt": attempt,
    }


@workflow.defn
class SyntheticRecoveryWorkflow:
    """Synthetic M02 exit workflow proving fan-out, pause, retry, restart and replay durability."""

    def __init__(self) -> None:
        self._project_key = ""
        self._shot_count = 0
        self._approval_after = 0
        self._expected_approval_revision = 1
        self._approval_received = False
        self._waiting_for_approval = False
        self._seen_signal_keys: set[str] = set()
        self._completed: dict[int, dict[str, Any]] = {}

    @workflow.signal
    def approve(self, payload: dict[str, Any]) -> None:
        signal_key = str(payload.get("signal_key", "")).strip()
        if not signal_key or signal_key in self._seen_signal_keys:
            return
        self._seen_signal_keys.add(signal_key)
        revision = int(payload.get("request_revision", 0))
        decision = str(payload.get("decision", "")).strip()
        if revision != self._expected_approval_revision or decision != "approved":
            return
        self._approval_received = True

    @workflow.query
    def progress(self) -> dict[str, Any]:
        return {
            "project_key": self._project_key,
            "shot_count": self._shot_count,
            "completed_count": len(self._completed),
            "waiting_for_approval": self._waiting_for_approval,
            "approval_received": self._approval_received,
        }

    def _restore(self, input: dict[str, Any]) -> tuple[list[int], int]:
        unknown = set(input) - RECOVERY_INPUT_KEYS
        if unknown:
            raise ApplicationError(
                f"unknown recovery input keys: {', '.join(sorted(unknown))}",
                type="SyntheticRecoveryInput",
                non_retryable=True,
            )
        self._project_key = str(input.get("project_key", "")).strip()
        self._shot_count = int(input.get("shot_count", 0))
        self._approval_after = int(input.get("approval_after", self._shot_count // 2))
        self._expected_approval_revision = int(input.get("expected_approval_revision", 1))
        if not self._project_key:
            raise ApplicationError(
                "project_key is required",
                type="SyntheticRecoveryInput",
                non_retryable=True,
            )
        if not 1 <= self._shot_count <= RECOVERY_MAX_SHOTS:
            raise ApplicationError(
                f"shot_count must be between 1 and {RECOVERY_MAX_SHOTS}",
                type="SyntheticRecoveryInput",
                non_retryable=True,
            )
        if not 0 <= self._approval_after <= self._shot_count:
            raise ApplicationError(
                "approval_after must be within shot_count",
                type="SyntheticRecoveryInput",
                non_retryable=True,
            )
        fail_first_indexes = sorted({int(value) for value in input.get("fail_first_indexes", [])})
        if any(value < 0 or value >= self._shot_count for value in fail_first_indexes):
            raise ApplicationError(
                "fail_first_indexes contains an out-of-range shot",
                type="SyntheticRecoveryInput",
                non_retryable=True,
            )
        completed_results = input.get("completed_results", [])
        if not isinstance(completed_results, list):
            raise ApplicationError(
                "completed_results must be a list",
                type="SyntheticRecoveryInput",
                non_retryable=True,
            )
        for item in completed_results:
            if not isinstance(item, dict):
                raise ApplicationError(
                    "completed_results contains a non-object",
                    type="SyntheticRecoveryInput",
                    non_retryable=True,
                )
            shot_index = int(item["shot_index"])
            if shot_index in self._completed:
                raise ApplicationError(
                    f"duplicate completed shot {shot_index}",
                    type="SyntheticRecoveryDuplicate",
                    non_retryable=True,
                )
            self._completed[shot_index] = dict(item)
        self._approval_received = bool(input.get("approval_received", False))
        self._seen_signal_keys = {str(value) for value in input.get("seen_signal_keys", [])}
        return fail_first_indexes, self._approval_after

    async def _fan_out(self, indexes: list[int], fail_first: set[int]) -> None:
        pending = [index for index in indexes if index not in self._completed]
        if not pending:
            return
        tasks = [
            workflow.execute_activity(
                synthetic_recovery_shot,
                {
                    "project_key": self._project_key,
                    "shot_index": index,
                    "fail_first": index in fail_first,
                },
                schedule_to_close_timeout=RECOVERY_ACTIVITY_SCHEDULE_TO_CLOSE,
                start_to_close_timeout=RECOVERY_ACTIVITY_START_TO_CLOSE,
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(milliseconds=50),
                    backoff_coefficient=2.0,
                    maximum_interval=timedelta(milliseconds=200),
                    maximum_attempts=3,
                    non_retryable_error_types=["SyntheticRecoveryInput"],
                ),
            )
            for index in pending
        ]
        results = await asyncio.gather(*tasks)
        for result in results:
            shot_index = int(result["shot_index"])
            if shot_index in self._completed:
                raise ApplicationError(
                    f"duplicate terminal result for shot {shot_index}",
                    type="SyntheticRecoveryDuplicate",
                    non_retryable=True,
                )
            self._completed[shot_index] = dict(result)

    def _continue_as_new_if_suggested(
        self,
        fail_first_indexes: list[int],
    ) -> None:
        if not workflow.info().is_continue_as_new_suggested():
            return
        workflow.continue_as_new(
            {
                "project_key": self._project_key,
                "shot_count": self._shot_count,
                "fail_first_indexes": fail_first_indexes,
                "approval_after": self._approval_after,
                "expected_approval_revision": self._expected_approval_revision,
                "completed_results": [self._completed[index] for index in sorted(self._completed)],
                "approval_received": self._approval_received,
                "seen_signal_keys": sorted(self._seen_signal_keys),
            }
        )

    @workflow.run
    async def run(self, input: dict[str, Any]) -> dict[str, Any]:
        fail_first_indexes, approval_after = self._restore(input)
        fail_first = set(fail_first_indexes)
        first_batch = list(range(0, approval_after))
        second_batch = list(range(approval_after, self._shot_count))

        await self._fan_out(first_batch, fail_first)
        self._continue_as_new_if_suggested(fail_first_indexes)

        if approval_after < self._shot_count and not self._approval_received:
            self._waiting_for_approval = True
            await workflow.wait_condition(lambda: self._approval_received)
            self._waiting_for_approval = False

        self._continue_as_new_if_suggested(fail_first_indexes)
        await self._fan_out(second_batch, fail_first)
        self._continue_as_new_if_suggested(fail_first_indexes)

        completed = [self._completed[index] for index in sorted(self._completed)]
        if len(completed) != self._shot_count:
            raise ApplicationError(
                f"completed {len(completed)} of {self._shot_count} shots",
                type="SyntheticRecoveryIncomplete",
                non_retryable=True,
            )
        terminal_keys = [str(item["terminal_key"]) for item in completed]
        if len(set(terminal_keys)) != self._shot_count:
            raise ApplicationError(
                "duplicate terminal side-effect identity detected",
                type="SyntheticRecoveryDuplicate",
                non_retryable=True,
            )
        return {
            "project_key": self._project_key,
            "shot_count": self._shot_count,
            "completed_count": len(completed),
            "terminal_keys": terminal_keys,
            "retried_shots": [
                int(item["shot_index"])
                for item in completed
                if int(item["activity_attempt"]) > 1
            ],
            "history_length": workflow.info().get_current_history_length(),
            "continue_as_new_suggested": workflow.info().is_continue_as_new_suggested(),
        }
