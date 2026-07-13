from fastapi import APIRouter

from app.core.config import get_settings
from app.database.session import check_database
from app.schemas.configuration import load_niches_file

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def ready() -> dict[str, object]:
    settings = get_settings()
    checks: dict[str, bool] = {
        "database": False,
        "configuration": False,
        "telegram": settings.dry_run or bool(settings.telegram_bot_token),
        "scheduler": True,
    }
    try:
        checks["database"] = check_database()
    except Exception:
        checks["database"] = False
    try:
        load_niches_file(settings.niches_config_path)
        checks["configuration"] = True
    except Exception:
        checks["configuration"] = False
    return {"ready": all(checks.values()), "checks": checks}


@router.get("/metrics/summary")
def metrics_summary() -> dict[str, object]:
    from sqlalchemy import func, select

    from app.database.models import Product, Publication, ScanRun
    from app.database.session import session_scope

    with session_scope() as session:
        return {
            "products": session.scalar(select(func.count()).select_from(Product)),
            "publications": session.scalar(select(func.count()).select_from(Publication)),
            "scan_runs": session.scalar(select(func.count()).select_from(ScanRun)),
        }

