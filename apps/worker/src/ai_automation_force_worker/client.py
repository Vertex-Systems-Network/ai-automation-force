from __future__ import annotations

from temporalio.client import Client

from .settings import WorkerSettings


async def connect_temporal(settings: WorkerSettings) -> Client:
    return await Client.connect(
        settings.temporal_target,
        namespace=settings.temporal_namespace,
    )
