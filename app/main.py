from __future__ import annotations

import argparse
import asyncio
import logging
import signal
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes_admin import router as admin_router
from app.api.routes_channels import router as channels_router
from app.api.routes_health import router as health_router
from app.api.routes_jobs import router as jobs_router
from app.api.routes_products import router as products_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.database.session import configure_session, init_db
from app.workers.continuous_worker import run_continuous
from app.workers.scan_worker import run_once

logger = logging.getLogger("app.main")


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level, settings.logs_dir)
    configure_session(settings)
    init_db()
    app = FastAPI(title="Oferta Telegram", version="0.1.0")
    app.include_router(health_router)
    app.include_router(admin_router)
    app.include_router(products_router)
    app.include_router(channels_router)
    app.include_router(jobs_router)
    static_dir = Path(__file__).resolve().parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
    return app


app = create_app()


def install_signal_handlers() -> None:
    def handle_signal(signum: int, _frame: object) -> None:
        logger.info("shutdown_requested signal=%s", signum)
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)


def main_cli() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        nargs="?",
        default="serve",
        choices=["serve", "run-once", "worker"],
    )
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    settings = get_settings()
    configure_logging(settings.log_level, settings.logs_dir)
    install_signal_handlers()
    if args.command == "run-once":
        asyncio.run(run_once(settings))
        return
    if args.command == "worker":
        try:
            asyncio.run(run_continuous(settings))
        except KeyboardInterrupt:
            logger.info("worker_interrupted")
        return
    uvicorn.run("app.main:app", host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main_cli()
