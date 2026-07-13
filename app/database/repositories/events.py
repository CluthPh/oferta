from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import ApplicationEvent


def record_event(
    session: Session,
    level: str,
    module: str,
    action: str,
    message: str = "",
) -> ApplicationEvent:
    event = ApplicationEvent(
        level=level.upper(),
        module=module,
        action=action,
        message=message,
    )
    session.add(event)
    return event


def list_events(session: Session, limit: int = 50) -> list[ApplicationEvent]:
    return list(
        session.scalars(
            select(ApplicationEvent).order_by(ApplicationEvent.created_at.desc()).limit(limit)
        ).all()
    )
