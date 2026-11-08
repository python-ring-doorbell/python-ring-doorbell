"""Tests for WebRTC stream handling shared by doorbells and intercoms."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

from ring_doorbell.doorbot import RingDoorBell
from ring_doorbell.other import RingOther
from ring_doorbell.webrtcdevice import RingWebRtcMixin
from ring_doorbell.webrtcstream import RingWebRtcMessage, RingWebRtcStream


def test_intercom_has_webrtc_methods():
    for cls in (RingDoorBell, RingOther):
        assert issubclass(cls, RingWebRtcMixin)
        for name in (
            "generate_webrtc_stream",
            "generate_async_webrtc_stream",
            "on_webrtc_candidate",
            "close_webrtc_stream",
            "sync_close_webrtc_stream",
            "keep_alive_webrtc_stream",
            "get_ice_servers",
        ):
            assert callable(getattr(cls, name))


async def test_server_close_does_not_await_reader_from_itself():
    """Ring's close message is handled inside the reader task.

    _close() must not await read_task from within it, and the close reason
    must reach the message callback.
    """
    messages: list[RingWebRtcMessage] = []
    other = RingOther(MagicMock(), 1)
    stream = RingWebRtcStream(MagicMock(), 1, on_message_callback=messages.append)

    async def _close_callback() -> None:
        other._webrtc_streams.pop("session", None)

    stream._on_close_callback = _close_callback
    stream.websocket = AsyncMock()
    stream.is_alive = True
    other._webrtc_streams["session"] = stream

    async def reader() -> None:
        await stream.handle_close_message(
            {"body": {"reason": {"code": 1, "text": "bye"}}}
        )

    stream.read_task = asyncio.create_task(reader())
    await stream.read_task

    assert "session" not in other._webrtc_streams
    assert [(m.error_code, m.error_message) for m in messages] == [(1, "bye")]
