from __future__ import annotations

import csv
import io
from pathlib import Path

import yaml
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, ValidationError

from app.api.dependencies import (
    SESSION_MAX_AGE_SECONDS,
    create_admin_session_token,
    require_admin_key,
)
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.database.repositories.approvals import get_approval, list_approvals, set_approval_status
from app.database.repositories.products import get_product_by_public_id
from app.database.repositories.scan_runs import list_scan_runs
from app.database.session import session_scope
from app.marketplaces.registry import marketplace_source_status
from app.schemas.configuration import load_niches_file
from app.schemas.niche import NichesFile
from app.services.configuration_service import ConfigurationService
from app.services.dashboard_service import DashboardService, tail_text_file
from app.services.env_service import EnvService
from app.services.preview_service import PreviewService
from app.services.publish_now_service import PublishNowService
from app.services.reporting_service import ReportingService
from app.services.telegram_diagnostic_service import TelegramDiagnosticService
from app.services.validation_service import ValidationService

router = APIRouter(tags=["admin"])


class ConfigUpdatePayload(BaseModel):
    content: str


class PreviewRequest(BaseModel):
    product_id: str
    niche: str | None = None


class PublishRequest(BaseModel):
    product_id: str
    niche: str | None = None
    force: bool = True


class ApprovalUpdatePayload(BaseModel):
    note: str = ""


class LoginPayload(BaseModel):
    admin_key: str


class TelegramTestPayload(BaseModel):
    chat_id: str | None = None


@router.get("/admin", response_class=HTMLResponse)
def admin_page() -> HTMLResponse:
    path = Path(__file__).resolve().parents[1] / "static" / "admin.html"
    return HTMLResponse(path.read_text(encoding="utf-8"))


@router.post("/auth/login")
def login(payload: LoginPayload, response: Response) -> dict[str, str]:
    settings = get_settings()
    if not settings.admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ADMIN_API_KEY nao configurada",
        )
    if payload.admin_key != settings.admin_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="chave invalida")
    response.set_cookie(
        "admin_session",
        create_admin_session_token(),
        max_age=SESSION_MAX_AGE_SECONDS,
        httponly=True,
        samesite="lax",
    )
    return {"status": "authenticated"}


@router.post("/auth/logout")
def logout(response: Response) -> dict[str, str]:
    response.delete_cookie("admin_session")
    return {"status": "logged_out"}


@router.get("/auth/status", dependencies=[Depends(require_admin_key)])
def auth_status() -> dict[str, bool]:
    return {"authenticated": True}


@router.get("/dashboard")
def dashboard() -> dict[str, object]:
    settings = get_settings()
    with session_scope() as session:
        return DashboardService(settings).build(session)


@router.get("/config/validate")
def validate_config() -> dict[str, object]:
    return ValidationService(get_settings()).validate()


@router.get("/config/raw", dependencies=[Depends(require_admin_key)])
def raw_config() -> dict[str, object]:
    path = get_settings().niches_config_path
    if not path.exists():
        raise HTTPException(status_code=404, detail="arquivo de nichos nao encontrado")
    return {"path": str(path), "content": path.read_text(encoding="utf-8")}


@router.get("/config/niches", dependencies=[Depends(require_admin_key)])
def config_niches() -> dict[str, object]:
    config = load_niches_file(get_settings().niches_config_path)
    return config.model_dump(mode="json")


@router.put("/config/niches", dependencies=[Depends(require_admin_key)])
def update_config_niches(payload: dict[str, object]) -> dict[str, object]:
    settings = get_settings()
    try:
        config = NichesFile.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    content = yaml.safe_dump(config.model_dump(mode="json"), sort_keys=False, allow_unicode=True)
    path = settings.niches_config_path
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.with_suffix(path.suffix + ".bak").write_text(
            path.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    path.write_text(content, encoding="utf-8")
    with session_scope() as session:
        ConfigurationService(path).sync_database(session, config)
    return {"status": "saved", "path": str(path)}


@router.put("/config/raw", dependencies=[Depends(require_admin_key)])
def update_raw_config(payload: ConfigUpdatePayload) -> dict[str, object]:
    settings = get_settings()
    try:
        raw = yaml.safe_load(payload.content)
        config = NichesFile.model_validate(raw)
    except (yaml.YAMLError, ValidationError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    path = settings.niches_config_path
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        backup = path.with_suffix(path.suffix + ".bak")
        backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    path.write_text(payload.content, encoding="utf-8")
    with session_scope() as session:
        ConfigurationService(path).sync_database(session, config)
    return {"status": "saved", "path": str(path)}


@router.get("/settings/runtime", dependencies=[Depends(require_admin_key)])
def runtime_settings() -> dict[str, object]:
    return EnvService().summary(get_settings())


@router.get("/sources")
def sources() -> list[dict[str, object]]:
    return marketplace_source_status(get_settings().marketplace_sources)


@router.patch("/settings/runtime", dependencies=[Depends(require_admin_key)])
def update_runtime_settings(payload: dict[str, object]) -> dict[str, object]:
    updated = EnvService().update(payload)
    return {"status": "saved", "updated": updated, "current": EnvService().summary(get_settings())}


@router.get("/scan-runs")
def scan_runs(limit: int = 20) -> list[dict[str, object]]:
    with session_scope() as session:
        return [
            {
                "id": row.id,
                "started_at": row.started_at,
                "finished_at": row.finished_at,
                "collected_count": row.collected_count,
                "approved_count": row.approved_count,
                "published_count": row.published_count,
                "ignored_count": row.ignored_count,
                "error_count": row.error_count,
                "error_message": row.error_message,
            }
            for row in list_scan_runs(session, limit)
        ]


@router.get("/approvals", dependencies=[Depends(require_admin_key)])
def approvals(status: str | None = None, limit: int = 100) -> list[dict[str, object]]:
    with session_scope() as session:
        return [
            {
                "id": row.id,
                "marketplace": row.marketplace,
                "product_id": row.product_id,
                "niche_name": row.niche_name,
                "search_query": row.search_query,
                "score": row.score,
                "reason": row.reason,
                "status": row.status,
                "note": row.note,
                "created_at": row.created_at,
                "updated_at": row.updated_at,
                "decided_at": row.decided_at,
                "published_at": row.published_at,
            }
            for row in list_approvals(session, status, limit)
        ]


@router.post("/approvals/{approval_id}/approve", dependencies=[Depends(require_admin_key)])
def approve_offer(approval_id: int, payload: ApprovalUpdatePayload) -> dict[str, object]:
    with session_scope() as session:
        row = set_approval_status(session, approval_id, "approved", payload.note)
        if row is None:
            raise HTTPException(status_code=404, detail="aprovacao nao encontrada")
        return {"status": row.status, "id": row.id}


@router.post("/approvals/{approval_id}/reject", dependencies=[Depends(require_admin_key)])
def reject_offer(approval_id: int, payload: ApprovalUpdatePayload) -> dict[str, object]:
    with session_scope() as session:
        row = set_approval_status(session, approval_id, "rejected", payload.note)
        if row is None:
            raise HTTPException(status_code=404, detail="aprovacao nao encontrada")
        return {"status": row.status, "id": row.id}


@router.post("/approvals/{approval_id}/publish", dependencies=[Depends(require_admin_key)])
async def publish_approval(approval_id: int) -> dict[str, object]:
    with session_scope() as session:
        approval = get_approval(session, approval_id)
        if approval is None:
            raise HTTPException(status_code=404, detail="aprovacao nao encontrada")
        product = get_product_by_public_id(session, approval.product_id)
        if product is None:
            raise HTTPException(status_code=404, detail="produto nao encontrado")
        set_approval_status(session, approval_id, "approved", "publicacao manual")
        return await PublishNowService(get_settings()).publish(
            session,
            product,
            approval.niche_name,
            force=True,
        )


@router.get("/logs/recent", dependencies=[Depends(require_admin_key)])
def recent_logs(kind: str = "application", lines: int = 120) -> dict[str, object]:
    if kind not in {"application", "errors"}:
        raise HTTPException(status_code=422, detail="kind deve ser application ou errors")
    safe_lines = max(1, min(lines, 500))
    path = get_settings().logs_dir / f"{kind}.log"
    return {"path": str(path), "lines": tail_text_file(path, safe_lines)}


@router.post("/offers/preview", dependencies=[Depends(require_admin_key)])
def preview_offer(payload: PreviewRequest) -> dict[str, object]:
    try:
        with session_scope() as session:
            product = get_product_by_public_id(session, payload.product_id)
            if product is None:
                raise HTTPException(status_code=404, detail="produto nao encontrado")
            return PreviewService(get_settings()).preview(session, product, payload.niche)
    except AppError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/offers/publish-now", dependencies=[Depends(require_admin_key)])
async def publish_now(payload: PublishRequest) -> dict[str, object]:
    with session_scope() as session:
        product = get_product_by_public_id(session, payload.product_id)
        if product is None:
            raise HTTPException(status_code=404, detail="produto nao encontrado")
        return await PublishNowService(get_settings()).publish(
            session,
            product,
            payload.niche,
            payload.force,
        )


@router.get("/reports/daily", dependencies=[Depends(require_admin_key)])
def daily_report() -> dict[str, object]:
    with session_scope() as session:
        return ReportingService().build_daily_report(session)


@router.post("/telegram/test", dependencies=[Depends(require_admin_key)])
async def telegram_test(payload: TelegramTestPayload) -> dict[str, object]:
    try:
        return await TelegramDiagnosticService(get_settings()).test(payload.chat_id)
    except AppError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/affiliate-links/export", dependencies=[Depends(require_admin_key)])
def export_affiliate_links() -> Response:
    from app.database.repositories.affiliate_links import list_affiliate_links

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "marketplace",
            "product_id",
            "canonical_url",
            "affiliate_url",
            "niche_id",
            "active",
        ],
    )
    writer.writeheader()
    with session_scope() as session:
        for row in list_affiliate_links(session):
            writer.writerow(
                {
                    "marketplace": row.marketplace,
                    "product_id": row.product_id,
                    "canonical_url": row.canonical_url,
                    "affiliate_url": row.affiliate_url,
                    "niche_id": row.niche_id or "",
                    "active": str(row.active).lower(),
                }
            )
    return Response(
        output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="affiliate_links.csv"'},
    )


@router.post("/affiliate-links/import", dependencies=[Depends(require_admin_key)])
def import_affiliate_links(payload: dict[str, str]) -> dict[str, object]:
    from app.database.repositories.affiliate_links import upsert_affiliate_link

    content = payload.get("csv", "")
    if not content.strip():
        raise HTTPException(status_code=422, detail="campo csv vazio")
    imported = 0
    with session_scope() as session:
        for row in csv.DictReader(io.StringIO(content)):
            if not row.get("product_id") or not row.get("affiliate_url"):
                continue
            raw_niche_id = (row.get("niche_id") or "").strip()
            niche_id = int(raw_niche_id) if raw_niche_id.isdigit() else None
            upsert_affiliate_link(
                session=session,
                marketplace=row.get("marketplace") or "mercadolivre",
                product_id=row["product_id"],
                canonical_url=row.get("canonical_url") or "",
                affiliate_url=row["affiliate_url"],
                niche_id=niche_id,
                active=(row.get("active") or "true").lower() in {"1", "true", "yes", "sim"},
            )
            imported += 1
    return {"status": "imported", "count": imported}
