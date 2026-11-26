"""Tests for Ring's native push descriptions and detection metadata."""

import json

import pytest
from ring_doorbell import Ring
from ring_doorbell.listen import RingEventListener

from tests.conftest import load_alert_v1, load_alert_v2


@pytest.mark.parametrize(
    ("provider", "body", "description"),
    [
        ("llm", "A person walks along a path.", "A person walks along a path."),
        ("default", "There is a Person at your Camera", None),
        (None, "Motion detected", None),
        ("future_provider", "A person walks along a path.", None),
        ("llm", None, None),
    ],
)
def test_native_description_source(auth, provider, body, description):
    """Only Ring's explicitly identified LLM body is a native description."""
    listener = RingEventListener(Ring(auth))
    message = load_alert_v2("camera_motion", 123456782)
    data = json.loads(message["data"]["data"])
    android_config = json.loads(message["data"]["android_config"])
    if provider is not None:
        data["event"]["description_provider"] = provider
    if body is None:
        android_config.pop("body", None)
    else:
        android_config["body"] = body
    data["event"]["ding"]["subtype"] = "motion"
    data["event"]["ding"]["detection_type"] = "human"
    message["data"]["data"] = json.dumps(data)
    message["data"]["android_config"] = json.dumps(android_config)

    event = listener._get_ring_event(message["data"])

    assert event.description == description
    assert event.description_provider == provider
    assert event.detection_type == "human"
    assert event.kind == "motion"
    assert event.state == "motion"
    if description is not None:
        assert description not in repr(event)


def test_missing_detection_metadata_is_not_inferred(auth):
    """A subtype is not a substitute for an absent structured detection label."""
    listener = RingEventListener(Ring(auth))
    message = load_alert_v2("camera_motion", 123456782)
    data = json.loads(message["data"]["data"])
    data["event"]["ding"].pop("detection_type")
    data["event"]["ding"]["subtype"] = "human"
    message["data"]["data"] = json.dumps(data)

    event = listener._get_ring_event(message["data"])

    assert event.detection_type is None
    assert event.description_provider is None
    assert event.description is None
    assert event.state == "human"


def test_unknown_detection_type_is_preserved(auth):
    """New server-provided labels do not require a library enum update."""
    listener = RingEventListener(Ring(auth))
    message = load_alert_v2("camera_motion", 123456782)
    data = json.loads(message["data"]["data"])
    data["event"]["ding"]["detection_type"] = "future_detection"
    message["data"]["data"] = json.dumps(data)

    event = listener._get_ring_event(message["data"])

    assert event.detection_type == "future_detection"


def test_legacy_event_has_no_native_description(auth):
    """Legacy notification text must not be relabeled as an AI description."""
    listener = RingEventListener(Ring(auth))
    message = load_alert_v1("doorbot_ding", 123456782)

    event = listener._get_legacy_ring_event(json.loads(message["data"]["gcmData"]))

    assert event.description is None
    assert event.description_provider is None
    assert event.detection_type is None


async def test_delayed_description_updates_only_its_original_event(auth, mocker):
    """A delayed native description replaces its initial alert without a new event."""
    ring = Ring(auth)
    listener = RingEventListener(ring)
    await listener.start()
    callback = mocker.Mock()
    listener.add_notification_callback(callback)
    try:
        message = load_alert_v2("camera_motion", 123456782)
        listener._on_notification(message, "initial")
        initial = callback.call_args.args[0]

        other_message = load_alert_v2("camera_motion", 123456782, ding_id_inc=1)
        listener._on_notification(other_message, "other")
        other = callback.call_args.args[0]

        data = json.loads(message["data"]["data"])
        android_config = json.loads(message["data"]["android_config"])
        data["event"]["description_provider"] = "llm"
        android_config["body"] = "A person walks along a path."
        message["data"]["data"] = json.dumps(data)
        message["data"]["android_config"] = json.dumps(android_config)
        listener._on_notification(message, "description")
        update = callback.call_args.args[0]

        assert update.get_key() == initial.get_key()
        assert update.is_update is True
        assert callback.call_count == 3
        ring.dings_data = [
            {
                "id": initial.id,
                "doorbot_id": initial.doorbot_id,
                "doorbot_description": initial.device_name,
                "device_kind": initial.device_kind,
                "now": initial.now,
                "expires_in": initial.expires_in,
                "kind": initial.kind,
                "state": initial.state,
            }
        ]
        alerts = {event.id: event for event in ring.active_alerts()}
        assert len(alerts) == 2
        assert alerts[initial.id].description == "A person walks along a path."
        assert alerts[initial.id].is_update is True
        assert alerts[other.id].description is None
        assert alerts[other.id].is_update is False
    finally:
        await listener.stop()
