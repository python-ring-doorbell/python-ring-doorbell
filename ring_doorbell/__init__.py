# coding: utf-8
# vim:sw=4:ts=4:et:
"""Python Ring Doorbell wrapper."""
import logging

from ring_doorbell.const import API_URI, DEVICES_ENDPOINT
from ring_doorbell.auth import Auth  # noqa
from ring_doorbell.doorbot import RingDoorBell
from ring_doorbell.chime import RingChime
from ring_doorbell.stickup_cam import RingStickUpCam


_LOGGER = logging.getLogger(__name__)


TYPES = {
    'stickup_cams': RingStickUpCam,
    'chimes': RingChime,
    'doorbots': RingDoorBell,
    'authorized_doorbots':
    lambda ring, description: RingDoorBell(ring, description, shared=True),
}


# pylint: disable=useless-object-inheritance
class Ring(object):
    """A Python Abstraction object to Ring Door Bell."""

    def __init__(self, auth):
        """Initialize the Ring object."""
        self.auth = auth

    def query(self,
              url,
              method='GET',
              extra_params=None,
              json=None,
              timeout=None):
        """Query data from Ring API."""
        return self.auth.query(url, method, extra_params, json, timeout)

    @property
    def devices(self):
        """Return all devices."""
        url = API_URI + DEVICES_ENDPOINT
        data = self.query(url).json()

        devices = {}

        for dev_type, convertor in TYPES.items():
            devices[dev_type] = [
                convertor(self, obj)
                for obj in data.get(dev_type, [])
            ]

        # Backwards compat
        devices['doorbells'] = (
            devices['doorbots'] +
            devices['authorized_doorbots']
        )

        return devices

    @property
    def chimes(self):
        """Return a list of RingDoorChime objects."""
        chimes = self.devices['chimes']
        for chime in chimes:
            chime.update()
        return chimes

    @property
    def stickup_cams(self):
        """Return a list of RingStickUpCam objects."""
        stickup_cams = self.devices['stickup_cams']
        for stickup_cam in stickup_cams:
            stickup_cam.update()
        return stickup_cams

    @property
    def doorbells(self):
        """Return a list of RingDoorBell objects."""
        doorbells = self.devices['doorbells']
        for doorbell in doorbells:
            doorbell.update()
        return doorbells

    def update(self):
        """Refreshes attributes for all linked devices."""
        for device_lst in self.devices.values():
            for device in device_lst:
                if hasattr(device, "update"):
                    _LOGGER.debug("Updating attributes from %s", device.name)
                    getattr(device, "update")
        return True
