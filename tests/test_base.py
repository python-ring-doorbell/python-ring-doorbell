# -*- coding:utf-8 -*-
"""Define basic data for unittests."""
import unittest
import requests_mock
from tests.helpers import load_fixture
from ring_doorbell import Ring, Auth

USERNAME = 'foo'
PASSWORD = 'bar'


class RingUnitTestBase(unittest.TestCase):
    """Top level Ring Doorbell test class."""

    @requests_mock.Mocker()
    def setUp(self, mock):
        """Setup unit test and load mock."""
        mock.post('https://oauth.ring.com/oauth/token',
                  text=load_fixture('ring_oauth.json'))
        mock.get('https://api.ring.com/clients_api/ring_devices',
                 text=load_fixture('ring_devices.json'))
        mock.post('https://api.ring.com/clients_api/session',
                  text=load_fixture('ring_session.json'))
        mock.put('https://api.ring.com/clients_api/device',
                 text=load_fixture('ring_devices.json'))

        auth = Auth()
        auth.fetch_token(USERNAME, PASSWORD)
        self.ring = Ring(auth)
