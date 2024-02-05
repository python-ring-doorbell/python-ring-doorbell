"""The tests for the Ring platform."""


def test_basic_attributes(ring):
    """Test the Ring class and methods."""
    data = ring.devices()
    assert len(data["chimes"]) == 1
    assert len(data["doorbots"]) == 1
    assert len(data["authorized_doorbots"]) == 1
    assert len(data["stickup_cams"]) == 1
    assert len(data["other"]) == 1


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
    assert dev.has_capability("history") is False
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
    assert dev.has_capability("history") is True
    assert dev.longitude == -70.12345
    assert dev.timezone == "America/New_York"
    assert dev.volume == 1
    assert dev.has_subscription is True
    assert dev.connection_status == "online"

    assert isinstance(dev.history(limit=1, kind="motion"), list)
    assert len(dev.history(kind="ding")) == 1
    assert len(dev.history(limit=1, kind="motion")) == 2
    assert len(dev.history(limit=1, kind="motion", enforce_limit=True, retry=50)) == 1

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
    assert dev.has_capability("history") is True
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
    assert dev.has_capability("history") is True
    assert dev.lights == "off"
    assert dev.siren == 0


def test_stickup_cam_controls(ring, requests_mock):
    dev = ring.devices()["stickup_cams"][0]

    dev.lights = "off"
    dev.lights = "on"
    dev.siren = 0
    dev.siren = 30

    history = list(filter(lambda x: x.method == "PUT", requests_mock.request_history))
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
    assert group.group_id == "mock-group-id"
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


def test_motion_detection_enable(ring, requests_mock):
    dev = ring.devices()["doorbots"][0]

    dev.motion_detection = True
    dev.motion_detection = False

    history = list(filter(lambda x: x.method == "PATCH", requests_mock.request_history))
    assert history[len(history) - 2].path == "/devices/v1/devices/987652/settings"
    assert (
        history[len(history) - 2].text
        == '{"motion_settings": {"motion_detection_enabled": true}}'
    )
    assert history[len(history) - 1].path == "/devices/v1/devices/987652/settings"
    assert (
        history[len(history) - 1].text
        == '{"motion_settings": {"motion_detection_enabled": false}}'
    )

    active_dings = ring.active_alerts()

    assert len(active_dings) == 3
    assert len(ring.active_alerts()) == 3
