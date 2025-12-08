import pytest

from ring_doorbell.webrtcstream import RingWebRtcStream


@pytest.mark.asyncio
async def test_force_correct_sdp_answer_removes_extmap_direction_and_fix_recvonly():
    # create a running loop before initialising the stream (so asyncio.Event works)
    stream = RingWebRtcStream(ring=None, device_api_id=1)

    # Offer has recvonly for audio; answer incorrectly has sendrecv.
    stream.sdp_offer = (
        "m=audio 9 UDP/TLS/RTP/SAVPF 111\r\n"
        "a=recvonly\r\n"
        "a=extmap:1 urn:ietf:params:rtp-hdrext:ssrc-audio-level sendrecv\r\n"
    )

    stream.sdp = (
        "m=audio 9 UDP/TLS/RTP/SAVPF 111\r\n"
        "a=sendrecv\r\n"
        "a=extmap:1 urn:ietf:params:rtp-hdrext:ssrc-audio-level sendrecv\r\n"
    )

    stream.force_correct_sdp_answer()

    # extmap direction should be removed
    assert "extmap:1 urn:ietf:params:rtp-hdrext:ssrc-audio-level sendrecv" not in stream.sdp
    assert "extmap:1 urn:ietf:params:rtp-hdrext:ssrc-audio-level" in stream.sdp

    # sendrecv should be replaced with sendonly because offer was recvonly
    assert "a=sendonly" in stream.sdp
    assert "a=sendrecv" not in stream.sdp
