from fastapi import APIRouter

from app.database.repositories.channels import list_niches
from app.database.session import session_scope

router = APIRouter(tags=["niches"])


@router.get("/niches")
def niches() -> list[dict[str, object]]:
    with session_scope() as session:
        return [
            {
                "id": niche.id,
                "name": niche.name,
                "enabled": niche.enabled,
                "priority": niche.priority,
                "channels": [channel.chat_id for channel in niche.channels if channel.active],
            }
            for niche in list_niches(session)
        ]

