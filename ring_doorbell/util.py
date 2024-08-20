"""Module for common utility functions."""

from __future__ import annotations

import asyncio
import datetime
import logging
from contextlib import suppress
from functools import update_wrapper
from threading import Lock
from typing import TYPE_CHECKING, Any, Callable
from warnings import warn

from typing_extensions import Concatenate, ParamSpec, TypeVar

from ring_doorbell.exceptions import RingError

if TYPE_CHECKING:
    from collections.abc import Coroutine

    from .auth import Auth
    from .generic import RingGeneric
    from .group import RingLightGroup
    from .listen.eventlistener import RingEventListener
    from .ring import Ring

    _T = TypeVar(
        "_T", bound=Auth | Ring | RingGeneric | RingLightGroup | RingEventListener
    )
    _R = TypeVar("_R")
    _P = ParamSpec("_P")

_logger = logging.getLogger(__name__)


def parse_datetime(datetime_str: str) -> datetime.datetime:
    """Parse a datetime string into a datetime object.

    Ring api has inconsistent datetime string patterns.
    """
    # Check if the datetime string contains a period which precedes 'Z',
    # indicating microseconds
    if "." in datetime_str and datetime_str.endswith("Z"):
        # String contains microseconds and ends with 'Z'
        format_str = "%Y-%m-%dT%H:%M:%S.%fZ"
    else:
        # String does not contain microseconds, should end with 'Z'
        # Could be updated to handle other formats
        format_str = "%Y-%m-%dT%H:%M:%SZ"
    try:
        res = datetime.datetime.strptime(datetime_str, format_str).replace(
            tzinfo=datetime.timezone.utc
        )
    except ValueError:
        _logger.exception(
            "Unable to parse datetime string %s, defaulting to now time", datetime_str
        )
        res = datetime.datetime.now(datetime.timezone.utc)
    return res


class _DeprecatedSyncApiHandler:
    def __init__(self, auth: Auth) -> None:
        self.auth = auth
        self._sync_lock = Lock()

    async def run_and_close_session(
        self,
        async_method: Callable[Concatenate[_T, _P], Coroutine[Any, Any, _R]],
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> _R:
        try:
            self._sync_lock.acquire()
            res = await async_method(*args, **kwargs)
        finally:
            with suppress(Exception):
                await self.auth.async_close()
            self._sync_lock.release()

        return res

    @staticmethod
    def check_no_loop(classname: str, method_name: str) -> None:
        current_loop = None
        with suppress(RuntimeError):
            current_loop = asyncio.get_running_loop()
        if current_loop:
            msg = (
                f"You cannot call deprecated sync function {classname}.{method_name} "
                "from within a running event loop."
            )
            raise RingError(msg)

    def get_api_query(
        self,
        class_instance: _T,
        method_name: str,
    ) -> Any:
        """Return deprecated sync api query attribute."""
        classname = type(class_instance).__name__

        def _deprecated_sync_function(
            async_func: Callable[Concatenate[_T, _P], Coroutine[Any, Any, _R]],
        ) -> Callable[_P, _R]:
            def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _R:
                self.check_no_loop(classname, method_name)
                msg = (
                    f"{classname}.{method_name} is deprecated, use "
                    f"{classname}.{async_method_name}"
                )
                warn(msg, DeprecationWarning, stacklevel=1)
                return asyncio.run(
                    self.run_and_close_session(async_func, *args, **kwargs)
                )

            return update_wrapper(wrapper, async_func)

        async_method_name = f"async_{method_name}"
        async_method = getattr(class_instance, async_method_name)
        return _deprecated_sync_function(async_method)

    def get_api_property(
        self,
        class_instance: _T,
        method_name: str,
    ) -> Any:
        """Return deprecated sync api property value."""
        classname = type(class_instance).__name__
        self.check_no_loop(classname, method_name)
        async_method_name = f"async_get_{method_name}"
        msg = (
            f"{classname}.{method_name} is deprecated, use "
            f"{classname}.{async_method_name}"
        )
        warn(msg, DeprecationWarning, stacklevel=1)
        async_method = getattr(class_instance, async_method_name)
        return asyncio.run(self.run_and_close_session(async_method))

    def set_api_property(
        self,
        class_instance: _T,
        property_name: str,
        value: Any,
    ) -> None:
        """Set sync api property value."""
        classname = type(class_instance).__name__

        self.check_no_loop(classname, property_name)
        async_method_name = f"async_set_{property_name}"
        msg = (
            f"{classname}.{property_name} is deprecated, use "
            f"{classname}.{async_method_name}"
        )
        warn(msg, DeprecationWarning, stacklevel=1)
        async_method = getattr(class_instance, async_method_name)
        asyncio.run(self.run_and_close_session(async_method, value))
