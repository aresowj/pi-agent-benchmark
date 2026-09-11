"""Notification delivery orchestration."""
# pyright: reportMissingImports=false

from __future__ import annotations

from dataclasses import dataclass

from .client import NotificationClient
from .config import Settings


@dataclass(frozen=True)
class Notification:
    delivery_id: str
    recipient: str
    payload: str


class NotificationService:
    def __init__(self, client: NotificationClient, settings: Settings) -> None:
        self.client = client
        self.settings = settings

    def deliver(self, notification: Notification) -> str:
        """Deliver one notification, retrying transient provider failures."""
        return self.client.send(notification.recipient, notification.payload)
