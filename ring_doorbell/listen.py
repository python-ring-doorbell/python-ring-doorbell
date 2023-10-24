"""Module for listening to firebase cloud messages and updating dings"""
import asyncio
import json
import logging
from datetime import datetime

from ring_doorbell.auth import Auth
from ring_doorbell.const import (
    API_URI,
    API_VERSION,
    DEFAULT_LISTEN_EVENT_EXPIRES_IN,
    RING_SENDER_ID,
    SUBSCRIPTION_ENDPOINT,
)
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
        self.connected = False
        self._app_id = auth.get_hardware_id()

        self._credentials = credentials
        self._credentials_updated_callback = credentials_updated_callback

        self._receiver = None
        self._config = FcmPushClientConfig()

        self._subscription_counter = 1

    def add_subscription_to_ring(self, token) -> bool:
        session_patch_data = {
            "device": {
                "metadata": {
                    "api_version": API_VERSION,
                    "device_model": "ring-doorbell",
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
            raise ValueError(
                "Cannot remove the default callback for ring-doorbell with value 1"
            )

        if subscription_id not in self._callbacks:
            raise ValueError(f"ID {subscription_id} is not a valid callback id")

        del self._callbacks[subscription_id]

        if len(self._callbacks) == 0 and self._receiver:
            self._receiver.disconnect()
            self._receiver = None

    def stop_listen(self):
        if self._receiver:
            self.connected = False
            self._receiver.disconnect()
            self._receiver = None

        self._callbacks = {}

    def start_listen(self, callback, init_loop):
        current_loop = None
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            # If the ring object wasn't created with a running loop
            # and there isn't one now then exit
            if not init_loop:
                return

        self.add_notification_callback(callback)

        if not self._receiver:
            self._receiver = FcmPushClient(
                credentials=self._credentials,
                credentials_updated_callback=self._credentials_updated_callback,
                config=self._config,
            )
            fcm_token = self._receiver.checkin(RING_SENDER_ID, self._app_id)
            if not fcm_token:
                _logger.error("Unable to check in to fcm, event listener not started")
                return

            self.add_subscription_to_ring(fcm_token)
            if self.subscribed:
                if current_loop == init_loop:
                    self._receiver.connect(self.on_notification)
                else:
                    loop = current_loop if current_loop else init_loop
                    loop.call_soon_threadsafe(
                        self._receiver.connect, self.on_notification
                    )
                self.connected = True

    def on_notification(self, notification, persistent_id, obj=None):
        gcm_data_json = json.loads(notification["data"]["gcmData"])
        ding = gcm_data_json["ding"]
        kind = gcm_data_json["subtype"]
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
            state="ringing",
        )

        for callback in self._callbacks.values():
            callback(re)
