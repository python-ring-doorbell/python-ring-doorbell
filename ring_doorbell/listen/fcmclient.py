"""Push client that copes with the Web Push headers Ring sends."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from firebase_messaging import FcmPushClient

if TYPE_CHECKING:
    from firebase_messaging.proto.mcs_pb2 import DataMessageStanza

_logger = logging.getLogger(__name__)

# The app data keys holding a Web Push header, and the parameter of that
# header which firebase-messaging needs to decrypt the message.
_WEBPUSH_HEADER_PARAMS = {"crypto-key": "dh", "encryption": "salt"}


def normalize_webpush_header(header: str, name: str) -> str:
    """Reduce a Web Push header to its ``name`` parameter, with padding.

    ``Crypto-Key`` and ``Encryption`` are lists of ``;`` separated parameters
    in no fixed order (RFC 8291 section 4), and their base64url values may
    come without ``=`` padding. A sender that signs its pushes with VAPID
    sends ``dh=<key>; p256ecdsa=<key>``.

    firebase-messaging expects exactly ``<name>=<padded value>``, so that is
    what is returned. A header without the parameter is returned unchanged.
    """
    for segment in header.split(";"):
        param, sep, value = segment.strip().partition("=")
        if sep and param == name:
            value = value.strip().rstrip("=")
            return f"{name}={value}{'=' * (-len(value) % 4)}"
    return header


class RingFcmPushClient(FcmPushClient):
    """FcmPushClient that survives the messages Ring sends.

    firebase-messaging slices the key and the salt off the Web Push headers
    by position. With a VAPID signed push that leaves the second parameter in
    the key, decoding raises, and because the exception is raised before the
    message is acknowledged the client shuts down and gets the same message
    again on every start.
    """

    def _app_data_by_key(
        self,
        p: DataMessageStanza,
        key: str,
        do_not_raise: bool = False,  # noqa: FBT001, FBT002
    ) -> str:
        value = super()._app_data_by_key(p, key, do_not_raise)
        if (name := _WEBPUSH_HEADER_PARAMS.get(key)) is not None:
            return normalize_webpush_header(value, name)
        return value

    def _handle_data_message(self, msg: DataMessageStanza) -> None:
        # Returning normally lets the caller acknowledge the message. If this
        # raised, the client would shut down without acknowledging and the
        # server would deliver the same message again after every restart.
        try:
            super()._handle_data_message(msg)
        except Exception:
            _logger.exception(
                "Unable to handle push message %s, skipping it", msg.persistent_id
            )
