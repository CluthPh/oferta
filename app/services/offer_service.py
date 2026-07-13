from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.database.repositories.price_history import get_previous_price, get_previous_prices
from app.schemas.niche import SearchConfig
from app.schemas.product import ProductCandidate
from app.schemas.publication import OfferDecision
from app.utils.text import contains_all_words, contains_any_word, normalize_words


class OfferService:
    def evaluate(
        self,
        session: Session,
        product: ProductCandidate,
        search: SearchConfig | None,
    ) -> OfferDecision:
        reasons: list[str] = []
        if product.current_price is None:
            return OfferDecision(False, 0, "produto sem preco atual")
        if search is not None:
            rejected = self._reject_by_search(product, search)
            if rejected:
                return OfferDecision(False, 0, rejected)
            reasons.append(f"regra={search.query}")
        score = self.score(session, product, search)
        if score < 35:
            return OfferDecision(False, score, f"score insuficiente: {score}")
        reasons.append(f"score={score}")
        return OfferDecision(True, score, "; ".join(reasons))

    def _reject_by_search(self, product: ProductCandidate, search: SearchConfig) -> str:
        if (
            search.min_price is not None
            and product.current_price is not None
            and product.current_price < search.min_price
        ):
            return "preco abaixo do minimo"
        if (
            search.max_price is not None
            and product.current_price is not None
            and product.current_price > search.max_price
        ):
            return "preco acima do maximo"
        if (
            search.min_discount_percent
            and (product.discount_percent or 0) < search.min_discount_percent
        ):
            return "desconto abaixo do minimo"
        if search.free_shipping_only and not product.free_shipping:
            return "sem frete gratis"
        if search.condition and product.condition and product.condition != search.condition:
            return "condicao diferente da configurada"
        if search.include_words and not contains_all_words(product.title, search.include_words):
            return "palavras obrigatorias ausentes"
        if search.exclude_words and contains_any_word(product.title, search.exclude_words):
            return "palavra proibida no titulo"
        seller = normalize_words(product.seller_name or product.seller_id)
        allowed_sellers = {normalize_words(item) for item in search.allowed_sellers}
        blocked_sellers = {normalize_words(item) for item in search.blocked_sellers}
        if search.allowed_sellers and seller not in allowed_sellers:
            return "vendedor fora da lista permitida"
        if search.blocked_sellers and seller in blocked_sellers:
            return "vendedor bloqueado"
        return ""

    def score(
        self,
        session: Session,
        product: ProductCandidate,
        search: SearchConfig | None,
    ) -> int:
        score = 0
        discount = product.discount_percent or 0
        score += min(35, int(discount * 1.5))
        previous = get_previous_price(session, product.marketplace, product.product_id)
        if previous and previous.price and product.current_price:
            drop = ((previous.price - product.current_price) / previous.price) * Decimal("100")
            if drop > 0:
                score += min(20, int(drop * 2))
        previous_prices = [
            row.price
            for row in get_previous_prices(session, product.marketplace, product.product_id)
            if row.price is not None
        ]
        if previous_prices and product.current_price is not None:
            lowest_previous = min(previous_prices)
            if lowest_previous > 0:
                discount_against_low = (
                    (lowest_previous - product.current_price) / lowest_previous
                ) * Decimal("100")
                if discount_against_low >= Decimal("5"):
                    score += 10
                elif discount_against_low >= Decimal("2"):
                    score += 5
        if product.free_shipping:
            score += 10
        if product.official_store:
            score += 10
        if product.sold_quantity:
            score += min(5, product.sold_quantity // 100)
        if product.available_quantity is not None and product.available_quantity > 0:
            score += 3
        if search is not None and search.include_words:
            normalized_title = normalize_words(product.title)
            matched = sum(
                1 for word in search.include_words if normalize_words(word) in normalized_title
            )
            score += min(15, matched * 5)
        if search is not None and product.current_price is not None:
            if search.min_price is None or product.current_price >= search.min_price:
                score += 5
            if search.max_price is None or product.current_price <= search.max_price:
                score += 5
        return max(0, min(100, score))
