"""Package for listener modules."""

from .eventlistener import RingEventListener
from .listenerconfig import RingEventListenerConfig

# can_listen used to be checkable to see if the optional listen extra installed.
# Now installed as default.
can_listen = True

__all__ = [
    "RingEventListener",
    "RingEventListenerConfig",
]
