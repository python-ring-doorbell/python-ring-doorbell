# coding: utf-8
# vim:sw=4:ts=4:et:
"""Python Ring Doorbell wrapper."""
import logging
from time import time

from .const import (
    API_URI,
    DEVICES_ENDPOINT,
    NEW_SESSION_ENDPOINT,
    DINGS_ENDPOINT,
    POST_DATA,
    GROUPS_ENDPOINT,
)
from .auth import Auth  # noqa
from .doorbot import RingDoorBell
from .chime import RingChime
from .stickup_cam import RingStickUpCam
from .group import RingLightGroup


_LOGGER = logging.getLogger(__name__)


TYPES = {
    "stickup_cams": RingStickUpCam,
    "chimes": RingChime,
    "doorbots": RingDoorBell,
    "authorized_doorbots": lambda ring, description: RingDoorBell(
        ring, description, shared=True
    ),
}


# pylint: disable=useless-object-inheritance
class Ring(object):
    """A Python Abstraction object to Ring Door Bell."""

    def __init__(self, auth):
        """Initialize the Ring object."""
        self.auth = auth
        self.session = None
        self.devices_data = None
        self.chime_health_data = None
        self.doorbell_health_data = None
        self.dings_data = None
        self.groups_data = None

    def update_data(self):
        """Update all data."""
        if self.session is None:
            self.create_session()

        self.update_devices()

        self.update_dings()

        self.update_groups()

    def create_session(self):
        """Create a new Ring session."""
        session_post_data = POST_DATA
        session_post_data["device[hardware_id]"] = self.auth.get_hardware_id()

        self.session = self.query(
            NEW_SESSION_ENDPOINT,
            method="POST",
            data=session_post_data,
        ).json()

    def update_devices(self):
        """Update device data."""
        data = self.query(DEVICES_ENDPOINT).json()

        # Index data by device ID.
        self.devices_data = {
            device_type: {obj["id"]: obj for obj in devices}
            for device_type, devices in data.items()
        }

    def update_dings(self):
        """Update dings data."""
        self.dings_data = self.query(DINGS_ENDPOINT).json()

    def update_groups(self):
        """Update groups data."""
        # Get all locations
        locations = set()
        for devices in self.devices_data.values():
            for dev in devices.values():
                if "location_id" in dev:
                    locations.add(dev["location_id"])

        # Query for groups
        self.groups_data = {}
        locations.discard(None)
        for location in locations:
            data = self.query(GROUPS_ENDPOINT.format(location)).json()
            if data["device_groups"] is not None:
                for group in data["device_groups"]:
                    self.groups_data[group["device_group_id"]] = group

    def query(
        self, url, method="GET", extra_params=None, data=None, json=None, timeout=None
    ):
        """Query data from Ring API."""
        return self.auth.query(
            API_URI + url,
            method=method,
            extra_params=extra_params,
            data=data,
            json=json,
            timeout=timeout,
        )

    def devices(self):
        """Get all devices."""
        devices = {}

        for dev_type, convertor in TYPES.items():
            devices[dev_type] = [
                convertor(self, obj["id"])
                for obj in self.devices_data.get(dev_type, {}).values()
            ]

        return devices

    def groups(self):
        """Get all groups."""
        groups = {}

        for group_id in self.groups_data:
            groups[group_id] = RingLightGroup(self, group_id)

        return groups

    def active_alerts(self):
        """Get active alerts."""
        alerts = []
        for alert in self.dings_data:
            expires_at = alert.get("now") + alert.get("expires_in")

            if time() < expires_at:
                alerts.append(alert)

        return alerts
