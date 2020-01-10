# coding: utf-8
# vim:sw=4:ts=4:et:
"""Python Ring Doorbell wrapper."""
import logging

from ring_doorbell.const import (
    API_URI, DEVICES_ENDPOINT, RETRY_TOKEN, TIMEOUT)

from ring_doorbell.doorbot import RingDoorBell
from ring_doorbell.chime import RingChime
from ring_doorbell.stickup_cam import RingStickUpCam
from ring_doorbell.auth import Auth


_LOGGER = logging.getLogger(__name__)


# pylint: disable=useless-object-inheritance
class Ring(object):
    """A Python Abstraction object to Ring Door Bell."""

    def __init__(self, username, password,
                 auth_callback=None,
                 debug=False, persist_token=False,
                 push_token_notify_url="http://localhost/", timeout=TIMEOUT):
        """Initialize the Ring object."""
        self.params = None
        self._persist_token = persist_token
        self._push_token_notify_url = push_token_notify_url
        self._timeout = timeout

        self.debug = debug
        self._oauth = Auth()
        self._oauth.fetch_token(username, password, auth_callback)

        self.cache = self._oauth.cache
        self.cache_file = self._oauth.cache_file

    def query(self,
              url,
              attempts=RETRY_TOKEN,
              method='GET',
              raw=False,
              extra_params=None,
              json=None,
              timeout=None):
        """Query data from Ring API."""

        response = self._oauth.query(url, attempts, method,
                                     raw, extra_params, json, timeout)
        return response

    @property
    def devices(self):
        """Return all devices."""
        devs = {}
        devs['chimes'] = self.chimes
        devs['stickup_cams'] = self.stickup_cams
        devs['doorbells'] = self.doorbells
        return devs

    def __devices(self, device_type):
        """Private method to query devices."""
        lst = []
        url = API_URI + DEVICES_ENDPOINT
        try:
            if device_type == 'stickup_cams':
                req = self.query(url).get('stickup_cams')
                for member in list((obj['description'] for obj in req)):
                    lst.append(RingStickUpCam(self, member))

            if device_type == 'chimes':
                req = self.query(url).get('chimes')
                for member in list((obj['description'] for obj in req)):
                    lst.append(RingChime(self, member))

            if device_type == 'doorbells':
                req = self.query(url).get('doorbots')
                for member in list((obj['description'] for obj in req)):
                    lst.append(RingDoorBell(self, member))

                # get shared doorbells, however device is read-only
                req = self.query(url).get('authorized_doorbots')
                for member in list((obj['description'] for obj in req)):
                    lst.append(RingDoorBell(self, member, shared=True))

        except AttributeError:
            pass
        return lst

    @property
    def chimes(self):
        """Return a list of RingDoorChime objects."""
        return self.__devices('chimes')

    @property
    def stickup_cams(self):
        """Return a list of RingStickUpCam objects."""
        return self.__devices('stickup_cams')

    @property
    def doorbells(self):
        """Return a list of RingDoorBell objects."""
        return self.__devices('doorbells')

    def update(self):
        """Refreshes attributes for all linked devices."""
        for device_lst in self.devices.values():
            for device in device_lst:
                if hasattr(device, "update"):
                    _LOGGER.debug("Updating attributes from %s", device.name)
                    getattr(device, "update")
        return True
