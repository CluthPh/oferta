from __future__ import annotations

from sqlalchemy.orm import Session

from app.affiliates.database_provider import DatabaseAffiliateLinkProvider
from app.core.config import Settings
from app.database.models import Product
from app.database.repositories.approvals import mark_product_published
from app.schemas.publication import OfferDecision
from app.services.niche_selector import select_niche
from app.services.offer_service import OfferService
from app.services.product_mapper import product_to_candidate
from app.services.publication_service import PublicationService
from app.telegram.client import TelegramClient
from app.telegram.publisher import TelegramPublisher


class PublishNowService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def publish(
        self,
        session: Session,
        product: Product,
        niche_name: str | None,
        force: bool = False,
    ) -> dict[str, object]:
        niche = select_niche(self.settings.niches_config_path, niche_name)
        candidate = product_to_candidate(product)
        decision = (
            OfferDecision(True, 100, "publicacao manual")
            if force
            else OfferService().evaluate(session, candidate, None)
        )
        if not decision.approved:
            return {
                "status": "rejected",
                "published": 0,
                "score": decision.score,
                "reason": decision.reason,
            }
        affiliate_provider = DatabaseAffiliateLinkProvider(
            self.settings.data_dir / "pending_affiliate_links.csv"
        )
        publisher = await self._build_publisher()
        try:
            service = PublicationService(affiliate_provider, publisher, self.settings)
            published = await service.publish_product(
                session,
                niche,
                candidate,
                decision,
                force=force,
            )
        finally:
            if publisher is not None:
                await publisher.aclose()
        if published:
            mark_product_published(session, candidate.marketplace, candidate.product_id, niche.name)
        return {
            "status": "finished",
            "published": published,
            "score": decision.score,
            "reason": decision.reason,
            "niche": niche.name,
        }

    async def _build_publisher(self) -> TelegramPublisher | None:
        if self.settings.dry_run:
            return None
        client = TelegramClient(self.settings)
        await client.__aenter__()
        return TelegramPublisher(client, self.settings)
