import pytest
from asyncclick.testing import CliRunner
from tests.helpers import load_fixture

from unittest.mock import MagicMock, DEFAULT
from pathlib import Path
import getpass
from oauthlib.oauth2 import MissingTokenError, InvalidGrantError
from ring_doorbell.cli import (
    cli,
    show,
    videos,
    list_command,
    motion_detection,
)

from ring_doorbell import Auth

# allow mocks to be awaited
# https://stackoverflow.com/questions/51394411/python-object-magicmock-cant-be-used-in-await-expression/51399767#51399767


async def async_magic():
    pass


MagicMock.__await__ = lambda x: async_magic().__await__()


async def test_cli_default(ring):
    runner = CliRunner()
    with runner.isolated_filesystem():
        res = await runner.invoke(
            cli, ["--username", "foo", "--password", "foo"], obj=ring
        )

        expected = (
            "Name:       Downstairs\nFamily:     chimes\nID:"
            + "         999999\nTimezone:   America/New_York\nWifi Name:"
            + "  ring_mock_wifi\nWifi RSSI:  -39\n\n"
        )

        assert res.exit_code == 0
        assert expected in res.output


async def test_show(ring):
    runner = CliRunner()
    with runner.isolated_filesystem():
        res = await runner.invoke(show, obj=ring)

        expected = (
            "Name:       Downstairs\nFamily:     chimes\nID:"
            + "         999999\nTimezone:   America/New_York\nWifi Name:"
            + "  ring_mock_wifi\nWifi RSSI:  -39\n\n"
        )

        assert res.exit_code == 0
        assert expected in res.output


async def test_list(ring):
    runner = CliRunner()
    with runner.isolated_filesystem():
        res = await runner.invoke(list_command, obj=ring)

        expected = "Front Door (lpd_v1)\nDownstairs (chime)\nFront (hp_cam_v1)\n"

        assert res.exit_code == 0
        assert expected in res.output


async def test_videos(ring, mocker):
    runner = CliRunner()

    with runner.isolated_filesystem():
        m = mocker.mock_open()
        ptch = mocker.patch("builtins.open", m, create=True)
        res = await runner.invoke(videos, ["--count", "--download-all"], obj=ring)
        assert ptch.mock_calls[2].args[0] == b"123456"
        assert "Downloading 2 videos" in res.output


@pytest.mark.parametrize(
    "affect_method, exception, file_exists",
    [
        (None, None, False),
        ("ring_doorbell.auth.Auth.fetch_token", MissingTokenError, False),
        ("ring_doorbell.ring.Ring.update_data", InvalidGrantError, True),
    ],
    ids=("No 2FA", "Require 2FA", "Invalid Grant"),
)
async def test_auth(mocker, affect_method, exception, file_exists):
    call_count = 0

    def _raise_once(self, *args, **kwargs):
        nonlocal call_count, exception
        if call_count == 0:
            call_count += 1
            raise exception("Simulated exception")
        call_count += 1

        if hasattr(self, "_update_data"):
            return self._update_data()

        return DEFAULT

    mocker.patch.object(Path, "is_file", return_value=file_exists)
    mocker.patch.object(Path, "read_text", return_value=load_fixture("ring_oauth.json"))
    mocker.patch("builtins.input", return_value="Foo")
    mocker.patch("getpass.getpass", return_value="Foo")
    if affect_method is not None:
        mocker.patch(affect_method, side_effect=_raise_once, autospec=True)

    runner = CliRunner()
    with runner.isolated_filesystem():
        res = await runner.invoke(cli)

        assert res.exit_code == 0


async def test_motion_detection(ring, requests_mock):
    runner = CliRunner()
    with runner.isolated_filesystem():
        res = await runner.invoke(
            motion_detection,
            ["--device-name", "Front"],
            obj=ring,
        )
        expected = "Front (hp_cam_v1) has motion detection off"
        assert res.exit_code == 0
        assert expected in res.output

        res = await runner.invoke(
            motion_detection,
            ["--device-name", "Front", "--off"],
            obj=ring,
        )
        expected = "Front (hp_cam_v1) already has motion detection off"
        assert res.exit_code == 0
        assert expected in res.output

        # Changes the return to indicate that the siren is now on.
        requests_mock.get(
            "https://api.ring.com/clients_api/ring_devices",
            text=load_fixture("ring_devices_updated.json"),
        )

        res = await runner.invoke(
            motion_detection,
            ["--device-name", "Front", "--on"],
            obj=ring,
        )
        expected = "Front (hp_cam_v1) motion detection set to on"
        assert res.exit_code == 0
        assert expected in res.output
