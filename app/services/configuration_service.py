from pathlib import Path

from sqlalchemy.orm import Session

from app.database.repositories.channels import sync_niche_config
from app.schemas.configuration import load_niches_file
from app.schemas.niche import NichesFile


class ConfigurationService:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> NichesFile:
        return load_niches_file(self.path)

    def sync_database(self, session: Session, config: NichesFile) -> None:
        for niche in config.niches:
            sync_niche_config(session, niche)

