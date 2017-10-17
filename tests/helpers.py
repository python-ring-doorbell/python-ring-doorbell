"""Helper methods for Ring DoorBell tests."""
import os


def load_fixture(filename):
    """Load a fixture."""
    path = os.path.join(os.path.dirname(__file__), 'fixtures', filename)
    with open(path) as fdp:
        return fdp.read()
