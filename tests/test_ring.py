"""The tests for the Ring platform."""
from datetime import datetime

import os
import time
import unittest
try:
    import mock
except ImportError:
    from unittest import mock

USERNAME = 'foo'
PASSWORD = 'bar'
CACHE = 'tests/cache.db'


def mocked_requests_get(*args, **kwargs):
    """Mock requests.get invocations."""
    class MockResponse:
        """Class to represent a mocked response."""

        def __init__(self, json_data, status_code):
            """Initialize the mock response class."""
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            """Return the json of the response."""
            return self.json_data

    if str(args[0]).startswith('https://api.ring.com/clients_api/session'):
        return MockResponse({
            "profile": {
                "authentication_token": "12345678910",
                "email": "foo@bar.org",
                "features": {
                    "chime_dnd_enabled": False,
                    "chime_pro_enabled": True,
                    "delete_all_enabled": True,
                    "delete_all_settings_enabled": False,
                    "device_health_alerts_enabled": True,
                    "floodlight_cam_enabled": True,
                    "live_view_settings_enabled": True,
                    "lpd_enabled": True,
                    "lpd_motion_announcement_enabled": False,
                    "multiple_calls_enabled": True,
                    "multiple_delete_enabled": True,
                    "nw_enabled": True,
                    "nw_larger_area_enabled": False,
                    "nw_user_activated": False,
                    "owner_proactive_snoozing_enabled": True,
                    "power_cable_enabled": False,
                    "proactive_snoozing_enabled": False,
                    "reactive_snoozing_enabled": False,
                    "remote_logging_format_storing": False,
                    "remote_logging_level": 1,
                    "ringplus_enabled": True,
                    "starred_events_enabled": True,
                    "stickupcam_setup_enabled": True,
                    "subscriptions_enabled": True,
                    "ujet_enabled": False,
                    "video_search_enabled": False,
                    "vod_enabled": False},
                "first_name": "Foo",
                "id": 999999,
                "last_name": "Bar"}
        }, 201)
    elif str(args[0])\
            .startswith("https://api.ring.com/clients_api/ring_devices"):
        return MockResponse({
            "authorized_doorbots": [
                {
                    "address": "123 Second St",
                    "alerts": {"connection": "online"},
                    "battery_life": 51,
                    "description": "Back Door",
                    "device_id": "aacdef124",
                    "external_connection": False,
                    "features": {
                        "advanced_motion_enabled": False,
                        "motion_message_enabled": False,
                        "motions_enabled": True,
                        "people_only_enabled": False,
                        "shadow_correction_enabled": False,
                        "show_recordings": True},
                    "firmware_version": "1.4.26",
                    "id": 987653,
                    "kind": "lpd_v1",
                    "latitude": 12.000000,
                    "longitude": -70.12345,
                    "motion_snooze": None,
                    "owned": True,
                    "owner": {
                        "email": "foo@bar.org",
                        "first_name": "Foo",
                        "id": 999999,
                        "last_name": "Bar"},
                    "settings": {
                        "chime_settings": {
                            "duration": 3,
                            "enable": True,
                            "type": 1},
                        "doorbell_volume": 5,
                        "enable_vod": True,
                        "live_view_preset_profile": "highest",
                        "live_view_presets": [
                            "low",
                            "middle",
                            "high",
                            "highest"],
                        "motion_announcement": False,
                        "motion_snooze_preset_profile": "low",
                        "motion_snooze_presets": [
                            "none",
                            "low",
                            "medium",
                            "high"]},
                    "subscribed": True,
                    "subscribed_motions": True,
                    "time_zone": "America/New_York"}],
            "chimes": [
                {
                    "address": "123 Main St",
                    "alerts": {"connection": "online"},
                    "description": "Downstairs",
                    "device_id": "abcdef123",
                    "do_not_disturb": {"seconds_left": 0},
                    "features": {"ringtones_enabled": True},
                    "firmware_version": "1.2.3",
                    "id": 999999,
                    "kind": "chime",
                    "latitude": 12.000000,
                    "longitude": -70.12345,
                    "owned": True,
                    "owner": {
                        "email": "foo@bar.org",
                        "first_name": "Marcelo",
                        "id": 999999,
                        "last_name": "Bar"},
                    "settings": {
                        "ding_audio_id": None,
                        "ding_audio_user_id": None,
                        "motion_audio_id": None,
                        "motion_audio_user_id": None,
                        "volume": 2},
                    "time_zone": "America/New_York"}],
            "doorbots": [
                {
                    "address": "123 Main St",
                    "alerts": {"connection": "online"},
                    "battery_life": 4081,
                    "description": "Front Door",
                    "device_id": "aacdef123",
                    "external_connection": False,
                    "features": {
                        "advanced_motion_enabled": False,
                        "motion_message_enabled": False,
                        "motions_enabled": True,
                        "people_only_enabled": False,
                        "shadow_correction_enabled": False,
                        "show_recordings": True},
                    "firmware_version": "1.4.26",
                    "id": 987652,
                    "kind": "lpd_v1",
                    "latitude": 12.000000,
                    "longitude": -70.12345,
                    "motion_snooze": None,
                    "owned": True,
                    "owner": {
                        "email": "foo@bar.org",
                        "first_name": "Foo",
                        "id": 999999,
                        "last_name": "Bar"},
                    "settings": {
                        "chime_settings": {
                            "duration": 3,
                            "enable": True,
                            "type": 0},
                        "doorbell_volume": 1,
                        "enable_vod": True,
                        "live_view_preset_profile": "highest",
                        "live_view_presets": [
                            "low",
                            "middle",
                            "high",
                            "highest"],
                        "motion_announcement": False,
                        "motion_snooze_preset_profile": "low",
                        "motion_snooze_presets": [
                            "none",
                            "low",
                            "medium",
                            "high"]},
                    "subscribed": True,
                    "subscribed_motions": True,
                    "time_zone": "America/New_York"}]
        }, 200)
    elif str(args[0]).startswith("https://api.ring.com/clients_api/doorbots"):
        return MockResponse([{
            "answered": False,
            "created_at": "2017-03-05T15:03:40.000Z",
            "events": [],
            "favorite": False,
            "id": 987654321,
            "kind": "motion",
            "recording": {"status": "ready"},
            "snapshot_url": ""
        }], 200)
    elif str(args[0])\
            .startswith("https://api.ring.com/clients_api/dings/active"):
        return MockResponse([{
            "audio_jitter_buffer_ms": 0,
            "device_kind": "lpd_v1",
            "doorbot_description": "Front Door",
            "doorbot_id": 12345,
            "expires_in": 180,
            "id": 123456789,
            "id_str": "123456789",
            "kind": "ding",
            "motion": False,
            "now": time.time(),
            "optimization_level": 1,
            "protocol": "sip",
            "sip_ding_id": "123456789",
            "sip_endpoints": None,
            "sip_from": "sip:abc123@ring.com",
            "sip_server_ip": "192.168.0.1",
            "sip_server_port": "15063",
            "sip_server_tls": "false",
            "sip_session_id": "28qdvjh-2043",
            "sip_to": "sip:28qdvjh-2043@192.168.0.1:15063;transport=tcp",
            "sip_token": "adecc24a428ed704b2d80adb621b5775755915529639e",
            "snapshot_url": "",
            "state": "ringing",
            "video_jitter_buffer_ms": 0
        }], 200)


class TestRing(unittest.TestCase):
    """Test the Ring."""

    @mock.patch('requests.Session.get', side_effect=mocked_requests_get)
    @mock.patch('requests.Session.post', side_effect=mocked_requests_get)
    def test_basic_attributes(self, get_mock, post_mock):
        """Test the Ring class and methods."""
        from ring_doorbell import Ring

        myring = Ring(USERNAME, PASSWORD, cache_file=CACHE)
        self.assertTrue(myring.is_connected)
        self.assertIsInstance(myring.cache, dict)
        self.assertFalse(myring.debug)
        self.assertEqual(1, len(myring.chimes))
        self.assertEqual(2, len(myring.doorbells))
        self.assertFalse(myring._persist_token)
        self.assertEquals('http://localhost/', myring._push_token_notify_url)


class TestRingChime(unittest.TestCase):
    """Test the Ring Chime object."""

    @mock.patch('requests.Session.get', side_effect=mocked_requests_get)
    @mock.patch('requests.Session.post', side_effect=mocked_requests_get)
    def test_chime_attributes(self, get_mock, post_mock):
        """Test the Ring Chime class and methods."""
        from ring_doorbell import Ring

        myring = Ring(USERNAME, PASSWORD, cache_file=CACHE)
        dev = myring.chimes[0]

        self.assertEqual('123 Main St', dev.address)
        self.assertNotEqual(99999, dev.account_id)
        self.assertEqual('abcdef123', dev.id)
        self.assertEqual('chime', dev.kind)
        self.assertIsNotNone(dev.latitude)
        self.assertEqual('America/New_York', dev.timezone)
        self.assertEqual(2, dev.volume)


class TestRingDoorBell(unittest.TestCase):
    """Test the Ring DoorBell object."""

    def cleanup(self):
        """Cleanup any data created from the tests."""
        if os.path.isfile(CACHE):
            os.remove(CACHE)

    def tearDown(self):
        """Stop everything started."""
        self.cleanup()

    @mock.patch('requests.Session.get', side_effect=mocked_requests_get)
    @mock.patch('requests.Session.post', side_effect=mocked_requests_get)
    def test_doorbell_attributes(self, get_mock, post_mock):
        """Test the Ring DoorBell class and methods."""
        from ring_doorbell import Ring

        myring = Ring(USERNAME, PASSWORD, cache_file=CACHE, persist_token=True)
        for dev in myring.doorbells:
            if not dev.shared:
                self.assertEqual('Front Door', dev.name)
                self.assertEqual(987652, dev.account_id)
                self.assertEqual('123 Main St', dev.address)
                self.assertEqual('lpd_v1', dev.kind)
                self.assertEqual(-70.12345, dev.longitude)
                self.assertEqual('America/New_York', dev.timezone)
                self.assertEqual(1, dev.volume)

                self.assertIsInstance(dev.history(limit=1, kind='motion'),
                                      list)
                self.assertEqual(0, len(dev.history(limit=1, kind='ding')))

                self.assertEqual('Mechanical', dev.existing_doorbell_type)
                self.assertTrue(myring._persist_token)

    @mock.patch('requests.Session.get', side_effect=mocked_requests_get)
    @mock.patch('requests.Session.post', side_effect=mocked_requests_get)
    def test_shared_doorbell_attributes(self, get_mock, post_mock):
        """Test the Ring Shared DoorBell class and methods."""
        from ring_doorbell import Ring

        myring = Ring(USERNAME, PASSWORD, cache_file=CACHE, persist_token=True)
        for dev in myring.doorbells:
            if dev.shared:
                self.assertEqual(987653, dev.account_id)
                self.assertEqual(51, dev.battery_life)
                self.assertEqual('123 Second St', dev.address)
                self.assertEqual('lpd_v1', dev.kind)
                self.assertEqual(-70.12345, dev.longitude)
                self.assertEqual('America/New_York', dev.timezone)
                self.assertEqual(5, dev.volume)
                self.assertEqual('Digital', dev.existing_doorbell_type)

        os.remove(CACHE)


class TestRingDoorBellAlerts(unittest.TestCase):
    """Test the Ring DoorBell alerts."""

    def cleanup(self):
        """Cleanup any data created from the tests."""
        if os.path.isfile(CACHE):
            os.remove(CACHE)

    def tearDown(self):
        """Stop everything started."""
        self.cleanup()

    @mock.patch('requests.Session.get', side_effect=mocked_requests_get)
    @mock.patch('requests.Session.post', side_effect=mocked_requests_get)
    def test_doorbell_alerts(self, get_mock, post_mock):
        """Test the Ring DoorBell alerts."""
        from ring_doorbell import Ring

        myring = Ring(USERNAME, PASSWORD, cache_file=CACHE, persist_token=True)
        for dev in myring.doorbells:
            self.assertEqual('America/New_York', dev.timezone)

            # call alerts
            dev.check_alerts()

            self.assertIsInstance(dev.alert, dict)
            self.assertIsInstance(dev.alert_expires_at, datetime)
            self.assertTrue(datetime.now() <= dev.alert_expires_at)
            self.assertIsNotNone(dev._ring.cache_file)
