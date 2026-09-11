"""Domain records shared by the service layers."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum


class DeliveryStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class JobStatus(StrEnum):
    QUEUED = "queued"
    CLAIMED = "claimed"
    DONE = "done"
    FAILED = "failed"


@dataclass(frozen=True)
class User:
    user_id: str
    display_name: str
    timezone_name: str = "UTC"
    enabled: bool = True


@dataclass(frozen=True)
class ProviderConfig:
    name: str
    endpoint: str
    enabled: bool = True
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass
class DeliveryRecord:
    delivery_id: str
    recipient: str
    payload: str
    status: DeliveryStatus = DeliveryStatus.PENDING
    attempts: int = 0
    error: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    sent_at: datetime | None = None

    def mark_sent(self) -> None:
        self.status = DeliveryStatus.SENT
        self.sent_at = datetime.now(timezone.utc)
        self.error = None

    def mark_failed(self, error: Exception | str) -> None:
        self.status = DeliveryStatus.FAILED
        self.error = str(error)

    def record_attempt(self) -> None:
        self.attempts += 1


@dataclass(frozen=True)
class HealthReport:
    component: str
    healthy: bool
    detail: str
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
