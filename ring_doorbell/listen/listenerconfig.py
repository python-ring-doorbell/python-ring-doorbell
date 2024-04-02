"""Module for RingEventListenerConfig."""

from firebase_messaging import FcmPushClientConfig


class RingEventListenerConfig(FcmPushClientConfig):
    """Configuration class for event listener."""

    @staticmethod
    def default_config() -> "RingEventListenerConfig":
        config = RingEventListenerConfig()
        config.server_heartbeat_interval = 60
        config.client_heartbeat_interval = 120
        config.monitor_interval = 15
        return config
