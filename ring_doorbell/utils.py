# coding: utf-8
# vim:sw=4:ts=4:et:
"""Python Ring Doorbell utils."""
import os
from ring_doorbell.const import CACHE_ATTRS, NOT_FOUND

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


def _clean_cache(filename):
    """Remove filename if pickle version mismatch."""
    if os.path.isfile(filename):
        os.remove(filename)

    # initialize cache since file was removed
    initial_cache_data = CACHE_ATTRS
    _save_cache(initial_cache_data, filename)
    return initial_cache_data


def _exists_cache(filename):
    """Check if filename exists and if is pickle object."""
    return bool(os.path.isfile(filename))


def _save_cache(data, filename):
    """Dump data into a pickle file."""
    with open(filename, 'wb') as pickle_db:
        pickle.dump(data, pickle_db)
    return True


def _read_cache(filename):
    """Read data from a pickle file."""
    try:
        if os.path.isfile(filename):
            data = pickle.load(open(filename, 'rb'))

            # make sure pickle obj has the expected defined keys
            # if not reinitialize cache
            if data.keys() != CACHE_ATTRS.keys():
                raise EOFError
            return data

    except (EOFError, ValueError):
        return _clean_cache(filename)
