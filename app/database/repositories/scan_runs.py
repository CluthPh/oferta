from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import ScanRun


def list_scan_runs(session: Session, limit: int = 20) -> list[ScanRun]:
    return list(
        session.scalars(select(ScanRun).order_by(ScanRun.started_at.desc()).limit(limit)).all()
    )


def latest_scan_run(session: Session) -> ScanRun | None:
    return session.scalar(select(ScanRun).order_by(ScanRun.started_at.desc()).limit(1))
