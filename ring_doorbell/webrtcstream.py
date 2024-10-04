"""Python Ring Doorbell RTC Stream handler.

This module is currently experimental and requires a webrtc enabled client
to function.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import ssl
import time
import uuid
from json import dumps as json_dumps
from json import loads as json_loads
from typing import TYPE_CHECKING, Any

from async_timeout import timeout as asyncio_timeout
from websockets.client import connect

from ring_doorbell.const import (
    APP_API_URI,
    RTC_STREAMING_TICKET_ENDPOINT,
    RTC_STREAMING_WEB_SOCKET_ENDPOINT,
)
from ring_doorbell.exceptions import RingError

if TYPE_CHECKING:
    from collections.abc import Coroutine

    from websockets import WebSocketClientProtocol

    from .ring import Ring

_LOGGER = logging.getLogger(__name__)

SDP_ANSWER_TIMEOUT = 1


class RingWebRtcStream:
    """Class to handle a Web RTC Stream."""

    PING_TIME_SECONDS = 5

    def __init__(
        self,
        ring: Ring,
        device_api_id: int,
        *,
        keep_alive_timeout: int | None = 30,
        on_close_callback: Coroutine | None = None,
    ) -> None:
        """Initialise the class."""
        self._ring = ring
        self.device_api_id = device_api_id
        self.sdp: str | None = None
        self.websocket: WebSocketClientProtocol | None = None
        self.do_ping = True
        self.ping_task: asyncio.Task | None = None
        self.read_task: asyncio.Task | None = None
        self.ice_candidates: dict[int, list[str]] = {0: [], 1: [], 2: [], 3: []}
        self.collect_ice_candidates = False
        self.ssl_context: ssl.SSLContext | None = None
        self._sdp_answer_event = asyncio.Event()
        self._keep_alive_timeout = keep_alive_timeout
        self._last_keep_alive: float | None = None
        self._on_close_callback: Coroutine | None = on_close_callback

    @staticmethod
    def get_sdp_session_id(sdp_offer: str) -> str | None:
        """Return the sdp session id from the offer."""
        try:
            lines = sdp_offer.split("\n")
            for line in lines:
                if line[0] == "o":
                    origin = line.split("=")[1]
                    break
            return origin.split(" ")[1]
        except Exception:
            _LOGGER.exception("Error getting session id from offer: %s", sdp_offer)
            return None

    async def generate(self, sdp_offer: str) -> str:
        """Generate the RTC stream."""
        try:
            _LOGGER.debug("Generating stream with sdp offer: %s", sdp_offer)
            req = await self._ring.async_query(
                RTC_STREAMING_TICKET_ENDPOINT,
                method="POST",
                base_uri=APP_API_URI,
            )
            ticket = req.json()["ticket"]

            _LOGGER.debug(
                "Received RTC streaming ticket %s from endpoint, creating websocket",
                ticket,
            )
            ws_uri = RTC_STREAMING_WEB_SOCKET_ENDPOINT.format(uuid.uuid4(), ticket)
            loop = asyncio.get_running_loop()

            if not self.ssl_context:
                # create_default_context() blocks the event loop
                self.ssl_context = await loop.run_in_executor(
                    None, ssl.create_default_context
                )
            self.websocket = await connect(
                ws_uri,
                user_agent_header="android:com.ringapp",
                ssl=self.ssl_context,
            )

            self.dialog_id = str(uuid.uuid4())
            msg = {
                "method": "live_view",
                "dialog_id": self.dialog_id,
                "body": {
                    "doorbot_id": self.device_api_id,
                    "stream_options": {"audio_enabled": True, "video_enabled": True},
                    "sdp": sdp_offer,
                    "type": "offer",
                },
            }
            _LOGGER.debug(
                "Connected to RTC streaming websocket, sending live_view message: %s",
                msg,
            )
            await self.websocket.send(json_dumps(msg))

            message = await self.websocket.recv()
            if TYPE_CHECKING:
                assert isinstance(message, str)

            # Should be session created message
            await self.handle_message(message)

            message2 = await self.websocket.recv()
            if TYPE_CHECKING:
                assert isinstance(message2, str)
            # Should be sdp answer message
            await self.handle_message(message2)

            activate_msg = self.get_session_message("activate_session", {})
            _LOGGER.debug("Sending activate_session message: %s", activate_msg)
            await self.websocket.send(json_dumps(activate_msg))

            options_msg = self.get_session_message(
                "stream_options", {"video_enabled": True, "audio_enabled": True}
            )
            _LOGGER.debug("Sending stream_options message: %s", options_msg)
            await self.websocket.send(json_dumps(options_msg))

            _LOGGER.debug("Starting ping and reader tasks")
            self._last_keep_alive = time.time()
            self.ping_task = asyncio.create_task(self.pinger())
            self.read_task = asyncio.create_task(self.reader())

            if self.collect_ice_candidates:
                _LOGGER.debug(
                    "Waiting %s seconds for ice candidates",
                    SDP_ANSWER_TIMEOUT,
                )
                await asyncio.sleep(SDP_ANSWER_TIMEOUT)
                self.insert_ice_candidates()
            else:
                async with asyncio_timeout(SDP_ANSWER_TIMEOUT):
                    await self._sdp_answer_event.wait()
        except Exception as ex:
            exmsg = "Error generating RTC stream"
            raise RingError(exmsg, ex) from ex

        if not self.sdp:
            exmsg = "Unable to generate RTC stream in time"
            await self.close()
            raise RingError(exmsg)
        _LOGGER.debug("Returning SDP answer: %s", self.sdp)
        return self.sdp

    async def keep_alive(self) -> None:
        """Keep alive the rtc stream."""
        self._last_keep_alive = time.time()

    def get_session_message(self, method: str, body: dict[str, Any]) -> dict[str, Any]:
        """Get a message to send to the session."""
        return {
            "method": method,
            "dialog_id": self.dialog_id,
            "body": {
                **body,
                "doorbot_id": self.device_api_id,
                "session_id": self.session_id,
            },
        }

    async def reader(self) -> None:
        """Read messages from the websocket."""
        if TYPE_CHECKING:
            assert self.websocket
        async for message in self.websocket:
            if TYPE_CHECKING:
                assert isinstance(message, str)
            await self.handle_message(message)

    async def pinger(self) -> None:
        """Ping to keep the session alive."""
        if TYPE_CHECKING:
            assert self.websocket
            assert self._last_keep_alive

        while self.do_ping and (
            self._keep_alive_timeout is None
            or (time.time() - self._last_keep_alive) <= self._keep_alive_timeout
        ):
            await asyncio.sleep(self.PING_TIME_SECONDS)
            ping = self.get_session_message("ping", {})
            await self.websocket.send(json_dumps(ping))

    def handle_ice_message(self, ice_candidate: str, multi_line_index: int) -> None:
        """Handle an ice candidate message."""
        _LOGGER.debug(
            "Ice candidate received, multi_line_index: %s candidate: %s",
            multi_line_index,
            ice_candidate,
        )
        if self.collect_ice_candidates:
            self.ice_candidates[int(multi_line_index)].append(ice_candidate)

    def insert_ice_candidates(self) -> None:
        """Insert an ice candidate into the sdp answer.

        In 2023 the ring api did not return the ice servers in the sdp answer
        and they had to be added as they were received on the web socket.
        As of Sep 2024 they are coming back with the initial sdp answer.
        """
        if TYPE_CHECKING:
            assert self.sdp
        _LOGGER.debug("Inserting ICE candidates into sdp answer")
        self.collect_ice_candidates = False
        for line_index, candidates in self.ice_candidates.items():
            if not candidates:
                continue
            candidates_dict = {
                int(candidate[10:12]): f"a={candidate}\r\n" for candidate in candidates
            }
            candidates_text = ("").join(dict(sorted(candidates_dict.items())).values())
            multi_text = f"a=mid:{line_index}"
            self.sdp = self.sdp.replace(multi_text, candidates_text + multi_text)

    async def close(self) -> None:
        """Close the rtc stream."""
        _LOGGER.debug("Closing the RTC Stream")
        await self._close(closed_by_self=False)

    async def _close(self, *, closed_by_self: bool) -> None:
        """Close the stream."""
        if closed_by_self and (close_cb := self._on_close_callback):
            self._on_close_callback = None
            await close_cb
        self.do_ping = False
        if ping_task := self.ping_task:
            self.ping_task = None
            if not ping_task.done():
                ping_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await ping_task
        if websocket := self.websocket:
            self.websocket = None
            await websocket.close()
        if read_task := self.read_task:
            self.read_task = None
            if not read_task.done():
                await read_task

    async def handle_message(self, message_str: str) -> None:
        """Handle a message from the web socket."""
        if TYPE_CHECKING:
            assert self.websocket
        message = json_loads(message_str)
        method = message["method"]
        if method == "ice":
            self.handle_ice_message(
                message["body"]["ice"], message["body"]["mlineindex"]
            )
        elif method == "sdp":
            sdp = message["body"]["sdp"]
            self.sdp = sdp
            _LOGGER.debug("SDP answer received: %s", sdp)
            self._sdp_answer_event.set()
        elif method == "notification":
            text = message["body"]["text"]
            if text == "camera_connected":
                _LOGGER.debug("Notification received: %s", text)
                camera_options = self.get_session_message(
                    "camera_options", {"stealth_mode": False}
                )
                _LOGGER.debug("Sending camera options: %s", camera_options)
                await self.websocket.send(json_dumps(camera_options))
            else:
                _LOGGER.debug("Received notification: %s", message)
        elif method == "session_created":
            self.session_id = message["body"]["session_id"]
            _LOGGER.debug(
                "Session created: %s___%s", self.session_id[:16], self.session_id[-16:]
            )
        elif method == "close":
            _LOGGER.debug("Close message received: %s", str(message["body"]["reason"]))
            self.do_ping = False
            await self._close(closed_by_self=True)
        elif method == "pong":
            _LOGGER.debug("Pong message received")
        else:
            _LOGGER.debug("Unknown message received with method: %s", method)
