"""Module for listening to firebase cloud messages and updating dings"""
import json
import logging
import time
from datetime import datetime

from ring_doorbell.auth import Auth
from ring_doorbell.const import (
    API_URI,
    API_VERSION,
    DEFAULT_LISTEN_EVENT_EXPIRES_IN,
    KIND_DING,
    KIND_MOTION,
    PUSH_ACTION_DING,
    PUSH_ACTION_MOTION,
    RING_SENDER_ID,
    SUBSCRIPTION_ENDPOINT,
)
from ring_doorbell.exceptions import RingError
from ring_doorbell.generic import RingEvent

try:
    from firebase_messaging import FcmPushClient, FcmPushClientConfig

    can_listen = True  # pylint:disable=invalid-name
except ImportError:  # pragma: no cover
    can_listen = False  # pylint:disable=invalid-name

_logger = logging.getLogger(__name__)


class RingEventListener:
    """Class to connect to firebase cloud messaging."""

    def __init__(self, auth: Auth, credentials=None, credentials_updated_callback=None):
        self._auth = auth

        self._callbacks = {}
        self.subscribed = False
        self.started = False
        self._app_id = auth.get_hardware_id()
        self._device_model = auth.get_device_model()

        self._credentials = credentials
        self._credentials_updated_callback = credentials_updated_callback

        self._receiver = None
        self._config = FcmPushClientConfig()
        self._config.server_heartbeat_interval = 60
        self._config.client_heartbeat_interval = 120

        self._subscription_counter = 1

    def add_subscription_to_ring(self, token) -> bool:
        # "hardware_id": self.auth.get_hardware_id(),
        session_patch_data = {
            "device": {
                "metadata": {
                    "api_version": API_VERSION,
                    "device_model": self._device_model,
                    "pn_service": "fcm",
                },
                "os": "android",
                "push_notification_token": token,
            }
        }
        resp = self._auth.query(
            API_URI + SUBSCRIPTION_ENDPOINT,
            method="PATCH",
            json=session_patch_data,
            raise_for_status=False,
        )
        if resp.status_code != 204:
            _logger.error(
                "Unable to checkin to listen service, "
                + "response was %s %s, event listener not started",
                resp.status_code,
                resp.text,
            )
            self.subscribed = False
            return

        self.subscribed = True

    def add_notification_callback(self, callback):
        sub_id = self._subscription_counter

        self._callbacks[sub_id] = callback
        self._subscription_counter += 1

        return sub_id

    def remove_notification_callback(self, subscription_id):
        if subscription_id == 1:
            raise RingError(
                "Cannot remove the default callback for ring-doorbell with value 1"
            )

        if subscription_id not in self._callbacks:
            raise RingError(f"ID {subscription_id} is not a valid callback id")

        del self._callbacks[subscription_id]

        if len(self._callbacks) == 0 and self._receiver:
            self._receiver.stop()
            self._receiver = None

    def stop_listen(self):
        if self._receiver:
            self.started = False
            self._receiver.stop()
            self._receiver = None

        self._callbacks = {}

    def start_listen(
        self, callback, *, listen_loop=None, callback_loop=None, timeout=30
    ):
        if not self._receiver:
            self._receiver = FcmPushClient(
                credentials=self._credentials,
                credentials_updated_callback=self._credentials_updated_callback,
                config=self._config,
            )
        fcm_token = self._receiver.checkin(RING_SENDER_ID, self._app_id)
        if not fcm_token:
            _logger.error("Unable to check in to fcm, event listener not started")
            return False

        self.add_subscription_to_ring(fcm_token)
        if self.subscribed:
            self.add_notification_callback(callback)

            self._receiver.start(
                self.on_notification,
                listen_event_loop=listen_loop,
                callback_event_loop=callback_loop,
            )

            start = time.time()
            now = start
            while not self._receiver.is_started() and now - start < timeout:
                time.sleep(0.1)
                now = time.time()
            self.started = self._receiver.is_started()

        return self.subscribed and self.started

    def on_notification(self, notification, persistent_id, obj=None):
        gcm_data_json = json.loads(notification["data"]["gcmData"])

        if "ding" not in gcm_data_json:
            if "community_alert" not in gcm_data_json:
                _logger.warning(
                    "Unexpected alert type in gcmData.  Full message is:\n%s",
                    json.dumps(notification),
                )
            return

        ding = gcm_data_json["ding"]
        action = gcm_data_json["action"]
        subtype = gcm_data_json["subtype"]
        if action.lower() == PUSH_ACTION_MOTION.lower():
            kind = KIND_MOTION
            state = subtype
        elif action.lower == PUSH_ACTION_DING.lower():
            kind = KIND_DING
            state = "ringing"
        else:
            kind = action
            state = subtype

        created_at = ding["created_at"]
        create_seconds = (
            datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%f%z")
        ).timestamp()
        re = RingEvent(
            id=ding["id"],
            kind=kind,
            doorbot_id=ding["doorbot_id"],
            device_name=ding["device_name"],
            device_kind=ding["device_kind"],
            now=create_seconds,
            expires_in=DEFAULT_LISTEN_EVENT_EXPIRES_IN,
            state=state,
        )

        for callback in self._callbacks.values():
            callback(re)
