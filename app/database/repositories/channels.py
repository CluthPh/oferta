from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Channel, Niche, SearchRule
from app.schemas.niche import NicheConfig


def sync_niche_config(session: Session, config: NicheConfig) -> Niche:
    niche = session.scalar(select(Niche).where(Niche.name == config.name))
    if niche is None:
        niche = Niche(name=config.name)
        session.add(niche)
        session.flush()

    niche.enabled = config.enabled
    niche.priority = config.priority
    niche.header = config.telegram.header
    niche.footer = "\n".join(config.telegram.footer)
    niche.button_text = config.telegram.button_text
    niche.hashtags = ",".join(config.telegram.hashtags)

    existing_channels = {channel.chat_id: channel for channel in niche.channels}
    for chat_id in config.telegram.chat_ids:
        channel = existing_channels.get(chat_id)
        if channel is None:
            channel = Channel(niche_id=niche.id, chat_id=chat_id)
            session.add(channel)
        channel.active = True
        channel.topic_id = config.telegram.topic_id

    for channel in niche.channels:
        if channel.chat_id not in config.telegram.chat_ids:
            channel.active = False

    for rule in list(niche.searches):
        session.delete(rule)
    session.flush()
    for search in config.searches:
        session.add(
            SearchRule(
                niche_id=niche.id,
                query=search.query,
                enabled=search.enabled,
                max_results=search.max_results,
                min_price=search.min_price,
                max_price=search.max_price,
                min_discount_percent=search.min_discount_percent,
                free_shipping_only=search.free_shipping_only,
                condition=search.condition,
                include_words=",".join(search.include_words),
                exclude_words=",".join(search.exclude_words),
                allowed_sellers=",".join(search.allowed_sellers),
                blocked_sellers=",".join(search.blocked_sellers),
                sort=search.sort,
            )
        )
    return niche


def list_niches(session: Session) -> list[Niche]:
    return list(session.scalars(select(Niche).order_by(Niche.priority.desc(), Niche.name)).all())


def get_niche_id(session: Session, name: str) -> int | None:
    niche = session.scalar(select(Niche.id).where(Niche.name == name))
    return int(niche) if niche is not None else None

