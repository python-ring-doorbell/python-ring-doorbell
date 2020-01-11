"""The tests utils.py for the Ring platform."""
import unittest
from ring_doorbell.utils import _locator

DATA = {'key': 'value'}


class TestUtils(unittest.TestCase):
    """Test utils.py."""

    def test_locator(self):
        """Test _locator method."""
        self.assertEqual(-1, _locator([DATA], 'key', 'bar'))
        self.assertEqual(0, _locator([DATA], 'key', 'value'))
