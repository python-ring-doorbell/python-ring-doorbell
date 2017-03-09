# coding: utf-8
# vim:sw=4:ts=4:et:
"""Python Ring Doorbell utils."""
import os
from ring_doorbell.const import NOT_FOUND

try:
    import cPickle as pickle
except ImportError:
    import pickle


def _locator(lst, key, value):
    """Return the position of a match item in list."""
    try:
        return next(index for (index, d) in enumerate(lst)
                    if d[key] == value)
    except StopIteration:
        return NOT_FOUND


def _save_cache(data, filename):
    """Dump data into a pickle file."""
    try:
        with open(filename, 'wb') as pickle_db:
            pickle.dump(data, pickle_db)
        return True
    except:
        raise


def _read_cache(filename):
    """Read data from a pickle file."""
    try:
        if os.path.isfile(filename):
            return pickle.load(open(filename, 'rb'))
    except:
        raise
    return None
