from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings, get_settings
from app.database.base import Base

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def _ensure_sqlite_parent(database_url: str) -> None:
    if not database_url.startswith("sqlite:///"):
        return
    raw_path = database_url.removeprefix("sqlite:///")
    if raw_path and raw_path != ":memory:":
        Path(raw_path).parent.mkdir(parents=True, exist_ok=True)


def create_database_engine(settings: Settings | None = None) -> Engine:
    resolved = settings or get_settings()
    _ensure_sqlite_parent(resolved.database_url)
    connect_args = (
        {"check_same_thread": False} if resolved.database_url.startswith("sqlite") else {}
    )
    return create_engine(resolved.database_url, connect_args=connect_args, pool_pre_ping=True)


def configure_session(settings: Settings | None = None) -> None:
    global _engine, _session_factory
    _engine = create_database_engine(settings)
    _session_factory = sessionmaker(bind=_engine, expire_on_commit=False)


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        configure_session()
    assert _engine is not None
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _session_factory
    if _session_factory is None:
        configure_session()
    assert _session_factory is not None
    return _session_factory


@contextmanager
def session_scope() -> Generator[Session]:
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    from app.database import models  # noqa: F401

    Base.metadata.create_all(bind=get_engine())


def check_database() -> bool:
    with get_engine().connect() as connection:
        connection.execute(text("SELECT 1"))
    return True
