from __future__ import annotations

from app.core.config import Settings
from app.workers.scan_worker import run_once


async def publish_pending(settings: Settings) -> None:
    await run_once(settings)

