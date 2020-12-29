# -*- coding: utf-8 -*-
"""The tests for the Ring platform."""
import pytest

from tests.helpers import load_fixture
import requests_mock

from ring_doorbell import Ring, Auth


@pytest.fixture
def ring(mock_ring_requests):
    """Return ring object."""
    auth = Auth("PythonRingDoorbell/0.6")
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
            "https://api.ring.com/groups/v1/locations/mock-location-id/groups/mock-group-id/devices",
            text=load_fixture("ring_group_devices.json"),
        )
        mock.post(
            "https://api.ring.com/groups/v1/locations/mock-location-id/groups/mock-group-id/devices",
            text="ok",
        )
        yield mock


def test_basic_attributes(ring):
    """Test the Ring class and methods."""
    data = ring.devices()
    assert len(data["chimes"]) == 1
    assert len(data["doorbots"]) == 1
    assert len(data["authorized_doorbots"]) == 1
    assert len(data["stickup_cams"]) == 1


def test_chime_attributes(ring):
    """Test the Ring Chime class and methods."""
    dev = ring.devices()["chimes"][0]

    assert dev.address == "123 Main St"
    assert dev.id != 99999
    assert dev.device_id == "abcdef123"
    assert dev.kind == "chime"
    assert dev.model == "Chime"
    assert dev.has_capability("battery") is False
    assert dev.has_capability("volume") is True
    assert dev.latitude is not None
    assert dev.timezone == "America/New_York"
    assert dev.volume == 2

    dev.update_health_data()
    assert dev.wifi_name == "ring_mock_wifi"
    assert dev.wifi_signal_category == "good"
    assert dev.wifi_signal_strength != 100


def test_doorbell_attributes(ring):
    data = ring.devices()
    dev = data["doorbots"][0]
    assert dev.name == "Front Door"
    assert dev.id == 987652
    assert dev.address == "123 Main St"
    assert dev.kind == "lpd_v1"
    assert dev.model == "Doorbell Pro"
    assert dev.has_capability("battery") is False
    assert dev.has_capability("volume") is True
    assert dev.longitude == -70.12345
    assert dev.timezone == "America/New_York"
    assert dev.volume == 1
    assert dev.has_subscription is True
    assert dev.connection_status == "online"

    assert isinstance(dev.history(limit=1, kind="motion"), list)
    assert len(dev.history(limit=1, kind="ding")) == 0
    assert len(dev.history(limit=1, kind="ding", enforce_limit=True, retry=50)) == 0

    assert dev.existing_doorbell_type == "Mechanical"

    dev.update_health_data()

    assert dev.wifi_name == "ring_mock_wifi"
    assert dev.wifi_signal_category == "good"
    assert dev.wifi_signal_strength == -58


def test_shared_doorbell_attributes(ring):
    data = ring.devices()
    dev = data["authorized_doorbots"][0]

    assert dev.id == 987653
    assert dev.battery_life == 51
    assert dev.address == "123 Second St"
    assert dev.kind == "lpd_v1"
    assert dev.model == "Doorbell Pro"
    assert dev.has_capability("battery") is False
    assert dev.has_capability("volume") is True
    assert dev.longitude == -70.12345
    assert dev.timezone == "America/New_York"
    assert dev.volume == 5
    assert dev.existing_doorbell_type == "Digital"


def test_stickup_cam_attributes(ring):
    dev = ring.devices()["stickup_cams"][0]
    assert dev.kind == "hp_cam_v1"
    assert dev.model == "Floodlight Cam"
    assert dev.has_capability("battery") is False
    assert dev.has_capability("light") is True
    assert dev.lights == "off"
    assert dev.siren == 0


def test_stickup_cam_controls(ring, mock_ring_requests):
    dev = ring.devices()["stickup_cams"][0]

    dev.lights = "off"
    dev.lights = "on"
    dev.siren = 0
    dev.siren = 30

    history = list(
        filter(lambda x: x.method == "PUT", mock_ring_requests.request_history)
    )
    assert history[0].path == "/clients_api/doorbots/987652/floodlight_light_off"
    assert history[1].path == "/clients_api/doorbots/987652/floodlight_light_on"
    assert history[2].path == "/clients_api/doorbots/987652/siren_off"
    assert "duration" not in history[2].qs
    assert history[3].path == "/clients_api/doorbots/987652/siren_on"
    assert history[3].qs["duration"][0] == "30"


def test_light_groups(ring):
    group = ring.groups()["mock-group-id"]

    assert group.name == "Landscape"
    assert group.family == "group"
    assert group.device_id == "mock-group-id"
    assert group.location_id == "mock-location-id"
    assert group.model == "Light Group"
    assert group.has_capability("light") is True
    assert group.has_capability("something-else") is False

    assert group.lights is False

    # Attempt turning on lights
    group.lights = True

    # Attempt turning off lights
    group.lights = False

    # Attempt turning on lights for 30 seconds
    group.lights = (True, 30)

    # Attempt setting lights to invalid value
    group.lights = 30
