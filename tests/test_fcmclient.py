"""The tests for the Ring push client."""

from __future__ import annotations

import logging
import os
from base64 import urlsafe_b64encode
from typing import Any

import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)
from firebase_messaging import FcmPushClient, FcmRegisterConfig
from firebase_messaging.proto.mcs_pb2 import DataMessageStanza
from http_ece import encrypt
from ring_doorbell.listen.fcmclient import RingFcmPushClient, normalize_webpush_header

APP_ID = "wp:receiver.push.com#test"
PERSISTENT_ID = "0:1234567890123456%0000000000000000"
PAYLOAD = b'{"foo": "bar"}'


def _b64(data: bytes, *, padded: bool = True) -> str:
    encoded = urlsafe_b64encode(data).decode("ascii")
    return encoded if padded else encoded.rstrip("=")


def _public_bytes(key: ec.EllipticCurvePrivateKey) -> bytes:
    return key.public_key().public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)


class PushMessageFactory:
    """Encrypts payloads the way a Web Push sender does."""

    def __init__(self) -> None:
        """Create the key pair and secret of the receiving client."""
        self._receiver_key = ec.generate_private_key(ec.SECP256R1())
        self._auth_secret = os.urandom(16)
        self.credentials = {
            "keys": {
                "private": _b64(
                    self._receiver_key.private_bytes(
                        Encoding.DER, PrivateFormat.PKCS8, NoEncryption()
                    )
                ),
                "public": _b64(_public_bytes(self._receiver_key)),
                "secret": _b64(self._auth_secret),
            },
            "gcm": {"app_id": APP_ID},
        }

    def message(self, *, vapid: bool, padded: bool) -> DataMessageStanza:
        """Return an encrypted message, with or without a VAPID signature key."""
        sender_key = ec.generate_private_key(ec.SECP256R1())
        salt = os.urandom(16)
        crypto_key = f"dh={_b64(_public_bytes(sender_key), padded=padded)}"
        if vapid:
            vapid_key = ec.generate_private_key(ec.SECP256R1())
            crypto_key += f"; p256ecdsa={_b64(_public_bytes(vapid_key), padded=False)}"

        msg = DataMessageStanza()
        msg.persistent_id = PERSISTENT_ID
        msg.raw_data = encrypt(
            PAYLOAD,
            salt=salt,
            private_key=sender_key,
            dh=_public_bytes(self._receiver_key),
            version="aesgcm",
            auth_secret=self._auth_secret,
        )
        for key, value in (
            ("subtype", APP_ID),
            ("crypto-key", crypto_key),
            ("encryption", f"salt={_b64(salt, padded=padded)}"),
        ):
            app_data = msg.app_data.add()
            app_data.key = key
            app_data.value = value
        return msg


@pytest.fixture
def factory() -> PushMessageFactory:
    return PushMessageFactory()


def _client(
    client_class: type[FcmPushClient],
    factory: PushMessageFactory,
    received: list[dict[str, Any]],
) -> FcmPushClient:
    return client_class(
        lambda notification, _persistent_id, _context: received.append(notification),
        FcmRegisterConfig("project", "app", "key", "sender"),
        factory.credentials,
    )


@pytest.mark.parametrize(
    ("header", "name", "expected"),
    [
        # A single parameter, as sent without VAPID.
        ("dh=AAAA", "dh", "dh=AAAA"),
        ("salt=BBBB", "salt", "salt=BBBB"),
        # VAPID adds p256ecdsa. The order of the parameters is not fixed.
        ("dh=AAAA; p256ecdsa=CCCC", "dh", "dh=AAAA"),
        ("p256ecdsa=CCCC;dh=AAAA", "dh", "dh=AAAA"),
        ("salt=BBBB; rs=4096", "salt", "salt=BBBB"),
        # Stripped padding is restored, existing padding is kept.
        ("dh=AAA; p256ecdsa=CCCC", "dh", "dh=AAA="),
        ("salt=BB", "salt", "salt=BB=="),
        ("salt=BB==", "salt", "salt=BB=="),
        # A header without the parameter is passed through.
        ("p256ecdsa=CCCC", "dh", "p256ecdsa=CCCC"),
        ("", "dh", ""),
    ],
)
def test_normalize_webpush_header(header: str, name: str, expected: str) -> None:
    assert normalize_webpush_header(header, name) == expected


@pytest.mark.parametrize(
    ("vapid", "padded"),
    [(False, True), (False, False), (True, True), (True, False)],
)
def test_data_message(factory: PushMessageFactory, vapid, padded) -> None:
    """Messages decrypt with and without a VAPID key or padding."""
    received: list[dict[str, Any]] = []
    client = _client(RingFcmPushClient, factory, received)

    client._handle_data_message(factory.message(vapid=vapid, padded=padded))

    assert received == [{"foo": "bar"}]


def test_vapid_message_fails_without_fix(factory: PushMessageFactory) -> None:
    """Guard that the message used above is the one that breaks the base class.

    This fails once firebase-messaging reads the header parameters by name.
    RingFcmPushClient._app_data_by_key can be removed at that point.
    """
    received: list[dict[str, Any]] = []
    client = _client(FcmPushClient, factory, received)

    with pytest.raises(ValueError, match="Incorrect padding"):
        client._handle_data_message(factory.message(vapid=True, padded=False))

    assert received == []


def test_undecodable_message_is_skipped(
    factory: PushMessageFactory, caplog: pytest.LogCaptureFixture
) -> None:
    """A message that can't be decrypted is logged and doesn't raise."""
    received: list[dict[str, Any]] = []
    client = _client(RingFcmPushClient, factory, received)
    msg = factory.message(vapid=False, padded=True)
    msg.raw_data = b"not an encrypted payload"

    with caplog.at_level(logging.ERROR, logger="ring_doorbell.listen.fcmclient"):
        client._handle_data_message(msg)

    assert received == []
    assert f"Unable to handle push message {PERSISTENT_ID}" in caplog.text
