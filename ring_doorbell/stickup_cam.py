# coding: utf-8
# vim:sw=4:ts=4:et:
"""Python Ring Doorbell wrapper."""
import logging

from ring_doorbell import RingDoorBell
from ring_doorbell.const import (
    API_URI, LIGHTS_ENDPOINT, MSG_ALLOWED_VALUES, MSG_VOL_OUTBOUND,
    FLOODLIGHT_CAM_KINDS, INDOOR_CAM_KINDS, SPOTLIGHT_CAM_BATTERY_KINDS,
    SPOTLIGHT_CAM_WIRED_KINDS, STICKUP_CAM_KINDS,
    STICKUP_CAM_BATTERY_KINDS, STICKUP_CAM_WIRED_KINDS,
    SIREN_DURATION_MIN, SIREN_DURATION_MAX, SIREN_ENDPOINT)

_LOGGER = logging.getLogger(__name__)


class RingStickUpCam(RingDoorBell):
    """Implementation for RingStickUpCam."""

    @property
    def family(self):
        """Return Ring device family type."""
        return 'stickup_cams'

    @property
    def model(self):
        """Return Ring device model name."""
        # ignore R1705: Unnecessary "elif" after "return" (no-else-return)
        if self.kind in FLOODLIGHT_CAM_KINDS:
            return 'Floodlight Cam'
        elif self.kind in INDOOR_CAM_KINDS:
            return 'Indoor Cam'
        elif self.kind in SPOTLIGHT_CAM_BATTERY_KINDS:
            return 'Spotlight Cam {}'.format(
                self._attrs.get('ring_cam_setup_flow', 'battery').title())
        elif self.kind in SPOTLIGHT_CAM_WIRED_KINDS:
            return 'Spotlight Cam {}'.format(
                self._attrs.get('ring_cam_setup_flow', 'wired').title())
        elif self.kind in STICKUP_CAM_KINDS:
            return 'Stick Up Cam'
        elif self.kind in STICKUP_CAM_BATTERY_KINDS:
            return 'Stick Up Cam Battery'
        elif self.kind in STICKUP_CAM_WIRED_KINDS:
            return 'Stick Up Cam Wired'
        return None

    def has_capability(self, capability):
        """Return if device has specific capability."""
        # ignore R1705: Unnecessary "elif" after "return" (no-else-return)
        if capability == 'battery':
            return self.kind in (SPOTLIGHT_CAM_BATTERY_KINDS +
                                 STICKUP_CAM_KINDS +
                                 STICKUP_CAM_BATTERY_KINDS)
        elif capability == 'light':
            return self.kind in (FLOODLIGHT_CAM_KINDS +
                                 SPOTLIGHT_CAM_BATTERY_KINDS +
                                 SPOTLIGHT_CAM_WIRED_KINDS)
        elif capability == 'siren':
            return self.kind in (FLOODLIGHT_CAM_KINDS +
                                 INDOOR_CAM_KINDS +
                                 SPOTLIGHT_CAM_BATTERY_KINDS +
                                 SPOTLIGHT_CAM_WIRED_KINDS +
                                 STICKUP_CAM_BATTERY_KINDS +
                                 STICKUP_CAM_WIRED_KINDS)
        return False

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
                (SIREN_DURATION_MIN <= duration <= SIREN_DURATION_MAX)):
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
