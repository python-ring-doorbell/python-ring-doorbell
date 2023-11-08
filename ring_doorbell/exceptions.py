"""ring-doorbell exceptions."""


class RingError(Exception):
    """Base exception for device errors."""


class Requires2FAError(RingError):
    """Exception that 2FA is required."""


class AuthenticationError(RingError):
    """Exception for ring authentication errors."""


class RingTimeout(RingError):
    """Exception for ring authentication errors."""
