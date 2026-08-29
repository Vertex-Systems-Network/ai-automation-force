from __future__ import annotations

import asyncio

from .client import connect_temporal
from .settings import load_worker_settings
from .worker import build_worker


async def run_worker() -> None:
    settings = load_worker_settings()
    client = await connect_temporal(settings)
    worker = build_worker(client, settings)
    await worker.run()


def main() -> None:
    asyncio.run(run_worker())


if __name__ == "__main__":
    main()
