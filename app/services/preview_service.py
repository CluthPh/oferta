from __future__ import annotations

from sqlalchemy.orm import Session

from app.affiliates.database_provider import DatabaseAffiliateLinkProvider
from app.core.config import Settings
from app.database.models import Product
from app.database.repositories.channels import get_niche_id
from app.database.repositories.posts import latest_publication, should_repost
from app.services.niche_selector import select_niche
from app.services.offer_service import OfferService
from app.services.product_mapper import product_to_candidate
from app.telegram.formatter import format_offer_html


class PreviewService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def preview(
        self,
        session: Session,
        product: Product,
        niche_name: str | None = None,
    ) -> dict[str, object]:
        niche = select_niche(self.settings.niches_config_path, niche_name)
        candidate = product_to_candidate(product)
        decision = OfferService().evaluate(session, candidate, None)
        niche_id = get_niche_id(session, niche.name)
        affiliate_provider = DatabaseAffiliateLinkProvider(
            self.settings.data_dir / "pending_affiliate_links.csv"
        )
        link = affiliate_provider.resolve_affiliate_link(session, candidate, niche_id=niche_id)
        link_used = link or candidate.canonical_url
        channels = []
        for chat_id in niche.telegram.chat_ids:
            previous = latest_publication(session, candidate.product_id, chat_id)
            can_post, reason = should_repost(
                previous=previous,
                current_price=candidate.current_price,
                repost_after_hours=niche.publication.repost_after_hours,
                min_price_drop_percent=niche.publication.min_price_drop_percent,
                price_change_mode=niche.publication.price_change_mode,
            )
            channels.append({"chat_id": chat_id, "can_post": can_post, "reason": reason})
        return {
            "product_id": candidate.product_id,
            "title": candidate.title,
            "niche": niche.name,
            "approved": decision.approved,
            "score": decision.score,
            "reason": decision.reason,
            "link": link_used,
            "affiliate_link_found": link is not None,
            "message_html": format_offer_html(candidate, niche.telegram),
            "channels": channels,
        }
