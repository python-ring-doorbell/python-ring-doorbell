"""The tests for the Ring platform."""
import asyncio
import datetime
import json

import pytest
import requests_mock

from ring_doorbell import Auth, Ring
from ring_doorbell.doorbot import RingDoorBell
from ring_doorbell.exceptions import RingError
from ring_doorbell.listen import can_listen
from tests.conftest import load_fixture

# test_module.py
pytestmark = pytest.mark.skipif(
    can_listen is False, reason=("requires the extra [listen] to be installed")
)


async def test_listen(auth, mocker):
    import firebase_messaging

    disconnectmock = mocker.patch("firebase_messaging.FcmPushClient.stop")
    ring = Ring(auth)
    ring.start_event_listener()
    assert firebase_messaging.FcmPushClient.checkin.call_count == 1
    assert firebase_messaging.FcmPushClient.start.call_count == 1
    assert ring.event_listener.subscribed is True
    assert ring.event_listener.started is True

    cbid = ring.add_event_listener_callback(lambda: 2)
    ring.remove_event_listener_callback(cbid)
    with pytest.raises(RingError, match="ID 10 is not a valid callback id"):
        ring.remove_event_listener_callback(10)

    with pytest.raises(
        RingError,
        match="Cannot remove the default callback for ring-doorbell with value 1",
    ):
        ring.remove_event_listener_callback(1)

    cbid = ring.add_event_listener_callback(lambda: 2)
    del ring.event_listener._callbacks[1]
    ring.remove_event_listener_callback(cbid)
    disconnectmock.assert_called()


async def test_active_dings(auth, mocker):
    import firebase_messaging

    ring = Ring(auth)
    ring.start_event_listener()
    ring.update_dings()
    assert firebase_messaging.FcmPushClient.checkin.call_count == 1
    assert firebase_messaging.FcmPushClient.start.call_count == 1
    assert ring.event_listener.subscribed is True
    assert ring.event_listener.started is True
    num_active = len(ring.active_alerts())
    assert num_active == 3
    alertstoadd = 2
    for i in range(alertstoadd):
        msg = json.loads(load_fixture("ring_listen_fcmdata.json"))
        gcmdata_dict = json.loads(load_fixture("ring_listen_ding.json"))
        created_at = datetime.datetime.utcnow().isoformat(timespec="milliseconds") + "Z"
        gcmdata_dict["ding"]["created_at"] = created_at
        gcmdata_dict["ding"]["id"] = gcmdata_dict["ding"]["id"] + i
        msg["data"]["gcmData"] = json.dumps(gcmdata_dict)
        ring.event_listener.on_notification(msg, "1234567" + str(i))

    dings = ring.active_alerts()
    assert len(dings) == num_active + alertstoadd
    # Test with the same id which should overwrite
    # previous and keep the overall count the same
    for i in range(alertstoadd):
        msg = json.loads(load_fixture("ring_listen_fcmdata.json"))
        gcmdata_dict = json.loads(load_fixture("ring_listen_ding.json"))
        created_at = datetime.datetime.utcnow().isoformat(timespec="milliseconds") + "Z"
        gcmdata_dict["ding"]["created_at"] = created_at
        gcmdata_dict["ding"]["id"] = gcmdata_dict["ding"]["id"] + 1
        msg["data"]["gcmData"] = json.dumps(gcmdata_dict)
        ring.event_listener.on_notification(msg, "1234567" + str(i))

    dings = ring.active_alerts()
    assert len(dings) == num_active + alertstoadd


@pytest.mark.nolistenmock
async def test_listen_subscribe_fail(auth, mocker, requests_mock, caplog):
    checkinmock = mocker.patch(
        "firebase_messaging.FcmPushClient.checkin", return_value="foobar"
    )
    connectmock = mocker.patch("firebase_messaging.FcmPushClient.start")
    mocker.patch("firebase_messaging.FcmPushClient.is_started", return_value=True)

    requests_mock.patch(
        "https://api.ring.com/clients_api/device",
        status_code=401,
        content=b"foobar",
    )

    ring = Ring(auth)
    ring.start_event_listener()
    # Check in gets and error so register is called
    assert checkinmock.call_count == 1
    assert ring.event_listener.subscribed is False
    assert ring.event_listener.started is False
    assert connectmock.call_count == 0

    exp = (
        "Unable to checkin to listen service, "
        + "response was 401 foobar, event listener not started"
    )
    assert (
        len(
            [
                record
                for record in caplog.records
                if record.levelname == "ERROR" and record.message == exp
            ]
        )
        == 1
    )


@pytest.mark.nolistenmock
async def test_listen_gcm_fail(auth, mocker, requests_mock, caplog):
    # Check in gets and error so register is called, the subscribe gets an error
    credentials = json.loads(load_fixture("ring_listen_credentials.json"))
    checkinmock = mocker.patch(
        "firebase_messaging.fcmpushclient.gcm_check_in", return_value=None
    )
    registermock = mocker.patch(
        "firebase_messaging.FcmPushClient.register", return_value=credentials
    )
    connectmock = mocker.patch("firebase_messaging.FcmPushClient.start")
    mocker.patch("firebase_messaging.FcmPushClient.is_started", return_value=True)

    ring = Ring(auth)
    ring.start_event_listener(credentials)
    # Check in gets and error so register is called
    assert checkinmock.call_count == 1
    assert registermock.call_count == 1
    assert ring.event_listener.subscribed is True
    assert ring.event_listener.started is True
    assert connectmock.call_count == 1


@pytest.mark.nolistenmock
async def test_listen_fcm_fail(auth, mocker, requests_mock, caplog):
    checkinmock = mocker.patch(
        "firebase_messaging.FcmPushClient.checkin", return_value=None
    )
    connectmock = mocker.patch("firebase_messaging.FcmPushClient.start")
    mocker.patch("firebase_messaging.FcmPushClient.is_started", return_value=True)

    ring = Ring(auth)
    ring.start_event_listener()
    # Check in gets and error so register is called
    assert checkinmock.call_count == 1

    assert ring.event_listener.subscribed is False
    assert ring.event_listener.started is False
    assert connectmock.call_count == 0
    exp = "Unable to check in to fcm, event listener not started"
    assert (
        len(
            [
                record
                for record in caplog.records
                if record.levelname == "ERROR" and record.message == exp
            ]
        )
        == 1
    )


@pytest.mark.nolistenmock
def test_no_event_loop(auth):
    ring = Ring(auth)
    ring.update_dings()
    assert ring.event_listener is None or ring.event_listener.started is False


async def test_run_in_executor(auth):
    import firebase_messaging

    ring = Ring(auth)
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, ring.start_event_listener)

    assert ring.event_listener and ring.event_listener.started
    assert firebase_messaging.FcmPushClient.checkin.call_count == 1
    assert firebase_messaging.FcmPushClient.start.call_count == 1
