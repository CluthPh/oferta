from __future__ import annotations

import csv
from pathlib import Path

from app.schemas.product import ProductCandidate

CSV_FIELDS = ["product_id", "canonical_url", "affiliate_url", "niche", "active"]


class AffiliateCsvStore:
    def __init__(self, pending_path: Path) -> None:
        self.pending_path = pending_path
        self.pending_path.parent.mkdir(parents=True, exist_ok=True)

    def register_pending(self, product: ProductCandidate, niche_name: str) -> None:
        rows = self.read_rows(self.pending_path)
        exists = any(
            row.get("product_id") == product.product_id and row.get("niche") == niche_name
            for row in rows
        )
        if exists:
            return
        rows.append(
            {
                "product_id": product.product_id,
                "canonical_url": product.canonical_url,
                "affiliate_url": "",
                "niche": niche_name,
                "active": "true",
            }
        )
        self.write_rows(self.pending_path, rows)

    def read_rows(self, path: Path) -> list[dict[str, str]]:
        if not path.exists():
            return []
        with path.open("r", encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))

    def write_rows(self, path: Path, rows: list[dict[str, str]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
            writer.writeheader()
            writer.writerows(rows)

