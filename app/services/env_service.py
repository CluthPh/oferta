from __future__ import annotations

from pathlib import Path

from app.core.config import Settings, get_settings

EDITABLE_ENV_KEYS = {
    "DRY_RUN",
    "POST_WITHOUT_AFFILIATE_LINK",
    "SCAN_INTERVAL_MINUTES",
    "RUN_SCAN_ON_STARTUP",
    "REQUIRE_APPROVAL",
    "MARKETPLACE_SOURCES",
}


class EnvService:
    def __init__(self, path: Path = Path(".env")) -> None:
        self.path = path

    def summary(self, settings: Settings) -> dict[str, object]:
        return {
            "DRY_RUN": settings.dry_run,
            "POST_WITHOUT_AFFILIATE_LINK": settings.post_without_affiliate_link,
            "SCAN_INTERVAL_MINUTES": settings.scan_interval_minutes,
            "RUN_SCAN_ON_STARTUP": settings.run_scan_on_startup,
            "REQUIRE_APPROVAL": settings.require_approval,
            "MARKETPLACE_SOURCES": settings.marketplace_sources,
        }

    def update(self, values: dict[str, object]) -> dict[str, str]:
        clean = {
            key: self._format_value(value)
            for key, value in values.items()
            if key in EDITABLE_ENV_KEYS and value is not None
        }
        if not clean:
            return {}
        lines = self._read_lines()
        seen: set[str] = set()
        updated: list[str] = []
        for line in lines:
            key = line.split("=", 1)[0].strip() if "=" in line else ""
            if key in clean:
                updated.append(f"{key}={clean[key]}")
                seen.add(key)
            else:
                updated.append(line)
        for key, value in clean.items():
            if key not in seen:
                updated.append(f"{key}={value}")
        self.path.write_text("\n".join(updated).rstrip() + "\n", encoding="utf-8")
        get_settings.cache_clear()
        return clean

    def _read_lines(self) -> list[str]:
        if not self.path.exists():
            return []
        return self.path.read_text(encoding="utf-8").splitlines()

    @staticmethod
    def _format_value(value: object) -> str:
        if isinstance(value, bool):
            return str(value).lower()
        return str(value)
