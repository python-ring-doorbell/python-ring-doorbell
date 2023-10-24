#!/usr/bin/env python
# vim:sw=4:ts=4:et
# Many thanks to @troopermax <https://github.com/troopermax>
"""DEPRACATED script which just runs the cli videos subcommand.

Deprecated as you can either call the cli directly:

ring_doorbell/cli.py videos

Or use the ring-doorbell script if you installed ring_doorbell via poetry or pip

ring-doorbell videos
"""
import sys

from ring_doorbell.cli import cli

if __name__ == "__main__":
    sys.argv.insert(1, "videos")
    sys.exit(cli())
