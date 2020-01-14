# coding: utf-8
# vim:sw=4:ts=4:et:
"""Python Ring Doorbell wrapper."""
import logging
from time import time
from uuid import uuid4

from .const import (
    API_URI,
    DEVICES_ENDPOINT,
    NEW_SESSION_ENDPOINT,
    DINGS_ENDPOINT,
)
from .auth import Auth  # noqa
from .doorbot import RingDoorBell
from .chime import RingChime
from .stickup_cam import RingStickUpCam


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

    def update_data(self):
        """Update all data."""
        if self.session is None:
            self.create_session()

        self.update_devices()

        self.update_dings()

    def create_session(self):
        """Create a new Ring session."""
        self.session = self.query(
            NEW_SESSION_ENDPOINT,
            method="POST",
            data={
                "api_version": "9",
                "device[hardware_id]": uuid4().hex,
                "device[os]": "android",
                "device[app_brand]": "ring",
                "device[metadata][device_model]": "KVM",
                "device[metadata][device_name]": "Python",
                "device[metadata][resolution]": "600x800",
                "device[metadata][app_version]": "1.3.806",
                "device[metadata][app_instalation_date]": "",
                "device[metadata][manufacturer]": "Qemu",
                "device[metadata][device_type]": "desktop",
                "device[metadata][architecture]": "desktop",
                "device[metadata][language]": "en",
            },
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

    def active_alerts(self):
        """Get active alerts."""
        alerts = []
        for alert in self.dings_data:
            expires_at = alert.get("now") + alert.get("expires_in")

            if time() < expires_at:
                alerts.append(alert)

        return alerts
