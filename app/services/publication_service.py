from __future__ import annotations

import asyncio
import logging

from sqlalchemy.orm import Session

from app.affiliates.base import AffiliateLinkProvider
from app.core.config import Settings, get_settings
from app.database.repositories.channels import get_niche_id
from app.database.repositories.events import record_event
from app.database.repositories.posts import latest_publication, record_publication, should_repost
from app.schemas.niche import ManualProductConfig, NicheConfig
from app.schemas.product import ProductCandidate
from app.schemas.publication import OfferDecision
from app.telegram.formatter import format_offer_html
from app.telegram.publisher import TelegramPublisher

logger = logging.getLogger("service.publication")


class PublicationService:
    def __init__(
        self,
        affiliate_provider: AffiliateLinkProvider,
        publisher: TelegramPublisher | None,
        settings: Settings | None = None,
    ) -> None:
        self.affiliate_provider = affiliate_provider
        self.publisher = publisher
        self.settings = settings or get_settings()
        self._published_by_niche: dict[str, int] = {}
        self._seen_targets: set[tuple[str, str, str]] = set()

    async def publish_product(
        self,
        session: Session,
        niche: NicheConfig,
        product: ProductCandidate,
        decision: OfferDecision,
        manual: ManualProductConfig | None = None,
        force: bool = False,
    ) -> int:
        niche_id = get_niche_id(session, niche.name)
        affiliate_url = self.affiliate_provider.resolve_affiliate_link(
            session,
            product,
            niche_id=niche_id,
            manual_affiliate_url=manual.affiliate_url if manual else None,
        )
        link = affiliate_url
        if link is None:
            self.affiliate_provider.register_pending_link(product, niche.name)
            if not self.settings.post_without_affiliate_link:
                logger.info("affiliate_missing product=%s niche=%s", product.product_id, niche.name)
                return 0
            link = product.canonical_url
            logger.warning(
                "posting_without_affiliate product=%s niche=%s",
                product.product_id,
                niche.name,
            )

        channels = self._target_channels(niche, manual)
        published = 0
        for chat_id in channels:
            target_key = (niche.name, product.product_id, chat_id)
            if target_key in self._seen_targets:
                record_event(
                    session,
                    "INFO",
                    "service.publication",
                    "duplicate_current_cycle",
                    f"{product.product_id} em {chat_id}",
                )
                continue
            if self._published_by_niche.get(niche.name, 0) >= niche.publication.max_posts_per_cycle:
                record_event(
                    session,
                    "INFO",
                    "service.publication",
                    "cycle_limit_reached",
                    f"{niche.name}: limite {niche.publication.max_posts_per_cycle}",
                )
                continue
            previous = latest_publication(session, product.product_id, chat_id)
            if force:
                can_post, reason = True, "publicacao manual"
            else:
                can_post, reason = should_repost(
                    previous=previous,
                    current_price=product.current_price,
                    repost_after_hours=niche.publication.repost_after_hours,
                    min_price_drop_percent=niche.publication.min_price_drop_percent,
                    price_change_mode=niche.publication.price_change_mode,
                )
            if not can_post:
                logger.info(
                    "publication_skipped product=%s channel=%s reason=%s",
                    product.product_id,
                    chat_id,
                    reason,
                )
                continue
            if self.settings.dry_run:
                self._print_dry_run(niche, chat_id, product, link, decision.reason)
                record_publication(
                    session,
                    product.marketplace,
                    product.product_id,
                    chat_id,
                    product.current_price,
                    link,
                    "dry_run",
                    decision.reason,
                    dry_run=True,
                )
                self._mark_published(niche.name, target_key)
                published += 1
                continue
            if self.publisher is None:
                raise RuntimeError("Publisher real nao configurado")
            try:
                message_id = await self.publisher.publish_offer(
                    product=product,
                    chat_id=chat_id,
                    config=niche.telegram,
                    link=link,
                    topic_id=niche.telegram.topic_id,
                )
            except Exception as exc:
                record_publication(
                    session,
                    product.marketplace,
                    product.product_id,
                    chat_id,
                    product.current_price,
                    link,
                    "failed",
                    str(exc),
                )
                logger.error(
                    "publication_failed product=%s channel=%s error=%s",
                    product.product_id,
                    chat_id,
                    exc,
                )
                continue
            record_publication(
                session,
                product.marketplace,
                product.product_id,
                chat_id,
                product.current_price,
                link,
                "sent",
                reason,
                telegram_message_id=message_id,
            )
            self._mark_published(niche.name, target_key)
            published += 1
            if niche.publication.seconds_between_posts > 0:
                await asyncio.sleep(niche.publication.seconds_between_posts)
        return published

    def _target_channels(self, niche: NicheConfig, manual: ManualProductConfig | None) -> list[str]:
        if manual and manual.channels:
            allowed = set(manual.channels)
            return [chat_id for chat_id in niche.telegram.chat_ids if chat_id in allowed]
        return niche.telegram.chat_ids

    def _print_dry_run(
        self,
        niche: NicheConfig,
        chat_id: str,
        product: ProductCandidate,
        link: str,
        reason: str,
    ) -> None:
        message = format_offer_html(product, niche.telegram)
        print(
            "\n".join(
                [
                    "DRY RUN",
                    f"Nicho: {niche.name}",
                    f"Canal: {chat_id}",
                    f"Produto: {product.title}",
                    f"Preco: {product.current_price}",
                    f"Desconto: {product.discount_percent}",
                    f"Link: {link}",
                    f"Mensagem:\n{message}",
                    f"Motivo da aprovacao: {reason}",
                    "",
                ]
            )
        )

    def _mark_published(self, niche_name: str, target_key: tuple[str, str, str]) -> None:
        self._seen_targets.add(target_key)
        self._published_by_niche[niche_name] = self._published_by_niche.get(niche_name, 0) + 1
