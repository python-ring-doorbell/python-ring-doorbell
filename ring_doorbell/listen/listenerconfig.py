"""Module for RingEventListenerConfig."""

from __future__ import annotations

from firebase_messaging import FcmPushClientConfig


class RingEventListenerConfig(FcmPushClientConfig):
    """Configuration class for event listener."""

    @staticmethod
    def default_config() -> RingEventListenerConfig:
        """Get an instance of the default config."""
        config = RingEventListenerConfig()
        config.server_heartbeat_interval = 60
        config.client_heartbeat_interval = 120
        config.monitor_interval = 15
        # Do not permanently shut down the push client after repeated errors,
        # keep resetting the connection instead.
        config.abort_on_sequential_error_count = None
        return config
