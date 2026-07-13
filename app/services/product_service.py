from sqlalchemy.orm import Session

from app.database.models import Product
from app.database.repositories.price_history import add_price_history
from app.database.repositories.products import upsert_product
from app.schemas.product import ProductCandidate


class ProductService:
    def save_candidate(self, session: Session, candidate: ProductCandidate) -> Product:
        product = upsert_product(session, candidate)
        add_price_history(session, candidate)
        return product
