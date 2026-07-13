from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from app.schemas.product import ProductCandidate


class AffiliateLinkProvider(ABC):
    @abstractmethod
    def resolve_affiliate_link(
        self,
        session: Session,
        product: ProductCandidate,
        niche_id: int | None,
        manual_affiliate_url: str | None = None,
    ) -> str | None:
        raise NotImplementedError

    @abstractmethod
    def register_pending_link(
        self,
        product: ProductCandidate,
        niche_name: str,
    ) -> None:
        raise NotImplementedError

