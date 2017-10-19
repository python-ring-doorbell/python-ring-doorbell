# coding: utf-8
# vim:sw=4:ts=4:et:
"""Python Ring Doorbell wrapper."""
import logging

from ring_doorbell import RingDoorBell
from ring_doorbell.const import (
    API_URI, LIGHTS_ENDPOINT, MSG_ALLOWED_VALUES, MSG_VOL_OUTBOUND,
    SIREN_DURATION_MIN, SIREN_DURATION_MAX, SIREN_ENDPOINT)

_LOGGER = logging.getLogger(__name__)


class RingStickUpCam(RingDoorBell):
    """Implementation for RingStickUpCam."""

    @property
    def family(self):
        """Return Ring device family type."""
        return 'stickup_cams'

    @property
    def lights(self):
        """Return lights status."""
        return self._attrs.get('led_status')

    @lights.setter
    def lights(self, state):
        """Control the lights."""
        values = ['on', 'off']
        if state not in values:
            _LOGGER.error("%s", MSG_ALLOWED_VALUES.format(', '.join(values)))
            return False

        url = API_URI + LIGHTS_ENDPOINT.format(self.account_id, state)
        self._ring.query(url, method='PUT')
        self.update()
        return True

    @property
    def siren(self):
        """Return siren status."""
        if self._attrs.get('siren_status'):
            return self._attrs.get('siren_status').get('seconds_remaining')
        return None

    @siren.setter
    def siren(self, duration):
        """Control the siren."""
        if not ((isinstance(duration, int)) and
                (duration >= SIREN_DURATION_MIN and
                 duration <= SIREN_DURATION_MAX)):
            _LOGGER.error("%s", MSG_VOL_OUTBOUND.format(SIREN_DURATION_MIN,
                                                        SIREN_DURATION_MAX))
            return False

        if duration > 0:
            state = 'on'
            params = {'duration': duration}
        else:
            state = 'off'
            params = {}
        url = API_URI + SIREN_ENDPOINT.format(self.account_id, state)
        self._ring.query(url, extra_params=params, method='PUT')
        self.update()
        return True
