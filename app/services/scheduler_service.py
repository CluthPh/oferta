from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import cast

from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore[import-untyped]

logger = logging.getLogger("service.scheduler")


class SchedulerService:
    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()
        self._locks: dict[str, asyncio.Lock] = {}

    def add_interval_job(
        self,
        job_id: str,
        seconds: int,
        callback: Callable[[], Awaitable[None]],
    ) -> None:
        self._locks[job_id] = asyncio.Lock()

        async def locked_callback() -> None:
            lock = self._locks[job_id]
            if lock.locked():
                logger.info("job_skipped_already_running job=%s", job_id)
                return
            async with lock:
                await callback()

        self.scheduler.add_job(locked_callback, "interval", seconds=seconds, id=job_id)

    def start(self) -> None:
        self.scheduler.start()

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    def running(self) -> bool:
        return cast("bool", self.scheduler.running)
