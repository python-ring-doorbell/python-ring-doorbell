"""The tests utils.py for the Ring platform."""
import os
import sys
import unittest
from ring_doorbell.utils import (
    _locator, _clean_cache, _exists_cache, _save_cache, _read_cache)
from ring_doorbell.const import CACHE_ATTRS

CACHE = 'tests/cache.db'
FAKE = 'tests/fake.db'
DATA = {'key': 'value'}


class TestUtils(unittest.TestCase):
    """Test utils.py."""

    def cleanup(self):
        """Cleanup any data created from the tests."""
        if os.path.isfile(CACHE):
            os.remove(CACHE)

    def tearDown(self):
        """Stop everything started."""
        self.cleanup()

    def test_locator(self):
        """Test _locator method."""
        self.assertEquals(-1, _locator([DATA], 'key', 'bar'))
        self.assertEquals(0, _locator([DATA], 'key', 'value'))

    def test_initiliaze_clean_cache(self):
        """Test _clean_cache method."""
        self.assertTrue(_save_cache(DATA, CACHE))
        self.assertIsInstance(_clean_cache(CACHE), dict)
        self.cleanup()

    def test_exists_cache(self):
        """Test _exists_cache method."""
        self.assertTrue(_save_cache(DATA, CACHE))
        self.assertTrue(_exists_cache(CACHE))
        self.cleanup()

    def test_read_cache(self):
        """Test _read_cache method."""
        self.assertTrue(_save_cache(DATA, CACHE))
        self.assertIsInstance(_read_cache(CACHE), dict)
        self.cleanup()

    def test_read_cache_eoferror(self):
        """Test _read_cache method."""
        open(CACHE, 'a').close()
        self.assertIsInstance(_read_cache(CACHE), dict)
        self.cleanup()

    def test_read_cache_dict(self):
        """Test _read_cache with expected dict."""
        self.assertTrue(_save_cache(CACHE_ATTRS, CACHE))
        self.assertIsInstance(_read_cache(CACHE), dict)
        self.cleanup()

    def test_general_exceptions(self):
        """Test exception triggers on utils.py"""
        self.assertRaises(TypeError, _clean_cache, True)
        if sys.version_info.major == 2:
            self.assertRaises(TypeError, _read_cache, True)
        else:
            self.assertRaises(OSError, _read_cache, True)
