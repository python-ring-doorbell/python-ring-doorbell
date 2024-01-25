"""Module for ring events."""
from dataclasses import dataclass


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

    def __getitem__(self, key):
        return getattr(self, key)

    def get(self, key):
        return getattr(self, key) if hasattr(self, key) else None
