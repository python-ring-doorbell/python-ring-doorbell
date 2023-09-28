# vim:sw=4:ts=4:et
# Many thanks to @troopermax <https://github.com/troopermax>
"""Python Ring command line interface."""
import json
import getpass
import asyncio
from pathlib import Path, PurePath
from oauthlib.oauth2 import MissingTokenError, InvalidGrantError
import asyncclick as click

from ring_doorbell.auth import Auth
from ring_doorbell.ring import Ring
from ring_doorbell.const import USER_AGENT, CLI_TOKEN_FILE


def _header():
    _bar()
    echo("Ring CLI")


def _bar():
    echo("---------------------------------")


click.anyio_backend = "asyncio"

pass_ring = click.make_pass_decorator(Ring)


class ExceptionHandlerGroup(click.Group):
    """Group to capture all exceptions and echo them nicely.

    Idea from https://stackoverflow.com/a/44347763
    """

    def __call__(self, *args, **kwargs):
        """Run the coroutine in the event loop and echo any exceptions."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.main(*args, **kwargs))

        except Exception as ex:  # pylint: disable=broad-exception-caught
            echo(f"Got error: {ex!r}")

        finally:
            loop.close()


cache_file = Path(CLI_TOKEN_FILE)

echo = click.echo


def token_updated(token):
    """Writes token to file"""
    cache_file.write_text(json.dumps(token), encoding="utf-8")


def _format_filename(device_name, event):
    if not isinstance(event, dict):
        return None

    if event["answered"]:
        answered_status = "answered"
    else:
        answered_status = "not_answered"

    filename = "{}_{}_{}_{}_{}".format(
        device_name, event["created_at"], event["kind"], answered_status, event["id"]
    )

    filename = filename.replace(" ", "_").replace(":", ".") + ".mp4"
    return filename


def _do_auth(username, password):
    if not username:
        username = input("Username: ")

    if not password:
        password = getpass.getpass("Password: ")

    auth = Auth(USER_AGENT, None, token_updated)
    try:
        auth.fetch_token(username, password)
        return auth
    except MissingTokenError:
        auth.fetch_token(username, password, input("2FA Code: "))
        return auth


def _get_updated_ring(username, password):
    # connect to Ring account
    if cache_file.is_file():
        auth = Auth(
            USER_AGENT,
            json.loads(cache_file.read_text(encoding="utf-8")),
            token_updated,
        )
        ring = Ring(auth)
        try:
            ring.update_data()
        except InvalidGrantError:
            auth = _do_auth(username, password)
            ring = Ring(auth)
            ring.update_data()
    else:
        auth = _do_auth(username, password)
        ring = Ring(auth)
        ring.update_data()

    return ring


@click.group(
    invoke_without_command=True,
    cls=ExceptionHandlerGroup,
)
@click.option(
    "--username",
    default=None,
    required=False,
    envvar="RING_USERNAME",
    help="Username for Ring account.",
)
@click.option(
    "--password",
    default=None,
    required=False,
    envvar="RING_PASSWORD",
    help="Password for Ring account",
)
@click.version_option(package_name="ring_doorbell")
@click.pass_context
async def cli(ctx, username, password):
    """Command line function."""

    _header()

    ring = _get_updated_ring(username, password)
    ctx.obj = ring

    if ctx.invoked_subcommand is None:
        return await ctx.invoke(show)


@cli.command()
@pass_ring
async def show(ring: Ring):
    """Display ring devices."""
    devices = ring.devices()

    # echo(devices)

    doorbells = devices["doorbots"]
    chimes = devices["chimes"]
    stickup_cams = devices["stickup_cams"]

    for device in doorbells:
        echo(device)
    for device in chimes:
        echo(device)
    for device in stickup_cams:
        echo(device)


@cli.command()
@click.option(
    "--count",
    required=False,
    default=False,
    is_flag=True,
    help="Count the number of videos on your Ring account",
)
@click.option(
    "--download-all",
    required=False,
    default=False,
    is_flag=True,
    help="Download all videos on your Ring account",
)
@click.option(
    "--download",
    required=False,
    default=False,
    is_flag=True,
    help="Download videos on your Ring account up to the max-count option",
)
@click.option(
    "--max-count",
    required=False,
    default=300,
    help="Maximum count of videos to count or download from your Ring account",
)
@click.option(
    "--download-to",
    required=False,
    default="./",
    help="Download location ending with a /",
)
@click.option(
    "--device-name",
    required=False,
    default=None,
    help="Name of device, defaults to the first device returned",
)
@pass_ring
@click.pass_context
async def videos(
    ctx, ring, count, download, download_all, max_count, download_to, device_name
):
    """Interact with ring videos."""
    devices = ring.video_devices()

    names_to_idx = {device.name: idx for (idx, device) in enumerate(devices)}
    device = (
        devices[0]
        if device_name not in names_to_idx
        else devices[names_to_idx[device_name]]
    )

    events = None
    if download_all:
        download = True
        max_count = -1

    def _get_events(device, max_count):
        limit = 100 if max_count == -1 else min(100, max_count)
        events = []
        history = device.history(limit=limit)
        while len(history) > 0:
            events += history
            if (len(events) >= max_count and max_count != -1) or len(history) < limit:
                break
            history = device.history(older_than=history[-1]["id"], limit=limit)
        return events

    if count:
        echo(
            f"\tCounting videos linked on your Ring account for {device.name}.\n"
            + "\tThis may take some time....\n"
        )

        events = _get_events(device, max_count)

        motion = len([m["kind"] for m in events if m["kind"] == "motion"])
        ding = len([m["kind"] for m in events if m["kind"] == "ding"])
        on_demand = len([m["kind"] for m in events if m["kind"] == "on_demand"])

        echo("\tTotal videos: {}".format(len(events)))
        echo("\tDing triggered: {}".format(ding))
        echo("\tMotion triggered: {}".format(motion))
        echo("\tOn-Demand triggered: {}".format(on_demand))

    if download:
        if events is None:
            echo(
                "\tGetting videos linked on your Ring account.\n"
                + "\tThis may take some time....\n"
            )
            events = _get_events(device, max_count)

        echo(
            f"\tDownloading {len(events)} videos linked on your Ring account.\n"
            + "\tThis may take some time....\n"
        )
        counter = 0
        for event in events:
            counter += 1
            filename = str(PurePath(download_to, _format_filename(device.name, event)))
            echo("\t{}/{} Downloading {}".format(counter, len(events), filename))

            device.recording_download(event["id"], filename=filename, override=False)


if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter
