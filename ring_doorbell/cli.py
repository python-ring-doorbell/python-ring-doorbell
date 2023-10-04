# vim:sw=4:ts=4:et
# Many thanks to @troopermax <https://github.com/troopermax>
"""Python Ring command line interface."""
import json
import getpass
import asyncio
import logging
from pathlib import Path, PurePath
from oauthlib.oauth2 import MissingTokenError, InvalidGrantError, InvalidClientError
import asyncclick as click
from ring_doorbell.auth import Auth
from ring_doorbell.ring import Ring
from ring_doorbell.const import USER_AGENT, CLI_TOKEN_FILE, PACKAGE_NAME


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
        except (InvalidGrantError, InvalidClientError):
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
@click.pass_context
async def cli(ctx, username, password, debug):
    """Command line function."""

    _header()

    logging.basicConfig()
    log_level = logging.DEBUG if debug else logging.INFO
    logger = logging.getLogger(PACKAGE_NAME)
    logger.setLevel(log_level)

    ring = _get_updated_ring(username, password)
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

    for device in doorbells:
        echo(device)
    for device in chimes:
        echo(device)
    for device in stickup_cams:
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
        echo(f"{str(device_name)} is not capable of motion detection")
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
            for device_id in ring.devices_data[device_type]:
                echo(json.dumps(ring.devices_data[device_type][device_id], indent=2))


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
    """Directly query a url."""
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
