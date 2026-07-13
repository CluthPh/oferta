from pathlib import Path

import yaml
from pydantic import ValidationError

from app.core.exceptions import ConfigurationError
from app.schemas.niche import NichesFile


def load_niches_file(path: Path) -> NichesFile:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigurationError(
            f"Arquivo de nichos nao encontrado: {path}. Copie data/niches.example.yml para {path}."
        ) from exc
    except yaml.YAMLError as exc:
        raise ConfigurationError(f"YAML invalido em {path}: {exc}") from exc

    try:
        return NichesFile.model_validate(raw)
    except ValidationError as exc:
        raise ConfigurationError(f"Configuracao invalida em {path}: {exc}") from exc

