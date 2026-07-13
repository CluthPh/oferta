from dataclasses import dataclass
from decimal import Decimal

from app.schemas.niche import NicheConfig
from app.schemas.product import ProductCandidate


@dataclass(frozen=True)
class OfferDecision:
    approved: bool
    score: int
    reason: str


@dataclass(frozen=True)
class PublicationTarget:
    niche: NicheConfig
    chat_id: str
    topic_id: int | None = None


@dataclass(frozen=True)
class PreparedPublication:
    product: ProductCandidate
    target: PublicationTarget
    link: str
    decision: OfferDecision
    price: Decimal | None
    dry_run: bool

