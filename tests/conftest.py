"""Test configuration for the Ring platform."""
import json
import os
import re
from time import time

import pytest
import requests_mock

from ring_doorbell import Auth, Ring
from ring_doorbell.const import USER_AGENT
from ring_doorbell.listen import can_listen


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "nolistenmock: mark test to not want the autouse listenmock"
    )


@pytest.fixture
def auth(requests_mock):
    """Return auth object."""
    auth = Auth(USER_AGENT)
    auth.fetch_token("foo", "bar")
    return auth


@pytest.fixture
def ring(auth):
    """Return updated ring object."""
    ring = Ring(auth)
    ring.update_data()
    return ring


def _set_dings_to_now(active_dings):
    dings = json.loads(active_dings)
    for ding in dings:
        ding["now"] = time()

    return json.dumps(dings)


def load_fixture(filename):
    """Load a fixture."""
    path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(path) as fdp:
        return fdp.read()


@pytest.fixture(autouse=True)
def listen_mock(mocker, request):
    if not can_listen or "nolistenmock" in request.keywords:
        return

    mocker.patch("firebase_messaging.FcmPushClient.checkin", return_value="foobar")
    mocker.patch("firebase_messaging.FcmPushClient.start")
    mocker.patch("firebase_messaging.FcmPushClient.is_started", return_value=True)


# setting the fixture name to requests_mock allows other
# tests to pull in request_mock and append uris
@pytest.fixture(autouse=True, name="requests_mock")
def requests_mock_fixture():
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
            re.compile(r"https:\/\/api\.ring\.com\/clients_api\/chimes\/\d+\/health"),
            text=load_fixture("ring_chime_health_attrs.json"),
        )
        mock.get(
            re.compile(r"https:\/\/api\.ring\.com\/clients_api\/doorbots\/\d+\/health"),
            text=load_fixture("ring_doorboot_health_attrs.json"),
        )
        mock.get(
            "https://api.ring.com/clients_api/doorbots/987652/history",
            text=load_fixture("ring_doorbot_history.json"),
        )
        mock.get(
            "https://api.ring.com/clients_api/dings/active",
            text=_set_dings_to_now(load_fixture("ring_ding_active.json")),
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
            re.compile(
                r"https:\/\/api\.ring\.com\/devices\/v1\/devices\/\d+\/settings"
            ),
            text="ok",
        )
        mock.get(
            re.compile(r"https:\/\/api\.ring\.com\/clients_api\/dings\/\d+\/recording"),
            # "https://api.ring.com/clients_api/dings/987654321/recording",
            status_code=200,
            content=b"123456",
        )
        mock.get(
            "https://api.ring.com/clients_api/dings/9876543212/recording",
            status_code=200,
            content=b"123456",
        )
        mock.patch(
            "https://api.ring.com/clients_api/device",
            status_code=204,
            content=b"",
        )
        mock.put(
            "https://api.ring.com/clients_api/doorbots/185036587",
            status_code=204,
            content=b"",
        )
        mock.get(
            "https://api.ring.com/devices/v1/devices/185036587/settings",
            text=load_fixture("ring_intercom_settings.json"),
        )
        mock.get(
            "https://api.ring.com/clients_api/locations/mock-location-id/users",
            text=load_fixture("ring_intercom_users.json"),
        )
        mock.post(
            "https://api.ring.com/clients_api/locations/mock-location-id/invitations",
            text="ok",
        )
        mock.delete(
            (
                "https://api.ring.com/clients_api/locations/"
                "mock-location-id/invitations/123456789"
            ),
            text="ok",
        )
        requestid = "44529542-3ed7-41da-807e-c170a01bac1d"
        mock.put(
            "https://api.ring.com/commands/v1/devices/185036587/device_rpc",
            text='{"result": {"code": 0}, "id": "' + requestid + '", "jsonrpc": "2.0"}',
        )
        yield mock
