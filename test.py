"""Test module which just runs the cli.  Deprecated as you can either call the cli directly:
python3 ring_doorbell/cli.py
Or use the ring-doorbell script if you installed ring_doorbell via poetry or pip
"""
import sys
from ring_doorbell.cli import cli

if __name__ == "__main__":
    sys.exit(cli())
