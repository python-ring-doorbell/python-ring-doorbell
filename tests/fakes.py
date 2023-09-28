"""The fakes for the Ring platform."""
import pytest

from tests.helpers import load_fixture
import requests_mock

from ring_doorbell import Ring, Auth
from ring_doorbell.const import USER_AGENT


@pytest.fixture
def ring(mock_ring_requests):
    """Return ring object."""
    auth = Auth(USER_AGENT)
    auth.fetch_token("foo", "bar")
    ring = Ring(auth)
    ring.update_data()
    return ring


@pytest.fixture(autouse=True)
def mock_ring_requests():
    with requests_mock.Mocker() as mock:
        mock.post(
            "https://oauth.ring.com/oauth/token", text=load_fixture("ring_oauth.json")
        )
        mock.post(
            "https://api.ring.com/clients_api/session",
            text=load_fixture("ring_session.json"),
        )
        mock.get(
            "https://api.ring.com/clients_api/ring_devices",
            text=load_fixture("ring_devices.json"),
        )
        mock.get(
            "https://api.ring.com/clients_api/chimes/999999/health",
            text=load_fixture("ring_chime_health_attrs.json"),
        )
        mock.get(
            "https://api.ring.com/clients_api/doorbots/987652/health",
            text=load_fixture("ring_doorboot_health_attrs.json"),
        )
        mock.get(
            "https://api.ring.com/clients_api/doorbots/987652/history",
            text=load_fixture("ring_doorbots.json"),
        )
        mock.get(
            "https://api.ring.com/clients_api/dings/active",
            text=load_fixture("ring_ding_active.json"),
        )
        mock.put(
            "https://api.ring.com/clients_api/doorbots/987652/floodlight_light_off",
            text="ok",
        )
        mock.put(
            "https://api.ring.com/clients_api/doorbots/987652/floodlight_light_on",
            text="ok",
        )
        mock.put("https://api.ring.com/clients_api/doorbots/987652/siren_on", text="ok")
        mock.put(
            "https://api.ring.com/clients_api/doorbots/987652/siren_off", text="ok"
        )
        mock.get(
            "https://api.ring.com/groups/v1/locations/mock-location-id/groups",
            text=load_fixture("ring_groups.json"),
        )
        mock.get(
            "https://api.ring.com/groups/v1/locations/"
            + "mock-location-id/groups/mock-group-id/devices",
            text=load_fixture("ring_group_devices.json"),
        )
        mock.post(
            "https://api.ring.com/groups/v1/locations/"
            + "mock-location-id/groups/mock-group-id/devices",
            text="ok",
        )
        mock.patch(
            "https://api.ring.com/devices/v1/devices/987652/settings",
            text="ok",
        )
        mock.get(
            "https://api.ring.com/clients_api/dings/987654321/recording",
            status_code=200,
            content=b"123456",
        )
        mock.get(
            "https://api.ring.com/clients_api/dings/9876543212/recording",
            status_code=200,
            content=b"123456",
        )
        yield mock
