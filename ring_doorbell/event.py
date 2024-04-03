"""Module for ring events."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RingEvent:
    """Class for ring events."""

    id: int
    doorbot_id: int
    device_name: str
    device_kind: str
    now: float
    expires_in: float
    kind: str
    state: str

    def __getitem__(self, key: str) -> Any:
        """Get a value by string."""
        return getattr(self, key)

    def get(self, key: str) -> Any | None:
        """Get a value by string and return None if not present."""
        return getattr(self, key) if hasattr(self, key) else None
