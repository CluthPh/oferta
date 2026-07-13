from pathlib import Path

from app.schemas.configuration import load_niches_file
from app.schemas.niche import NicheConfig


def select_niche(path: Path, niche_name: str | None = None) -> NicheConfig:
    config = load_niches_file(path)
    enabled = [niche for niche in config.niches if niche.enabled]
    if not enabled:
        raise ValueError("nenhum nicho ativo no YAML")
    if niche_name is None:
        return sorted(enabled, key=lambda item: item.priority, reverse=True)[0]
    for niche in enabled:
        if niche.name == niche_name:
            return niche
    raise ValueError(f"nicho nao encontrado: {niche_name}")
