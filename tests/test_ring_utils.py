"""The tests utils.py for the Ring platform."""
import os
import unittest
from ring_doorbell.utils import (
    _locator, _clean_cache, _exists_cache, _save_cache, _read_cache)

CACHE = 'tests/cache.db'
FAKE = 'tests/fake.db'
DATA = {'key': 'value'}


class TestUtils(unittest.TestCase):
    """Test utils.py."""

    def test_locator(self):
        """Test _locator method."""
        self.assertEquals(-1, _locator([DATA], 'key', 'bar'))
        self.assertEquals(0, _locator([DATA], 'key', 'value'))

    def test_initiliaze_clean_cache(self):
        """Test _clean_cache method."""
        self.assertTrue(_save_cache(DATA, CACHE))
        self.assertIsInstance(_clean_cache(CACHE), dict)
        os.remove(CACHE)

    def test_exists_cache(self):
        """Test _exists_cache method."""
        self.assertTrue(_save_cache(DATA, CACHE))
        self.assertTrue(_exists_cache(CACHE))
        os.remove(CACHE)

    def test_read_cache(self):
        """Test _read_cache method."""
        self.assertTrue(_save_cache(DATA, CACHE))
        self.assertIsInstance(_read_cache(CACHE), dict)
        os.remove(CACHE)

    def test_read_cache_eoferror(self):
        """Test _read_cache method."""
        open(CACHE, 'a').close()
        self.assertIsInstance(_read_cache(CACHE), dict)
        os.remove(CACHE)
