"""The tests for the Ring platform."""


def test_other_attributes(ring):
    """Test the Ring Other class and methods."""
    dev = ring.devices()["other"][0]

    assert dev.id != 99999
    assert dev.device_id == "124ba1b3fe1a"
    assert dev.kind == "intercom_handset_audio"
    assert dev.model == "Intercom"
    assert dev.location_id == "mock-location-id"
    assert dev.has_capability("battery") is False
    assert dev.has_capability("open") is True
    assert dev.has_capability("history") is False
    assert dev.timezone == "Europe/Rome"
    assert dev.battery_life == 52
    assert dev.doorbell_volume == 8
    assert dev.mic_volume == 11
    assert dev.clip_length_max == 60
    assert dev.connection_status == "online"
    assert len(dev.allowed_users) == 2
    assert dev.subscribed is True
    assert dev.has_subscription is True
    assert dev.unlock_duration is None
    assert dev.keep_alive_auto == 45.0

    dev.update_health_data()
    assert dev.wifi_name == "ring_mock_wifi"
    assert dev.wifi_signal_category == "good"
    assert dev.wifi_signal_strength != 100


def test_other_controls(ring, requests_mock):
    dev = ring.devices()["other"][0]

    dev.doorbell_volume = 6
    history = list(filter(lambda x: x.method == "PUT", requests_mock.request_history))
    assert history[0].path == "/clients_api/doorbots/185036587"
    assert history[0].query == "doorbot%5bsettings%5d%5bdoorbell_volume%5d=6"

    dev.mic_volume = 10
    dev.voice_volume = 9
    dev.clip_length_max = 30
    dev.keep_alive_auto = 32.2
    history = list(filter(lambda x: x.method == "PATCH", requests_mock.request_history))
    assert history[0].path == "/devices/v1/devices/185036587/settings"
    assert history[0].text == '{"volume_settings": {"mic_volume": 10}}'
    assert history[1].path == "/devices/v1/devices/185036587/settings"
    assert history[1].text == '{"volume_settings": {"voice_volume": 9}}'
    assert history[2].path == "/devices/v1/devices/185036587/settings"
    assert history[2].text == '{"video_settings": {"clip_length_max": 30}}'
    assert history[3].path == "/devices/v1/devices/185036587/settings"
    assert history[3].text == '{"keep_alive_settings": {"keep_alive_auto": 32.2}}'


def test_other_invitations(ring, requests_mock):
    dev = ring.devices()["other"][0]

    dev.invite_access("test@example.com")
    history = list(filter(lambda x: x.method == "POST", requests_mock.request_history))
    assert history[2].path == "/clients_api/locations/mock-location-id/invitations"
    assert history[2].text == (
        '{"invitation": {"doorbot_ids": [185036587],'
        ' "invited_email": "test@example.com", "group_ids": []}}'
    )

    dev.remove_access(123456789)
    history = list(
        filter(lambda x: x.method == "DELETE", requests_mock.request_history)
    )
    assert (
        history[0].path
        == "/clients_api/locations/mock-location-id/invitations/123456789"
    )


def test_other_open_door(ring, requests_mock, mocker):
    dev = ring.devices()["other"][0]

    mocker.patch("uuid.uuid4", return_value="987654321")

    dev.open_door(15)
    history = list(filter(lambda x: x.method == "PUT", requests_mock.request_history))
    assert history[0].path == "/commands/v1/devices/185036587/device_rpc"
    assert history[0].text == (
        '{"command_name": "device_rpc", "request": '
        '{"id": "987654321", "jsonrpc": "2.0", "method": "unlock_door", "params": '
        '{"door_id": 0, "user_id": 15}}}'
    )
