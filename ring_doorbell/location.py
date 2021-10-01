# coding: utf-8
# vim:sw=4:ts=4:et:
"""Python Ring Location wrapper."""
import logging

from ring_doorbell.generic import RingGeneric
from ring_doorbell.const import (
    APP_URI,
    LOCATION_MODE_ENDPOINT
)
from enum import Enum

_LOGGER = logging.getLogger(__name__)

class LocationMode(Enum):
    HOME = "home"
    AWAY = "away"

class RingLocation:
    """Implementation for Ring Location."""

    def __init__(self, ring, locationData):
        self._ring = ring
        self._location_id = locationData["location_id"]
        self._owner_id = locationData["owner_id"]
        self._name = locationData["name"]
        self._latitude = locationData["geo_coordinates"]["latitude"]
        self._longitude = locationData["geo_coordinates"]["longitude"]
        self._address1 = locationData["address"]["address1"]
        self._address2 = locationData["address"]["address2"]
        self._city = locationData["address"]["city"]
        self._state = locationData["address"]["state"]
        self._zip_code = locationData["address"]["zip_code"]
        self._country = locationData["address"]["country"]
        self._timezone = locationData["address"]["timezone"]
        self.update()


    def update(self):
        """Update this device info."""
        modevalue = self._ring.query(LOCATION_MODE_ENDPOINT.format(self._location_id), base=APP_URI).json().get("mode", {})
        
        self._mode = LocationMode[modevalue.upper()]

    @property
    def family(self):
        """Return Ring device family type."""
        return "locations"

    @property
    def location_id(self):
        """Return location location_id."""
        return self._location_id

    @property
    def owner_id(self):
        """Return location owner_id."""
        return self._owner_id

    @property
    def name(self):
        """Return location name."""
        return self._name

    @property
    def mode(self):
        """Return location mode."""
        return self._mode

    @property
    def latitude(self):
        """Return location latitude."""
        return self._latitude

    @property
    def longitude(self):
        """Return location longitude."""
        return self._longitude

    @property
    def address1(self):
        """Return location address1."""
        return self._address1

    @property
    def address1(self):
        """Return location address2."""
        return self._address2

    @property
    def city(self):
        """Return location city."""
        return self._city

    @property
    def state(self):
        """Return location state."""
        return self._state

    @property
    def zip_code(self):
        """Return location zip_code."""
        return self._zip_code

    @property
    def country(self):
        """Return location country."""
        return self._country

    @property
    def timezone(self):
        """Return location timezone."""
        return self._timezone

    @mode.setter
    def mode(self, mode):
        if not isinstance(mode, LocationMode):
            raise TypeError('mode must be an instance of LocationMode Enum')

        payload = {"mode": mode.value}

        url = LOCATION_MODE_ENDPOINT.format(self._location_id)
        self._ring.query(url, base=APP_URI, method="POST", json=payload)
        self._ring.update_devices()
        return True
