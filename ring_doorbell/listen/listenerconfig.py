"""Module for RingEventListenerConfig."""
from firebase_messaging import FcmPushClientConfig


class RingEventListenerConfig(FcmPushClientConfig):
    """Configuration class for event listener."""

    @classmethod
    @property
    def default_config(cls) -> "RingEventListenerConfig":
        "Return the default configuration for listening to ring alerts."
        config = RingEventListenerConfig()
        config.server_heartbeat_interval = 60
        config.client_heartbeat_interval = 120
        config.monitor_interval = 15
        return config
