from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError

from app.core.config import Settings
from app.core.exceptions import AppError
from app.database.session import check_database
from app.marketplaces.registry import marketplace_source_status
from app.schemas.configuration import load_niches_file


class ValidationService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def validate(self) -> dict[str, object]:
        checks: list[dict[str, object]] = []
        self._check_paths(checks)
        self._check_config(checks)
        self._check_runtime(checks)
        status = "ok" if all(item["ok"] for item in checks) else "attention"
        return {"status": status, "checks": checks}

    def _check_paths(self, checks: list[dict[str, object]]) -> None:
        self._append_path_check(checks, "data_dir", self.settings.data_dir, must_exist=True)
        self._append_path_check(checks, "logs_dir", self.settings.logs_dir, must_exist=True)
        self._append_path_check(
            checks,
            "niches_config",
            self.settings.niches_config_path,
            must_exist=True,
        )

    def _check_config(self, checks: list[dict[str, object]]) -> None:
        path = self.settings.niches_config_path
        if not path.exists():
            checks.append(
                {
                    "name": "niches_yaml",
                    "ok": False,
                    "level": "error",
                    "message": f"arquivo nao encontrado: {path}",
                }
            )
            return
        try:
            config = load_niches_file(path)
        except (AppError, ValidationError, OSError, ValueError) as exc:
            checks.append(
                {
                    "name": "niches_yaml",
                    "ok": False,
                    "level": "error",
                    "message": str(exc),
                }
            )
            return
        enabled_niches = [niche for niche in config.niches if niche.enabled]
        searches = sum(len(niche.searches) for niche in enabled_niches)
        manual = sum(len(niche.manual_products) for niche in enabled_niches)
        checks.append(
            {
                "name": "niches_yaml",
                "ok": True,
                "level": "info",
                "message": (
                    f"{len(enabled_niches)} nicho(s) ativo(s), "
                    f"{searches} busca(s), {manual} produto(s) manual(is)"
                ),
            }
        )

    def _check_runtime(self, checks: list[dict[str, object]]) -> None:
        checks.append(
            {
                "name": "admin_api_key",
                "ok": bool(self.settings.admin_api_key),
                "level": "warning",
                "message": (
                    "ADMIN_API_KEY configurada"
                    if self.settings.admin_api_key
                    else "defina ADMIN_API_KEY para usar acoes administrativas"
                ),
            }
        )
        checks.append(
            {
                "name": "telegram",
                "ok": self.settings.dry_run or bool(self.settings.telegram_bot_token),
                "level": (
                    "info"
                    if self.settings.dry_run or self.settings.telegram_bot_token
                    else "error"
                ),
                "message": (
                    "DRY_RUN ativo; Telegram real nao sera usado"
                    if self.settings.dry_run
                    else "TELEGRAM_BOT_TOKEN configurado"
                    if self.settings.telegram_bot_token
                    else "TELEGRAM_BOT_TOKEN ausente com DRY_RUN=false"
                ),
            }
        )
        try:
            check_database()
        except Exception as exc:
            checks.append(
                {
                    "name": "database",
                    "ok": False,
                    "level": "error",
                    "message": str(exc),
                }
            )
        else:
            checks.append(
                {
                    "name": "database",
                    "ok": True,
                    "level": "info",
                    "message": "conexao SQLite/SQLAlchemy ok",
                }
            )
        sources = marketplace_source_status(self.settings.marketplace_sources)
        unsupported = [item["name"] for item in sources if not item["supported"]]
        checks.append(
            {
                "name": "marketplace_sources",
                "ok": not unsupported,
                "level": "warning" if unsupported else "info",
                "message": (
                    f"fontes sem provedor: {', '.join(str(item) for item in unsupported)}"
                    if unsupported
                    else ", ".join(str(item["name"]) for item in sources)
                ),
            }
        )

    @staticmethod
    def _append_path_check(
        checks: list[dict[str, object]],
        name: str,
        path: Path,
        must_exist: bool,
    ) -> None:
        exists = path.exists()
        checks.append(
            {
                "name": name,
                "ok": exists if must_exist else True,
                "level": "info" if exists else "error",
                "message": str(path),
            }
        )
