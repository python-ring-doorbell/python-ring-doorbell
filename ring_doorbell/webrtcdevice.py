"""WebRTC live-stream support shared by Ring devices that offer live view."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ring_doorbell.const import ICE_SERVERS
from ring_doorbell.exceptions import RingError
from ring_doorbell.webrtcstream import RingWebRtcMessageCallback, RingWebRtcStream

if TYPE_CHECKING:
    from ring_doorbell.ring import Ring


class RingWebRtcMixin:
    """WebRTC stream management for devices that support live view.

    Used by doorbells/cameras and by intercoms (``RingOther``), which use the
    same signalling as cameras.
    """

    _ring: Ring
    device_api_id: int
    _webrtc_streams: dict[str, RingWebRtcStream]

    async def generate_webrtc_stream(
        self, sdp_offer: str, *, keep_alive_timeout: int | None = 30
    ) -> str:
        """Generate the rtc stream."""
        if session_id := RingWebRtcStream.get_sdp_session_id(sdp_offer):

            async def _close_callback() -> None:
                # The stream is already closing itself; only forget it.
                self._webrtc_streams.pop(session_id, None)

            stream = RingWebRtcStream(
                self._ring,
                self.device_api_id,
                keep_alive_timeout=keep_alive_timeout,
                on_close_callback=_close_callback,
            )
            sdp_answer = await stream.generate(sdp_offer)
            # generate will raise if no sdp answer as no callback passed
            assert sdp_answer  # noqa: S101
            self._webrtc_streams[session_id] = stream
            return sdp_answer
        msg = "Unable to generate the stream, could not extract session id from offer."
        raise RingError(msg)

    async def generate_async_webrtc_stream(
        self,
        sdp_offer: str,
        session_id: str,
        on_message_callback: RingWebRtcMessageCallback,
        *,
        keep_alive_timeout: int | None = 60 * 5,
    ) -> None:
        """Generate the rtc stream. Will callback with answers and ICE candidates."""

        async def _close_callback() -> None:
            # Called from the stream's own reader task when Ring ends the
            # session. The stream is already closing itself, so only forget
            # it: calling close() again would re-enter _close().
            self._webrtc_streams.pop(session_id, None)

        stream = RingWebRtcStream(
            self._ring,
            self.device_api_id,
            on_message_callback=on_message_callback,
            keep_alive_timeout=keep_alive_timeout,
            on_close_callback=_close_callback,
        )
        self._webrtc_streams[session_id] = stream
        await stream.generate(sdp_offer)

    async def on_webrtc_candidate(
        self, session_id: str, candidate: str, multi_line_index: int
    ) -> None:
        """Send an ICE candidate."""
        if stream := self._webrtc_streams.get(session_id):
            await stream.on_ice_candidate(candidate, multi_line_index)
        else:
            msg = "Ice candidate received before stream has been created."
            raise RingError(msg)

    async def close_webrtc_stream(self, session_id: str) -> None:
        """Close the rtc stream."""
        stream = self._webrtc_streams.pop(session_id, None)
        if stream:
            await stream.close()

    def sync_close_webrtc_stream(self, session_id: str) -> None:
        """Close the rtc stream."""
        stream = self._webrtc_streams.pop(session_id, None)
        if stream:
            stream.sync_close()

    async def keep_alive_webrtc_stream(self, sdp_session_id: str) -> None:
        """Keep alive the rtc stream."""
        stream = self._webrtc_streams.get(sdp_session_id, None)
        if stream:
            await stream.keep_alive()

    def get_ice_servers(self) -> list[str]:
        """Return the ICE servers."""
        return ICE_SERVERS
