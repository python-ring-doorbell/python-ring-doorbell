# -*- coding:utf-8 -*-
"""Define basic data for unittests."""
import os
import unittest
import requests_mock
from tests.helpers import load_fixture

USERNAME = 'foo'
PASSWORD = 'bar'
CACHE = os.path.join(os.path.dirname(__file__), 'cache.db')


class RingUnitTestBase(unittest.TestCase):
    """Top level Ring Doorbell test class."""

    @requests_mock.Mocker()
    def setUp(self, mock):
        """Setup unit test and load mock."""
        from ring_doorbell import Ring
        mock.get('https://api.ring.com/clients_api/ring_devices',
                 text=load_fixture('ring_devices.json'))
        mock.post('https://api.ring.com/clients_api/session',
                  text=load_fixture('ring_session.json'))
        mock.put('https://api.ring.com/clients_api/device',
                 text=load_fixture('ring_devices.json'))

        self.ring = Ring(USERNAME, PASSWORD, cache_file=CACHE)
        self.ring_persistent = \
            Ring(USERNAME, PASSWORD, cache_file=CACHE, persist_token=True)

    def cleanup(self):
        """Cleanup any data created from the tests."""
        self.ring = None
        if os.path.isfile(CACHE):
            os.remove(CACHE)

    def tearDown(self):
        """Stop everything started."""
        self.cleanup()
