from __future__ import annotations

import asyncio
import logging

from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.services.scheduler_service import SchedulerService
from app.workers.scan_worker import run_once

logger = logging.getLogger("worker.continuous")


async def run_continuous(settings: Settings | None = None) -> None:
    resolved = settings or get_settings()
    configure_logging(resolved.log_level, resolved.logs_dir)
    scheduler = SchedulerService()

    async def scan_job() -> None:
        logger.info(
            "scan_cycle_started dry_run=%s interval_minutes=%s",
            resolved.dry_run,
            resolved.scan_interval_minutes,
        )
        try:
            scan = await run_once(resolved)
        except Exception:
            logger.exception("scan_cycle_failed")
            return
        logger.info(
            "scan_cycle_finished collected=%s approved=%s published=%s ignored=%s errors=%s",
            scan.collected_count,
            scan.approved_count,
            scan.published_count,
            scan.ignored_count,
            scan.error_count,
        )

    print("Worker de ofertas iniciado.")
    print(f"DRY_RUN={resolved.dry_run}")
    print(f"Intervalo: {resolved.scan_interval_minutes} minuto(s)")
    print("Pressione Ctrl+C para parar.")

    if resolved.run_scan_on_startup:
        await scan_job()

    scheduler.add_interval_job(
        job_id="scan_offers",
        seconds=resolved.scan_interval_minutes * 60,
        callback=scan_job,
    )
    scheduler.start()

    try:
        while True:
            await asyncio.sleep(1)
    finally:
        scheduler.shutdown()
        logger.info("continuous_worker_stopped")
