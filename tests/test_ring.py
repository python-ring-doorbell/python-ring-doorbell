# -*- coding: utf-8 -*-
"""The tests for the Ring platform."""
from datetime import datetime
from tests.test_base import RingUnitTestBase
from tests.helpers import load_fixture
import requests_mock


class TestRing(RingUnitTestBase):
    """Unit test for core Ring."""

    @requests_mock.Mocker()
    def test_basic_attributes(self, mock):
        """Test the Ring class and methods."""
        mock.get('https://api.ring.com/clients_api/ring_devices',
                 text=load_fixture('ring_devices.json'))
        mock.get('https://api.ring.com/clients_api/chimes/999999/health',
                 text=load_fixture('ring_chime_health_attrs.json'))
        mock.get('https://api.ring.com/clients_api/doorbots/987652/health',
                 text=load_fixture('ring_doorboot_health_attrs.json'))
        mock.get('https://api.ring.com/clients_api/doorbots/987653/health',
                 text=load_fixture('ring_doorboot_health_attrs_id987653.json'))

        data = self.ring
        self.assertTrue(data.is_connected)
        self.assertIsInstance(data.cache, dict)
        self.assertFalse(data.debug)
        self.assertEqual(1, len(data.chimes))
        self.assertEqual(2, len(data.doorbells))
        self.assertFalse(data._persist_token)
        self.assertEquals('http://localhost/', data._push_token_notify_url)

    @requests_mock.Mocker()
    def test_chime_attributes(self, mock):
        """Test the Ring Chime class and methods."""
        mock.get('https://api.ring.com/clients_api/ring_devices',
                 text=load_fixture('ring_devices.json'))
        mock.get('https://api.ring.com/clients_api/chimes/999999/health',
                 text=load_fixture('ring_chime_health_attrs.json'))

        data = self.ring
        dev = data.chimes[0]

        self.assertEqual('123 Main St', dev.address)
        self.assertNotEqual(99999, dev.account_id)
        self.assertEqual('abcdef123', dev.id)
        self.assertEqual('chime', dev.kind)
        self.assertIsNotNone(dev.latitude)
        self.assertEqual('America/New_York', dev.timezone)
        self.assertEqual(2, dev.volume)
        self.assertEqual('ring_mock_wifi', dev.wifi_name)
        self.assertEqual('good', dev.wifi_signal_category)
        self.assertNotEqual(100, dev.wifi_signal_strength)

    @requests_mock.Mocker()
    def test_doorbell_attributes(self, mock):
        mock.get('https://api.ring.com/clients_api/ring_devices',
                 text=load_fixture('ring_devices.json'))
        mock.get('https://api.ring.com/clients_api/doorbots/987652/history',
                 text=load_fixture('ring_doorbots.json'))
        mock.get('https://api.ring.com/clients_api/doorbots/987652/health',
                 text=load_fixture('ring_doorboot_health_attrs.json'))
        mock.get('https://api.ring.com/clients_api/doorbots/987653/health',
                 text=load_fixture('ring_doorboot_health_attrs_id987653.json'))

        data = self.ring_persistent
        for dev in data.doorbells:
            if not dev.shared:
                self.assertEqual('Front Door', dev.name)
                self.assertEqual(987652, dev.account_id)
                self.assertEqual('123 Main St', dev.address)
                self.assertEqual('lpd_v1', dev.kind)
                self.assertEqual(-70.12345, dev.longitude)
                self.assertEqual('America/New_York', dev.timezone)
                self.assertEqual(1, dev.volume)
                self.assertEqual('online', dev.connection_status)

                self.assertIsInstance(dev.history(limit=1, kind='motion'),
                                      list)
                self.assertEqual(0, len(dev.history(limit=1, kind='ding')))
                self.assertEqual(0, len(dev.history(limit=1,
                                                    kind='ding',
                                                    enforce_limit=True,
                                                    retry=50)))

                self.assertEqual('Mechanical', dev.existing_doorbell_type)
                self.assertTrue(data._persist_token)
                self.assertEqual('ring_mock_wifi', dev.wifi_name)
                self.assertEqual('good', dev.wifi_signal_category)
                self.assertEqual(-58, dev.wifi_signal_strength)

    @requests_mock.Mocker()
    def test_shared_doorbell_attributes(self, mock):
        mock.get('https://api.ring.com/clients_api/ring_devices',
                 text=load_fixture('ring_devices.json'))
        mock.get('https://api.ring.com/clients_api/doorbots/987652/history',
                 text=load_fixture('ring_doorbots.json'))
        mock.get('https://api.ring.com/clients_api/doorbots/987652/health',
                 text=load_fixture('ring_doorboot_health_attrs.json'))
        mock.get('https://api.ring.com/clients_api/doorbots/987653/health',
                 text=load_fixture('ring_doorboot_health_attrs_id987653.json'))

        data = self.ring_persistent
        for dev in data.doorbells:
            if dev.shared:
                self.assertEqual(987653, dev.account_id)
                self.assertEqual(51, dev.battery_life)
                self.assertEqual('123 Second St', dev.address)
                self.assertEqual('lpd_v1', dev.kind)
                self.assertEqual(-70.12345, dev.longitude)
                self.assertEqual('America/New_York', dev.timezone)
                self.assertEqual(5, dev.volume)
                self.assertEqual('Digital', dev.existing_doorbell_type)

    @requests_mock.Mocker()
    def test_doorbell_alerts(self, mock):
        mock.get('https://api.ring.com/clients_api/ring_devices',
                 text=load_fixture('ring_devices.json'))
        mock.get('https://api.ring.com/clients_api/dings/active',
                 text=load_fixture('ring_ding_active.json'))
        mock.get('https://api.ring.com/clients_api/doorbots/987652/health',
                 text=load_fixture('ring_doorboot_health_attrs.json'))
        mock.get('https://api.ring.com/clients_api/doorbots/987653/health',
                 text=load_fixture('ring_doorboot_health_attrs_id987653.json'))

        data = self.ring_persistent
        for dev in data.doorbells:
            self.assertEqual('America/New_York', dev.timezone)

            # call alerts
            dev.check_alerts()

            self.assertIsInstance(dev.alert, dict)
            self.assertIsInstance(dev.alert_expires_at, datetime)
            self.assertTrue(datetime.now() >= dev.alert_expires_at)
            self.assertIsNotNone(dev._ring.cache_file)
