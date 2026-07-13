from __future__ import annotations

from app.core.constants import MARKETPLACE_MERCADOLIVRE

SUPPORTED_MARKETPLACES = {MARKETPLACE_MERCADOLIVRE}


def parse_marketplace_sources(raw: str) -> list[str]:
    return [item.strip().lower() for item in raw.split(",") if item.strip()]


def marketplace_source_status(raw: str) -> list[dict[str, object]]:
    sources = parse_marketplace_sources(raw)
    return [
        {
            "name": source,
            "supported": source in SUPPORTED_MARKETPLACES,
            "message": (
                "provedor ativo"
                if source in SUPPORTED_MARKETPLACES
                else "fonte configurada, mas provedor ainda nao implementado"
            ),
        }
        for source in sources
    ]
