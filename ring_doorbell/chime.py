# coding: utf-8
# vim:sw=4:ts=4:et:
"""Python Ring Chime wrapper."""
import logging

from ring_doorbell.generic import RingGeneric
from ring_doorbell.const import (
    API_URI, CHIMES_ENDPOINT, CHIME_VOL_MIN, CHIME_VOL_MAX,
    LINKED_CHIMES_ENDPOINT, MSG_VOL_OUTBOUND, TESTSOUND_CHIME_ENDPOINT,
    CHIME_TEST_SOUND_KINDS, KIND_DING)

_LOGGER = logging.getLogger(__name__)


class RingChime(RingGeneric):
    """Implementation for Ring Chime."""

    @property
    def family(self):
        """Return Ring device family type."""
        return 'chimes'

    @property
    def battery_life(self):
        """Return battery life."""
        return self._health_attrs.get('battery_percentage')

    @property
    def volume(self):
        """Return if chime volume."""
        return self._attrs.get('settings').get('volume')

    @volume.setter
    def volume(self, value):
        if not ((isinstance(value, int)) and
                (value >= CHIME_VOL_MIN and value <= CHIME_VOL_MAX)):
            _LOGGER.error("%s", MSG_VOL_OUTBOUND.format(CHIME_VOL_MIN,
                                                        CHIME_VOL_MAX))
            return False

        params = {
            'chime[description]': self.name,
            'chime[settings][volume]': str(value)}
        url = API_URI + CHIMES_ENDPOINT.format(self.account_id)
        self._ring.query(url, extra_params=params, method='PUT')
        self.update()
        return True

    @property
    def linked_tree(self):
        """Return doorbell data linked to chime."""
        url = API_URI + LINKED_CHIMES_ENDPOINT.format(self.account_id)
        return self._ring.query(url)

    def test_sound(self, kind=KIND_DING):
        """Play chime to test sound."""
        if kind not in CHIME_TEST_SOUND_KINDS:
            return False
        url = API_URI + TESTSOUND_CHIME_ENDPOINT.format(self.account_id)
        self._ring.query(url, method='POST', extra_params={"kind": kind})
        return True
