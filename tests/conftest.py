from collections.abc import Generator
from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.database.session import configure_session, init_db, session_scope


@pytest.fixture
def test_settings(tmp_path: Path) -> Settings:
    return Settings(
        DATABASE_URL=f"sqlite:///{tmp_path / 'offers.db'}",
        LOG_LEVEL="ERROR",
        DRY_RUN=True,
        POST_WITHOUT_AFFILIATE_LINK=False,
        NICHES_CONFIG_PATH=tmp_path / "niches.yml",
    )


@pytest.fixture
def db_session(test_settings: Settings) -> Generator[Session]:
    configure_session(test_settings)
    init_db()
    with session_scope() as session:
        yield session

