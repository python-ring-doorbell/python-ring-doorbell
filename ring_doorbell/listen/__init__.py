"Package for listener modules."
import sys

try:
    from .eventlistener import RingEventListener
    from .listenerconfig import RingEventListenerConfig

    can_listen = sys.version_info >= (3, 9)  # pylint:disable=invalid-name
except ImportError:  # pragma: no cover
    can_listen = False  # pylint:disable=invalid-name

__all__ = [
    "RingEventListener",
    "RingEventListenerConfig",
]
