from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import require_admin_key
from app.core.config import get_settings
from app.database.models import AffiliateLink, Publication
from app.database.repositories.affiliate_links import list_affiliate_links, upsert_affiliate_link
from app.database.repositories.posts import list_publications
from app.database.session import session_scope
from app.workers.scan_worker import run_once

router = APIRouter(tags=["jobs"])


@router.post("/jobs/scan", dependencies=[Depends(require_admin_key)])
async def scan_job() -> dict[str, object]:
    scan = await run_once(get_settings())
    return {
        "status": "finished",
        "collected": scan.collected_count,
        "approved": scan.approved_count,
        "published": scan.published_count,
        "errors": scan.error_count,
    }


@router.post("/jobs/publish", dependencies=[Depends(require_admin_key)])
async def publish_job() -> dict[str, object]:
    return await scan_job()


@router.get("/offers/pending")
def pending_offers() -> list[dict[str, object]]:
    path = get_settings().data_dir / "pending_affiliate_links.csv"
    if not path.exists():
        return []
    import csv

    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


@router.get("/publications")
def publications(limit: int = 100) -> list[dict[str, object]]:
    with session_scope() as session:
        rows: list[Publication] = list_publications(session, limit)
        return [
            {
                "id": row.id,
                "product_id": row.product_id,
                "channel_id": row.channel_id,
                "status": row.status,
                "published_price": (
                    str(row.published_price) if row.published_price is not None else None
                ),
                "link_used": row.link_used,
                "reason": row.reason,
                "published_at": row.published_at,
                "created_at": row.created_at,
                "dry_run": row.dry_run,
            }
            for row in rows
        ]


@router.post("/affiliate-links", dependencies=[Depends(require_admin_key)])
def create_affiliate_link(payload: dict[str, object]) -> dict[str, object]:
    required = {"marketplace", "product_id", "canonical_url", "affiliate_url"}
    if missing := required - payload.keys():
        raise HTTPException(
            status_code=422,
            detail=f"campos obrigatorios ausentes: {sorted(missing)}",
        )
    with session_scope() as session:
        raw_niche_id = payload.get("niche_id")
        niche_id = raw_niche_id if isinstance(raw_niche_id, int) else None
        row = upsert_affiliate_link(
            session=session,
            marketplace=str(payload["marketplace"]),
            product_id=str(payload["product_id"]),
            canonical_url=str(payload["canonical_url"]),
            affiliate_url=str(payload["affiliate_url"]),
            niche_id=niche_id,
            active=bool(payload.get("active", True)),
        )
        session.flush()
        return {"id": row.id, "status": "saved"}


@router.patch("/affiliate-links/{link_id}", dependencies=[Depends(require_admin_key)])
def update_affiliate_link(link_id: int, payload: dict[str, object]) -> dict[str, str]:
    with session_scope() as session:
        row = session.get(AffiliateLink, link_id)
        if row is None:
            raise HTTPException(status_code=404, detail="link nao encontrado")
        if "affiliate_url" in payload:
            row.affiliate_url = str(payload["affiliate_url"])
        if "active" in payload:
            row.active = bool(payload["active"])
        return {"status": "updated"}


@router.delete("/affiliate-links/{link_id}", dependencies=[Depends(require_admin_key)])
def delete_affiliate_link(link_id: int) -> dict[str, str]:
    with session_scope() as session:
        row = session.get(AffiliateLink, link_id)
        if row is None:
            raise HTTPException(status_code=404, detail="link nao encontrado")
        session.delete(row)
        return {"status": "deleted"}


@router.get("/affiliate-links")
def affiliate_links() -> list[dict[str, object]]:
    with session_scope() as session:
        return [
            {
                "id": row.id,
                "marketplace": row.marketplace,
                "product_id": row.product_id,
                "canonical_url": row.canonical_url,
                "affiliate_url": row.affiliate_url,
                "niche_id": row.niche_id,
                "active": row.active,
                "created_at": row.created_at,
                "updated_at": row.updated_at,
            }
            for row in list_affiliate_links(session)
        ]
