# coding: utf-8
# vim:sw=4:ts=4:et:
"""Python Ring Doorbell wrapper."""
import logging

from ring_doorbell import RingDoorBell
#from ring_doorbell.const import (

_LOGGER = logging.getLogger(__name__)

class RingBaseStation(RingDoorBell):
    """Implementation for RingBaseStation."""

    @property
    def family(self):
        """Return Ring device family type."""
        return "base_stations"
