# vim:sw=4:ts=4:et:
"""Python Ring RingGeneric wrapper."""


# pylint: disable=useless-object-inheritance
import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

import pytz

from ring_doorbell.const import URL_DOORBELL_HISTORY, RingCapability

_LOGGER = logging.getLogger(__name__)


class RingGeneric:
    """Generic Implementation for Ring Chime/Doorbell."""

    if TYPE_CHECKING:
        from ring_doorbell.ring import Ring

    def __init__(self, ring: "Ring", device_api_id: int) -> None:
        """Initialize Ring Generic."""
        self._ring = ring
        # This is the account ID of the device.
        # Not the same as device ID.
        self.device_api_id = device_api_id
        self.capability = False
        self.alert = None
        self._health_attrs: Dict[str, Any] = {}

        # alerts notifications
        self.alert_expires_at = None

    def __repr__(self) -> str:
        """Return __repr__."""
        return f"<{self.__class__.__name__}: {self.name}>"

    def __str__(self) -> str:
        return f"{self.name} ({self.kind})"

    def update(self) -> None:
        """Update this device info."""
        self.update_health_data()

    def update_health_data(self) -> None:
        """Update the health data."""
        raise NotImplementedError

    @property
    def _attrs(self) -> Dict[str, Any]:
        """Return attributes."""
        return self._ring.devices_data[self.family][self.device_api_id]

    @property
    def id(self) -> int:
        """Return ID."""
        return self.device_api_id

    @property
    def name(self) -> str:
        """Return name."""
        return self._attrs["description"]

    @property
    def device_id(self) -> str:
        """Return device ID.

        This is the device_id returned by the api, usually the MAC.
        Not to be confused with the id for the device
        """
        return self._attrs["device_id"]

    @property
    def location_id(self) -> Optional[str]:
        """Return location id."""
        return self._attrs.get("location_id", None)

    @property
    def family(self) -> str:
        """Return Ring device family type."""
        raise NotImplementedError

    @property
    def model(self) -> str:
        """Return Ring device model name."""
        raise NotImplementedError

    @property
    def battery_life(self) -> Optional[int]:
        """Return battery life."""
        raise NotImplementedError

    def has_capability(self, capability: Union[RingCapability, str]) -> bool:
        """Return if device has specific capability."""
        return self.capability

    @property
    def address(self) -> Optional[str]:
        """Return address."""
        return self._attrs.get("address")

    @property
    def firmware(self) -> Optional[str]:
        """Return firmware."""
        return self._attrs.get("firmware_version")

    @property
    def latitude(self) -> Optional[float]:
        """Return latitude attr."""
        return self._attrs.get("latitude")

    @property
    def longitude(self) -> Optional[float]:
        """Return longitude attr."""
        return self._attrs.get("longitude")

    @property
    def kind(self) -> str:
        """Return kind attr."""
        return self._attrs["kind"]

    @property
    def timezone(self) -> Optional[str]:
        """Return timezone."""
        return self._attrs.get("time_zone")

    @property
    def wifi_name(self) -> Optional[str]:
        """Return wifi ESSID name.

        Requires health data to be updated.
        """
        return self._health_attrs.get("wifi_name")

    @property
    def wifi_signal_strength(self) -> Optional[int]:
        """Return wifi RSSI.

        Requires health data to be updated.
        """
        return self._health_attrs.get("latest_signal_strength")

    @property
    def wifi_signal_category(self) -> Optional[str]:
        """Return wifi signal category.

        Requires health data to be updated.
        """
        return self._health_attrs.get("latest_signal_category")

    def history(
        self,
        limit: int = 30,
        timezone: Optional[str] = None,
        kind: Optional[str] = None,
        enforce_limit: bool = False,
        older_than: Optional[int] = None,
        retry: int = 8,
        *,
        convert_timezone: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Return history with datetime objects.

        :param limit: specify number of objects to be returned
        :param timezone: determine which timezone to convert data objects
        :param kind: filter by kind (ding, motion, on_demand)
        :param enforce_limit: when True, this will enforce the limit and kind
        :param older_than: return older objects than the passed event_id
        :param retry: determine the max number of attempts to archive the limit
        """
        if not self.has_capability("history"):
            return []

        queries = 0
        original_limit = limit

        # set cap for max queries
        # pylint:disable=consider-using-min-builtin
        if retry > 10:
            retry = 10

        while True:
            params = {"limit": limit}
            if older_than:
                params["older_than"] = older_than

            url = URL_DOORBELL_HISTORY.format(self.device_api_id)
            response = self._ring.query(url, extra_params=params).json()

            # cherrypick only the selected kind events
            if kind:
                response = list(filter(lambda array: array["kind"] == kind, response))

            if convert_timezone:
                # convert for specific timezone
                utc = pytz.utc
                if timezone:
                    mytz = pytz.timezone(timezone)

                for entry in response:
                    dt_at = datetime.strptime(
                        entry["created_at"], "%Y-%m-%dT%H:%M:%S.%f%z"
                    )
                    utc_dt = datetime(
                        dt_at.year,
                        dt_at.month,
                        dt_at.day,
                        dt_at.hour,
                        dt_at.minute,
                        dt_at.second,
                        tzinfo=utc,
                    )
                    if timezone:
                        tz_dt = utc_dt.astimezone(mytz)
                        entry["created_at"] = tz_dt
                    else:
                        entry["created_at"] = utc_dt

            if enforce_limit:
                # return because already matched the number
                # of events by kind
                if len(response) >= original_limit:
                    return response[:original_limit]

                # ensure the loop will exit after max queries
                queries += 1
                if queries == retry:
                    _LOGGER.debug(
                        "Could not find total of %s of kind %s", original_limit, kind
                    )
                    break

                # ensure the kind objects returned to match limit
                limit = limit * 2

            else:
                break

        return response
