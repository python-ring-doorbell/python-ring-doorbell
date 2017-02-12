# coding: utf-8
# vim:sw=4:ts=4:et:
"""Python Ring Doorbell utils."""
from ring_doorbell.const import NOT_FOUND


def _locator(lst, key, value):
    """Return the position of a match item in list."""
    try:
        return next(index for (index, d) in enumerate(lst)
                    if d[key] == value)
    except StopIteration:
        return NOT_FOUND
