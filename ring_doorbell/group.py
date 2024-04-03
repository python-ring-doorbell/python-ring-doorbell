# vim:sw=4:ts=4:et:
"""Python Ring light group wrapper."""

from __future__ import annotations

import logging
import warnings
from typing import TYPE_CHECKING, Any

from ring_doorbell.const import (
    GROUP_DEVICES_ENDPOINT,
    MSG_ALLOWED_VALUES,
    RingCapability,
)
from ring_doorbell.exceptions import RingError

_LOGGER = logging.getLogger(__name__)


class RingLightGroup:
    """Implementation for RingLightGroup."""

    if TYPE_CHECKING:
        from ring_doorbell.ring import Ring

    def __init__(self, ring: Ring, group_id: str) -> None:
        """Initialize Ring Light Group."""
        self._ring = ring
        self.group_id = group_id  # pylint:disable=invalid-name
        self._health_attrs: dict[str, Any] = {}
        self._health_attrs_fetched = False

    def __repr__(self) -> str:
        """Return __repr__."""
        return f"<{self.__class__.__name__}: {self.name}>"

    def update(self) -> None:
        """Update this device info."""
        url = GROUP_DEVICES_ENDPOINT.format(self.location_id, self.group_id)
        self._health_attrs = self._ring.query(url).json()
        self._health_attrs_fetched = True

    @property
    def _attrs(self) -> dict[str, Any]:
        """Return attributes."""
        return self._ring.groups_data[self.group_id]

    @property
    def id(self) -> str:
        """Return ID."""
        return self.group_id

    @property
    def name(self) -> str:
        """Return name."""
        return self._attrs["name"]

    @property
    def family(self) -> str:
        """Return Ring device family type."""
        return "group"

    @property
    def device_id(self) -> str:
        """Return group ID. Deprecated."""
        warnings.warn(
            "RingLightGroup.device_id is deprecated; use group_id",
            DeprecationWarning,
            stacklevel=1,
        )
        return self.group_id

    @property
    def location_id(self) -> str:
        """Return group location ID."""
        return self._attrs["location_id"]

    @property
    def model(self) -> str:
        """Return Ring device model name."""
        return "Light Group"

    def has_capability(self, capability: RingCapability | str) -> bool:
        """Return if device has specific capability."""
        capability = (
            capability
            if isinstance(capability, RingCapability)
            else RingCapability.from_name(capability)
        )
        if capability == RingCapability.LIGHT:
            return True
        return False

    @property
    def lights(self) -> bool:
        """Return lights status."""
        if not self._health_attrs_fetched:
            self.update()
        return self._health_attrs["lights_on"]

    @lights.setter
    def lights(self, value: bool | tuple[bool, int]) -> None:
        """Control the lights."""
        values = ["True", "False"]
        state = None
        duration = None
        if isinstance(value, tuple):
            state, duration = value
        else:
            state = value
        if not isinstance(state, bool):
            raise RingError(MSG_ALLOWED_VALUES.format(", ".join(values)))

        url = GROUP_DEVICES_ENDPOINT.format(self.location_id, self.group_id)
        payload: dict[str, dict[str, bool | int]] = {"lights_on": {"enabled": state}}
        if duration is not None:
            payload["lights_on"]["duration_seconds"] = duration
        self._ring.query(url, method="POST", json=payload)
        self.update()
