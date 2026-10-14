"""The tests for the Ring platform."""

import datetime
import json
import time

import pytest
from freezegun.api import FrozenDateTimeFactory
from ring_doorbell import Ring
from ring_doorbell.exceptions import RingError
from ring_doorbell.listen import RingEventListener

from tests.conftest import load_alert_v1, load_alert_v2, load_fixture


async def test_listen(auth, mocker):
    import firebase_messaging

    ring = Ring(auth)
    listener = RingEventListener(ring)

    await listener.start()
    assert firebase_messaging.FcmPushClient.checkin_or_register.call_count == 1
    assert firebase_messaging.FcmPushClient.start.call_count == 1
    assert listener.subscribed is True
    assert listener.started is True

    with pytest.raises(RingError, match="ID 10 is not a valid callback id"):
        listener.remove_notification_callback(10)

    with pytest.raises(
        RingError,
        match="Cannot remove the default callback for ring-doorbell with value 1",
    ):
        listener.remove_notification_callback(1)

    cbid = listener.add_notification_callback(lambda: 2)
    del listener._callbacks[1]
    listener.remove_notification_callback(cbid)


async def test_active_dings(auth, mocker):
    import firebase_messaging

    ring = Ring(auth)
    listener = RingEventListener(ring)
    await listener.start()
    assert firebase_messaging.FcmPushClient.checkin_or_register.call_count == 1
    assert firebase_messaging.FcmPushClient.start.call_count == 1
    assert listener.subscribed is True
    assert listener.started is True
    num_active = len(ring.active_alerts())
    assert num_active == 0
    alertstoadd = 2
    for i in range(alertstoadd):
        msg = load_alert_v1("doorbot_ding", 123456781, ding_id_inc=i)
        listener._on_notification(msg, "1234567" + str(i))
        msg = load_alert_v2("camera_motion", 123456782, ding_id_inc=i)
        listener._on_notification(msg, "1234567" + str(i))
        msg = load_alert_v1("intercom_unlock", 185036587, ding_id_inc=i)
        listener._on_notification(msg, "1234567" + str(i))

    dings = ring.active_alerts()
    assert len(dings) == num_active + alertstoadd * 3
    # Test with the same id which should overwrite
    # previous and keep the overall count the same
    for i in range(alertstoadd):
        msg = load_alert_v1("doorbot_ding", 123456781, ding_id_inc=i)
        listener._on_notification(msg, "1234567" + str(i))
        msg = load_alert_v2("camera_motion", 123456782, ding_id_inc=i)
        listener._on_notification(msg, "1234567" + str(i))

    dings = ring.active_alerts()
    assert len(dings) == num_active + alertstoadd * 3
    await listener.stop()


async def test_ding_expirey(auth, mocker, freezer: FrozenDateTimeFactory):
    ring = Ring(auth)
    listener = RingEventListener(ring)
    await listener.start()

    assert listener.subscribed is True
    assert listener.started is True

    assert len(ring.push_dings_data) == 0
    assert len(ring.active_alerts()) == 0

    alertstoadd = 2
    for i in range(alertstoadd):
        msg = load_alert_v1("doorbot_ding", 123456781, ding_id_inc=i)
        listener._on_notification(msg, "1234567" + str(i))
        msg = load_alert_v2("camera_motion", 123456782, ding_id_inc=i)
        listener._on_notification(msg, "1234567" + str(i))
        msg = load_alert_v1("intercom_unlock", 185036587, ding_id_inc=i)
        listener._on_notification(msg, "1234567" + str(i))

    assert len(ring.push_dings_data) == 6
    assert len(ring.active_alerts()) == 6

    freezer.tick(datetime.timedelta(minutes=5))

    msg = load_alert_v1("doorbot_ding", 123456781, ding_id_inc=alertstoadd + 1)
    listener._on_notification(msg, "123456781" + str(alertstoadd + 1))

    assert len(ring.push_dings_data) == 1
    assert len(ring.active_alerts()) == 1


@pytest.mark.nolistenmock
async def test_listen_subscribe_fail(auth, mocker, caplog, putpatch_status_fixture):
    checkinmock = mocker.patch(
        "firebase_messaging.FcmPushClient.checkin_or_register", return_value="foobar"
    )
    connectmock = mocker.patch("firebase_messaging.FcmPushClient.start")
    mocker.patch("firebase_messaging.FcmPushClient.is_started", return_value=True)

    putpatch_status_fixture.overrides["https://api.ring.com/clients_api/device"] = 401

    ring = Ring(auth)
    listener = RingEventListener(ring)
    await listener.start()
    # Check in gets and error so register is called
    assert checkinmock.call_count == 1
    assert listener.subscribed is False
    assert listener.started is False
    assert connectmock.call_count == 0

    exp = (
        "Unable to checkin to listen service, "
        "response was 401 , event listener not started"
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
async def test_listen_gcm_fail(auth, mocker):
    # Check in gets and error so register is called, the subscribe gets an error
    credentials = json.loads(load_fixture("ring_listen_credentials.json"))
    checkinmock = mocker.patch(
        "firebase_messaging.fcmregister.FcmRegister.gcm_check_in", return_value=None
    )
    registermock = mocker.patch(
        "firebase_messaging.fcmregister.FcmRegister.register", return_value=credentials
    )
    connectmock = mocker.patch("firebase_messaging.FcmPushClient.start")
    mocker.patch("firebase_messaging.FcmPushClient.is_started", return_value=True)

    ring = Ring(auth)
    listener = RingEventListener(ring, credentials)
    await listener.start()
    # Check in gets and error so register is called
    assert checkinmock.call_count == 1
    assert registermock.call_count == 1
    assert listener.subscribed is True
    assert listener.started is True
    assert connectmock.call_count == 1


@pytest.mark.nolistenmock
async def test_listen_fcm_fail(auth, mocker, caplog):
    checkinmock = mocker.patch(
        "firebase_messaging.FcmPushClient.checkin_or_register", return_value=None
    )
    connectmock = mocker.patch("firebase_messaging.FcmPushClient.start")
    mocker.patch("firebase_messaging.FcmPushClient.is_started", return_value=True)

    ring = Ring(auth)
    listener = RingEventListener(ring)
    await listener.start()
    # Check in gets and error so register is called
    assert checkinmock.call_count == 1

    assert listener.subscribed is False
    assert listener.started is False
    assert connectmock.call_count == 0
    exp = "Ring listener unable to check in to fcm, event listener not started"
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


async def test_legacy_ding_kind(auth, mocker):
    ring = Ring(auth)
    listener = RingEventListener(ring)
    events = []
    listener.add_notification_callback(events.append)

    msg = load_alert_v1("doorbot_ding", 123456781)
    listener._on_notification(msg, "12345671")

    assert len(events) == 1
    assert events[0].kind == "ding"
    assert events[0].state == "ringing"


async def test_unparseable_notification_does_not_raise(auth, mocker, caplog):
    ring = Ring(auth)
    listener = RingEventListener(ring)
    events = []
    listener.add_notification_callback(events.append)

    msg = load_alert_v2("camera_motion", 123456782)
    data = json.loads(msg["data"]["data"])
    del data["event"]["ding"]["id"]
    msg["data"]["data"] = json.dumps(data)

    listener._on_notification(msg, "12345671")

    assert events == []
    assert "Unable to parse fcm message data" in caplog.text

    # The listener keeps processing subsequent valid notifications
    listener._on_notification(load_alert_v2("camera_motion", 123456782), "12345672")
    assert len(events) == 1


async def test_default_config_does_not_abort_on_errors(auth):
    listener = RingEventListener(Ring(auth))
    assert listener._config.abort_on_sequential_error_count is None


async def test_periodic_session_refresh_repeats(auth, mocker, caplog):
    ring = Ring(auth)
    listener = RingEventListener(ring)
    listener.SESSION_REFRESH_INTERVAL = -1
    listener.SESSION_REFRESH_RETRY_INTERVAL = 0
    listener.started = True
    listener.fcm_token = "foobar"
    ring.session_refresh_time = time.monotonic()

    calls = 0

    async def _create_session() -> None:
        nonlocal calls
        calls += 1
        if calls == 1:
            msg = "Session error"
            raise RingError(msg)
        ring.session_refresh_time = time.monotonic()
        if calls == 3:
            listener.started = False

    mocker.patch.object(ring, "async_create_session", side_effect=_create_session)
    subscribe = mocker.patch.object(listener, "add_subscription_to_ring")

    await listener._periodic_session_refresh()

    assert calls == 3
    assert subscribe.call_count == 2
    assert "Error refreshing ring session" in caplog.text
