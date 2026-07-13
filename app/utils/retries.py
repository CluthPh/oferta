from __future__ import annotations

import asyncio
import random
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta


@dataclass
class CircuitBreaker:
    failure_threshold: int = 5
    reset_after_seconds: int = 300
    failures: int = 0
    opened_at: datetime | None = None

    def allow_request(self) -> bool:
        if self.opened_at is None:
            return True
        if datetime.now(UTC) - self.opened_at >= timedelta(seconds=self.reset_after_seconds):
            self.failures = 0
            self.opened_at = None
            return True
        return False

    def record_success(self) -> None:
        self.failures = 0
        self.opened_at = None

    def record_failure(self) -> None:
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.opened_at = datetime.now(UTC)


async def retry_async[T](
    func: Callable[[], Awaitable[T]],
    attempts: int = 3,
    base_delay: float = 1.0,
    retry_after: float | None = None,
) -> T:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            return await func()
        except Exception as exc:
            last_error = exc
            if attempt == attempts - 1:
                break
            delay = retry_after if retry_after is not None else base_delay * (2**attempt)
            await asyncio.sleep(delay + random.uniform(0, 0.25))
    assert last_error is not None
    raise last_error
