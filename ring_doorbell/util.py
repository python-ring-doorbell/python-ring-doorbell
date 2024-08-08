"""Module for common utility functions."""

import datetime
import logging

_logger = logging.getLogger(__name__)


def parse_datetime(datetime_str: str) -> datetime.datetime:
    """Parse a datetime string into a datetime object.

    Ring api has inconsistent datetime string patterns.
    """
    # Check if the datetime string contains a period which precedes 'Z',
    # indicating microseconds
    if "." in datetime_str and datetime_str.endswith("Z"):
        # String contains microseconds and ends with 'Z'
        format_str = "%Y-%m-%dT%H:%M:%S.%fZ"
    else:
        # String does not contain microseconds, should end with 'Z'
        # Could be updated to handle other formats
        format_str = "%Y-%m-%dT%H:%M:%SZ"
    try:
        res = datetime.datetime.strptime(datetime_str, format_str).replace(
            tzinfo=datetime.timezone.utc
        )
    except ValueError:
        _logger.exception(
            "Unable to parse datetime string %s, defaulting to now time", datetime_str
        )
        res = datetime.datetime.now(datetime.timezone.utc)
    return res
