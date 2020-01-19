#!/usr/bin/env python
# vim:sw=4:ts=4:et
# Many thanks to @troopermax <https://github.com/troopermax>

import json
import getpass
import argparse
from pathlib import Path
from ring_doorbell import Ring, Auth
from oauthlib.oauth2 import MissingTokenError


def _header():
    _bar()
    print("Ring CLI")


def _bar():
    print("---------------------------------")


cache_file = Path("test_token.cache")


def token_updated(token):
    cache_file.write_text(json.dumps(token))


def _format_filename(event):
    if not isinstance(event, dict):
        return

    if event["answered"]:
        answered_status = "answered"
    else:
        answered_status = "not_answered"

    filename = "{}_{}_{}_{}".format(
        event["created_at"], event["kind"], answered_status, event["id"]
    )

    filename = filename.replace(" ", "_").replace(":", ".") + ".mp4"
    return filename


def main():

    parser = argparse.ArgumentParser(
        description="Ring Doorbell",
        epilog="https://github.com/tchellomello/python-ring-doorbell",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-u", "--username", dest="username", type=str, help="username for Ring account"
    )

    parser.add_argument(
        "-p", "--password", type=str, dest="password", help="username for Ring account"
    )

    parser.add_argument(
        "--count",
        action="store_true",
        default=False,
        help="count the number of videos on your Ring account",
    )

    parser.add_argument(
        "--download-all",
        action="store_true",
        default=False,
        help="download all videos on your Ring account",
    )

    args = parser.parse_args()
    _header()

    # connect to Ring account
    if cache_file.is_file():
        auth = Auth("RingCLI/0.6", json.loads(cache_file.read_text()), token_updated)
    else:
        if not args.username:
            args.username = input("Username: ")

        if not args.password:
            args.password = getpass.getpass("Password: ")

        auth = Auth("RingCLI/0.6", None, token_updated)
        try:
            auth.fetch_token(args.username, args.password)
        except MissingTokenError:
            auth.fetch_token(args.username, args.password, input("2FA Code: "))

    ring = Ring(auth)
    ring.update_data()
    devices = ring.devices()
    doorbell = devices["doorbots"][0]

    _bar()

    if args.count:
        print(
            "\tCounting videos linked on your Ring account.\n"
            + "\tThis may take some time....\n"
        )

        events = []
        counter = 0
        history = doorbell.history(limit=100)
        while len(history) > 0:
            events += history
            counter += len(history)
            history = doorbell.history(older_than=history[-1]["id"])

        motion = len([m["kind"] for m in events if m["kind"] == "motion"])
        ding = len([m["kind"] for m in events if m["kind"] == "ding"])
        on_demand = len([m["kind"] for m in events if m["kind"] == "on_demand"])

        print("\tTotal videos: {}".format(counter))
        print("\tDing triggered: {}".format(ding))
        print("\tMotion triggered: {}".format(motion))
        print("\tOn-Demand triggered: {}".format(on_demand))

        # already have all events in memory
        if args.download_all:
            counter = 0
            print(
                "\tDownloading all videos linked on your Ring account.\n"
                + "\tThis may take some time....\n"
            )

            for event in events:
                counter += 1
                filename = _format_filename(event)
                print("\t{}/{} Downloading {}".format(counter, len(events), filename))

                doorbell.recording_download(
                    event["id"], filename=filename, override=False
                )

    if args.download_all and not args.count:
        print(
            "\tDownloading all videos linked on your Ring account.\n"
            + "\tThis may take some time....\n"
        )
        history = doorbell.history(limit=100)

        while len(history) > 0:
            print(
                "\tProcessing and downloading the next" + " videos".format(len(history))
            )

            counter = 0
            for event in history:
                counter += 1
                filename = _format_filename(event)
                print("\t{}/{} Downloading {}".format(counter, len(history), filename))

                doorbell.recording_download(
                    event["id"], filename=filename, override=False
                )

            history = doorbell.history(limit=100, older_than=history[-1]["id"])


if __name__ == "__main__":
    main()
