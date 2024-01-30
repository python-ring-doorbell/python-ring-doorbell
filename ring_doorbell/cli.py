# vim:sw=4:ts=4:et
# Many thanks to @troopermax <https://github.com/troopermax>
"""Python Ring command line interface."""
import asyncio
import functools
import getpass
import json
import logging
import select
import sys
import traceback
from datetime import datetime
from pathlib import Path, PurePath

import asyncclick as click

from ring_doorbell import Auth, AuthenticationError, Requires2FAError, Ring, RingEvent
from ring_doorbell.const import CLI_TOKEN_FILE, PACKAGE_NAME, USER_AGENT
from ring_doorbell.listen import can_listen


def _header():
    _bar()
    echo("Ring CLI")


def _bar():
    echo("---------------------------------")


click.anyio_backend = "asyncio"

pass_ring = click.make_pass_decorator(Ring)

cache_file = Path(CLI_TOKEN_FILE)


class ExceptionHandlerGroup(click.Group):
    """Group to capture all exceptions and echo them nicely.

    Idea from https://stackoverflow.com/a/44347763
    """

    def __call__(self, *args, **kwargs):
        """Run the coroutine in the event loop and echo any exceptions."""
        try:
            asyncio.run(self.main(*args, **kwargs))
        except asyncio.CancelledError:
            pass
        except KeyboardInterrupt:
            echo("Cli interrupted with keyboard interrupt")
        except Exception as ex:  # pylint: disable=broad-exception-caught
            echo(f"Got error: {ex!r}")
            traceback.print_exc()


class MutuallyExclusiveOption(click.Option):
    """Prevents incompatable options being supplied, i.e. on and off."""

    def __init__(self, *args, **kwargs):
        self.mutually_exclusive = set(kwargs.pop("mutually_exclusive", []))
        _help = kwargs.get("help", "")
        if self.mutually_exclusive:
            ex_str = ", ".join(self.mutually_exclusive)
            kwargs["help"] = _help + (
                " NOTE: This argument is mutually exclusive with "
                " arguments: [" + ex_str + "]."
            )
        super().__init__(*args, **kwargs)

    async def handle_parse_result(self, ctx, opts, args):
        if self.mutually_exclusive.intersection(opts) and self.name in opts:
            raise click.UsageError(
                "Illegal usage: `{}` is mutually exclusive with "
                "arguments `{}`.".format(self.name, ", ".join(self.mutually_exclusive))
            )

        return await super().handle_parse_result(ctx, opts, args)


echo = click.echo


def token_updated(token):
    """Writes token to file"""
    cache_file.write_text(json.dumps(token), encoding="utf-8")


def _format_filename(device_name, event):
    if not isinstance(event, dict):
        return None

    answered_status = "answered" if event["answered"] else "not_answered"

    filename = "{}_{}_{}_{}_{}".format(
        device_name, event["created_at"], event["kind"], answered_status, event["id"]
    )

    filename = filename.replace(" ", "_").replace(":", ".") + ".mp4"
    return filename


def _do_auth(username, password, user_agent=USER_AGENT):
    if not username:
        username = input("Username: ")

    if not password:
        password = getpass.getpass("Password: ")

    auth = Auth(user_agent, None, token_updated)
    try:
        auth.fetch_token(username, password)
        return auth
    except Requires2FAError:
        auth.fetch_token(username, password, input("2FA Code: "))
        return auth


def _get_ring(username, password, do_update_data, user_agent=USER_AGENT):
    # connect to Ring account
    global cache_file
    if user_agent != USER_AGENT:
        cache_file = Path(user_agent + ".token.cache")
    if cache_file.is_file():
        auth = Auth(
            user_agent,
            json.loads(cache_file.read_text(encoding="utf-8")),
            token_updated,
        )
        ring = Ring(auth)
        do_method = ring.update_data if do_update_data else ring.create_session
        try:
            do_method()
        except AuthenticationError:
            auth = _do_auth(username, password)
            ring = Ring(auth)
            do_method = ring.update_data if do_update_data else ring.create_session
            do_method()
    else:
        auth = _do_auth(username, password, user_agent=user_agent)
        ring = Ring(auth)
        do_method = ring.update_data if do_update_data else ring.create_session
        do_method()

    return ring


@click.group(
    invoke_without_command=True,
    cls=ExceptionHandlerGroup,
)
@click.version_option(package_name="ring_doorbell")
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
@click.option("-d", "--debug", default=False, is_flag=True)
@click.option(
    "--user-agent",
    default=USER_AGENT,
    required=False,
    envvar="RING_USER_AGENT",
    help="User agent to send to ring",
)
@click.pass_context
async def cli(ctx, username, password, debug, user_agent):
    """Command line function."""
    _header()

    logging.basicConfig()
    log_level = logging.DEBUG if debug else logging.INFO
    logger = logging.getLogger(PACKAGE_NAME)
    logger.setLevel(log_level)
    if can_listen:
        logger = logging.getLogger("firebase_messaging")
        logger.setLevel(log_level)

    no_update_commands = ["listen"]
    no_update = ctx.invoked_subcommand in no_update_commands

    ring = _get_ring(username, password, not no_update, user_agent)
    ctx.obj = ring

    if ctx.invoked_subcommand is None:
        return await ctx.invoke(show)


@cli.command(name="list")
@pass_ring
async def list_command(ring: Ring):
    """List ring devices."""
    devices = ring.devices()

    doorbells = devices["doorbots"]
    chimes = devices["chimes"]
    stickup_cams = devices["stickup_cams"]
    other = devices["other"]

    for device in doorbells:
        echo(device)
    for device in chimes:
        echo(device)
    for device in stickup_cams:
        echo(device)
    for device in other:
        echo(device)


@cli.command()
@pass_ring
@click.pass_context
@click.option(
    "--on",
    "turn_on",
    cls=MutuallyExclusiveOption,
    is_flag=True,
    default=None,
    required=False,
    mutually_exclusive=["--off"],
)
@click.option(
    "--off",
    "turn_off",
    cls=MutuallyExclusiveOption,
    is_flag=True,
    default=None,
    required=False,
    mutually_exclusive=["--on"],
)
@click.option(
    "--device-name",
    "-dn",
    required=True,
    default=None,
    help="Name of the ring device",
)
async def motion_detection(ctx, ring: Ring, device_name, turn_on, turn_off):
    """Display ring devices."""
    device = ring.get_device_by_name(device_name)

    if not device:
        echo(
            f"No device with name {device_name} found."
            + " List of found device names (kind) is:"
        )
        return await ctx.invoke(list_command)
    if not device.has_capability("motion_detection"):
        echo(f"{str(device)} is not capable of motion detection")
        return

    state = "on" if device.motion_detection else "off"
    if not turn_on and not turn_off:
        echo(f"{str(device)} has motion detection {state}")
        return
    is_on = device.motion_detection
    if (turn_on and is_on) or (turn_off and not is_on):
        echo(f"{str(device)} already has motion detection {state}")
        return

    device.motion_detection = turn_on if turn_on else False
    state = "on" if device.motion_detection else "off"
    echo(f"{str(device)} motion detection set to {state}")
    return


@cli.command()
@click.option(
    "--device-name",
    "-dn",
    required=False,
    default=None,
    help="Name of device, if ommited shows all devices",
)
@pass_ring
@click.pass_context
async def show(ctx, ring: Ring, device_name):
    """Display ring devices."""
    devices = None

    if device_name and (device := ring.get_device_by_name(device_name)):
        devices = [device]
    elif device_name:
        echo(
            f"No device with name {device_name} found. "
            + "List of found device names (kind) is:"
        )
        return await ctx.invoke(list_command)
    else:
        devices = ring.get_device_list()

    for dev in devices:
        dev.update_health_data()
        echo("Name:       %s" % dev.name)
        echo("Family:     %s" % dev.family)
        echo("ID:         %s" % dev.id)
        echo("Timezone:   %s" % dev.timezone)
        echo("Wifi Name:  %s" % dev.wifi_name)
        echo("Wifi RSSI:  %s" % dev.wifi_signal_strength)
        echo()


@cli.command(name="devices")
@click.option(
    "--device-name",
    "-dn",
    required=False,
    default=None,
    help="Name of device, if ommited shows all devices",
)
@click.option(
    "--json",
    "json_flag",
    required=False,
    is_flag=True,
    help="Output raw json",
)
@pass_ring
@click.pass_context
async def devices_command(ctx, ring: Ring, device_name, json_flag):
    """Get device information."""
    if not json_flag:
        echo(
            "(Pretty format coming soon, if you want json consistently "
            + "from this command provide the --json flag)"
        )
    device_json = None
    if device_name and (device := ring.get_device_by_name(device_name)):
        device_json = ring.devices_data[device.family][device.id]
    elif device_name:
        echo(
            f"No device with name {device_name} found. "
            + "List of found device names (kind) is:"
        )
        return await ctx.invoke(list_command)

    if device_json:
        echo(json.dumps(device_json, indent=2))
    else:
        for device_type in ring.devices_data:
            for device_api_id in ring.devices_data[device_type]:
                echo(
                    json.dumps(ring.devices_data[device_type][device_api_id], indent=2)
                )


@cli.command()
@click.option(
    "--json",
    "json_flag",
    required=False,
    is_flag=True,
    help="Output raw json",
)
@pass_ring
async def dings(ring: Ring, json_flag):
    """Get dings information."""
    if not json_flag:
        echo(
            "(Pretty format coming soon, if you want json consistently "
            + "from this command provide the --json flag)"
        )
    echo(json.dumps(ring.dings_data, indent=2))


@cli.command()
@click.option(
    "--json",
    "json_flag",
    required=False,
    is_flag=True,
    help="Output raw json",
)
@pass_ring
async def groups(ring: Ring, json_flag):
    """Get group information."""
    if not json_flag:
        echo(
            "(Pretty format coming soon, if you want json consistently "
            + "from this command provide the --json flag)"
        )
    if not ring.groups_data:
        echo("No ring device groups setup")
    else:
        for group in ring.groups_data:
            echo(json.dumps(group, indent=2))


@cli.command()
@click.option(
    "--url",
    required=True,
    type=str,
    help="Url to query, i.e. /clients_api/dings/active",
)
@pass_ring
async def raw_query(ring: Ring, url):
    """Directly query a url and return json result."""
    data = ring.query(url).json()
    echo(json.dumps(data, indent=2))


@cli.command(name="history")
@click.option(
    "--device-name",
    "-dn",
    required=False,
    default=None,
    help="Name of device, if ommited shows all devices",
)
@click.option(
    "--limit",
    required=False,
    default=5,
    help="Limit number of records to return",
)
@click.option(
    "--kind",
    required=False,
    default=None,
    type=click.Choice(["ding", "motion"], case_sensitive=False),
    help="Get devices",
)
@click.option(
    "--json",
    "json_flag",
    required=False,
    is_flag=True,
    help="Output raw json",
)
@pass_ring
@click.pass_context
async def history_command(ctx, ring: Ring, device_name, kind, limit, json_flag):
    """Print raw json."""
    if not json_flag:
        echo(
            "(Pretty format coming soon, if you want json consistently "
            + "from this command provide the --json flag)"
        )
    device = ring.get_device_by_name(device_name)
    if not device:
        echo(
            f"No device with name {device_name} found. "
            + "List of found device names (kind) is:"
        )
        return await ctx.invoke(list_command)

    history = device.history(limit=limit, kind=kind, convert_timezone=False)
    echo(json.dumps(history, indent=2))


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
    "-dn",
    default=None,
    required=False,
    help="Name of the ring device, if ommited uses the first device returned",
)
@pass_ring
@click.pass_context
async def videos(
    ctx, ring: Ring, count, download, download_all, max_count, download_to, device_name
):
    """Interact with ring videos."""
    device = None
    if device_name and not (device := ring.get_device_by_name(device_name)):
        echo(
            f"No device with name {device_name} found. "
            + "List of found device names (kind) is:"
        )
        return await ctx.invoke(list_command)
    if device and not device.has_capability("video"):
        echo(f"Device {device.name} is not a video device")
        return
    # return the first device is implemented to be consistent with previous cli version
    if not device:
        if video_devices := ring.video_devices():
            device = video_devices[0]
        else:
            echo(
                "No video devices found. "
                + "List of found device names (with device kind) is:"
            )
            return await ctx.invoke(list_command)

    if not count and not download and not download_all:
        echo("Last recording url is: " + device.recording_url(device.last_recording_id))
        return

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

        echo(f"\tTotal videos: {len(events)}")
        echo(f"\tDing triggered: {ding}")
        echo(f"\tMotion triggered: {motion}")
        echo(f"\tOn-Demand triggered: {on_demand}")

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
            echo(f"\t{counter}/{len(events)} Downloading {filename}")

            device.recording_download(event["id"], filename=filename, override=False)


async def ainput(string: str) -> str:
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, lambda s=string: sys.stdout.write(s + " "))

    def read_with_timeout(timeout):
        if select.select(
            [
                sys.stdin,
            ],
            [],
            [],
            timeout,
        )[0]:
            # line = sys.stdin.next()
            line = sys.stdin.readline()
            return line
        return None

    line = None
    while loop.is_running() and not line:
        line = await loop.run_in_executor(None, functools.partial(read_with_timeout, 1))
    return line


def get_now_str():
    return str(datetime.utcnow())


class _event_handler:  # pylint:disable=invalid-name
    def __init__(self, ring: Ring):
        self.ring = ring

    def on_event(self, event: RingEvent):
        msg = (
            get_now_str()
            + ": "
            + str(event)
            + " : Currently active count = "
            + str(len(self.ring.push_dings_data))
        )
        echo(msg)


@cli.command
@click.option(
    "--credentials-file",
    required=False,
    default="credentials.json",
    help=(
        "File to store push credentials, "
        + "if not provided credentials will be recreated from scratch"
    ),
)
@click.option(
    "--store-credentials/--no-store-credentials",
    default=False,
    help="Whether or not to store the push credentials, default is false",
)
@click.option(
    "--show-credentials",
    default=False,
    is_flag=True,
    help="Whether or not to store the push credentials, default is false",
)
@pass_ring
@click.pass_context
async def listen(
    ctx,
    ring,
    store_credentials,
    credentials_file,
    show_credentials,
):
    """Listen to push notification like the ones sent to your phone."""
    if not can_listen:
        echo("Ring is not configured for listening to notifications!")
        echo("pip install ring_doorbell[listen]")
        return

    from ring_doorbell.listen import (  # pylint:disable=import-outside-toplevel
        RingEventListener,
    )

    def credentials_updated_callback(credentials):
        if store_credentials:
            with open(credentials_file, "w", encoding="utf-8") as f:
                json.dump(credentials, f)
        else:
            echo("New push credentials created:")
            if show_credentials:
                echo(credentials)

    credentials = None
    if store_credentials and Path(credentials_file).is_file():
        # already registered, load previous credentials
        with open(credentials_file, encoding="utf-8") as f:
            credentials = json.load(f)

    event_listener = RingEventListener(ring, credentials, credentials_updated_callback)
    event_listener.start()
    event_listener.add_notification_callback(_event_handler(ring).on_event)

    await ainput("Listening, press enter to cancel\n")

    event_listener.stop()


if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter
