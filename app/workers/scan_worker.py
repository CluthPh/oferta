from __future__ import annotations

import logging
from datetime import UTC, datetime

from app.affiliates.database_provider import DatabaseAffiliateLinkProvider
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.database.models import ScanRun
from app.database.repositories.approvals import mark_product_published, upsert_pending_approval
from app.database.repositories.events import record_event
from app.database.session import configure_session, init_db, session_scope
from app.marketplaces.mercadolivre import MercadoLivreApiProvider, MercadoLivreWebProvider
from app.schemas.niche import ManualProductConfig, SearchConfig
from app.services.configuration_service import ConfigurationService
from app.services.discovery_service import DiscoveryService
from app.services.offer_service import OfferService
from app.services.product_service import ProductService
from app.services.publication_service import PublicationService
from app.telegram.client import TelegramClient
from app.telegram.publisher import TelegramPublisher

logger = logging.getLogger("worker.scan")


async def run_once(settings: Settings | None = None) -> ScanRun:
    resolved = settings or get_settings()
    configure_logging(resolved.log_level, resolved.logs_dir)
    configure_session(resolved)
    init_db()

    config_service = ConfigurationService(resolved.niches_config_path)
    niches_file = config_service.load()
    affiliate_provider = DatabaseAffiliateLinkProvider(
        resolved.data_dir / "pending_affiliate_links.csv"
    )
    product_service = ProductService()
    offer_service = OfferService()

    async with (
        MercadoLivreApiProvider(resolved) as api_provider,
        MercadoLivreWebProvider(resolved) as web_provider,
    ):
        discovery = DiscoveryService(api_provider)
        with session_scope() as session:
            config_service.sync_database(session, niches_file)
            scan_run = ScanRun()
            session.add(scan_run)
            record_event(session, "INFO", "worker.scan", "scan_started", "ciclo iniciado")
            session.commit()
            publisher = await _build_publisher(resolved)
            try:
                publication_service = PublicationService(affiliate_provider, publisher, resolved)
                ordered_niches = sorted(
                    niches_file.niches,
                    key=lambda item: item.priority,
                    reverse=True,
                )
                for niche in ordered_niches:
                    collected = await discovery.discover_niche(niche)
                    if not collected:
                        fallback_discovery = DiscoveryService(web_provider)
                        collected = await fallback_discovery.discover_niche(niche)
                    for product, search, manual in collected:
                        try:
                            scan_run.collected_count += 1
                            saved_product = product_service.save_candidate(session, product)
                            if saved_product.ignored:
                                scan_run.ignored_count += 1
                                record_event(
                                    session,
                                    "INFO",
                                    "worker.scan",
                                    "product_ignored",
                                    product.product_id,
                                )
                                continue
                            rule = _manual_as_search(manual) if manual else search
                            decision = offer_service.evaluate(session, product, rule)
                            if not decision.approved:
                                scan_run.ignored_count += 1
                                continue
                            scan_run.approved_count += 1
                            approval = upsert_pending_approval(
                                session,
                                product,
                                niche,
                                rule,
                                decision,
                            )
                            if resolved.require_approval and approval.status != "approved":
                                record_event(
                                    session,
                                    "INFO",
                                    "worker.scan",
                                    "approval_pending",
                                    f"{product.product_id} em {niche.name}",
                                )
                                session.commit()
                                continue
                            published = await publication_service.publish_product(
                                session,
                                niche,
                                product,
                                decision,
                                manual,
                            )
                            scan_run.published_count += published
                            if published:
                                mark_product_published(
                                    session,
                                    product.marketplace,
                                    product.product_id,
                                    niche.name,
                                )
                            session.commit()
                        except Exception as exc:
                            session.rollback()
                            scan_run.error_count += 1
                            record_event(
                                session,
                                "ERROR",
                                "worker.scan",
                                "product_cycle_failed",
                                f"{product.product_id}: {exc}",
                            )
                            logger.error(
                                "product_cycle_failed product=%s error=%s",
                                product.product_id,
                                exc,
                        )
                scan_run.finished_at = datetime.now(UTC)
                record_event(
                    session,
                    "INFO",
                    "worker.scan",
                    "scan_finished",
                    (
                        f"coletados={scan_run.collected_count} "
                        f"aprovados={scan_run.approved_count} "
                        f"publicados={scan_run.published_count} "
                        f"erros={scan_run.error_count}"
                    ),
                )
                session.commit()
            except Exception as exc:
                scan_run.error_message = str(exc)
                scan_run.finished_at = datetime.now(UTC)
                record_event(session, "ERROR", "worker.scan", "scan_failed", str(exc))
                session.commit()
                raise
            finally:
                if publisher is not None:
                    await publisher.aclose()
            return scan_run


async def _build_publisher(settings: Settings) -> TelegramPublisher | None:
    if settings.dry_run:
        return None
    client = TelegramClient(settings)
    await client.__aenter__()
    return TelegramPublisher(client, settings)


def _manual_as_search(manual: ManualProductConfig | None) -> SearchConfig | None:
    if manual is None:
        return None
    return SearchConfig(
        query="manual",
        enabled=manual.enabled,
        max_results=1,
        max_price=manual.max_price,
        min_discount_percent=manual.min_discount_percent,
    )
