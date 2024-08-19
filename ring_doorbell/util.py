"""Module for common utility functions."""

from __future__ import annotations

import asyncio
import contextlib
import datetime
import logging
from functools import update_wrapper
from typing import TYPE_CHECKING, Any, Callable, TypeVar
from warnings import warn

from typing_extensions import Concatenate, ParamSpec

from ring_doorbell.exceptions import RingError

if TYPE_CHECKING:
    from collections.abc import Coroutine

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


def _check_no_loop(classname: str, method_name: str) -> None:
    current_loop = None
    with contextlib.suppress(RuntimeError):
        current_loop = asyncio.get_running_loop()
    if current_loop:
        msg = (
            f"You cannot call deprecated sync function {classname}.{method_name} "
            "from within a running event loop."
        )
        raise RingError(msg)


_T = TypeVar("_T")
_R = TypeVar("_R")
_P = ParamSpec("_P")


def get_deprecated_sync_api_query(
    class_instance: object,
    method_name: str,
    deprecated_api_calls: set[str],
    deprecated_property_getters: set[str] | None = None,
) -> Any:
    """Return deprecated sync api query attribute."""
    classname = type(class_instance).__name__

    def _deprecated_sync_function(
        async_func: Callable[Concatenate[_T, _P], Coroutine[Any, Any, _R]],
    ) -> Callable[_P, _R]:
        def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            _check_no_loop(classname, method_name)
            msg = (
                f"{classname}.{method_name} is deprecated, use "
                f"{classname}.{async_method_name}"
            )
            warn(msg, DeprecationWarning, stacklevel=1)
            return asyncio.run(async_func(*args, **kwargs))

        return update_wrapper(wrapper, async_func)

    if method_name in deprecated_api_calls:
        async_method_name = f"async_{method_name}"
        async_method = getattr(class_instance, async_method_name)
        return _deprecated_sync_function(async_method)
    if deprecated_property_getters and method_name in deprecated_property_getters:
        _check_no_loop(classname, method_name)
        async_method_name = f"async_get_{method_name}"
        msg = (
            f"{classname}.{method_name} is deprecated, use "
            f"{classname}.{async_method_name}"
        )
        warn(msg, DeprecationWarning, stacklevel=1)
        async_method = getattr(class_instance, async_method_name)
        return asyncio.run(async_method())
    return None


def set_deprecated_sync_api_property(
    class_instance: object,
    property_name: str,
    value: Any,
    deprecated_property_setters: set[str],
) -> bool:
    """Return deprecated sync api query attribute."""
    classname = type(class_instance).__name__

    if property_name in deprecated_property_setters:
        _check_no_loop(classname, property_name)
        async_method_name = f"async_set_{property_name}"
        msg = (
            f"{classname}.{property_name} is deprecated, use "
            f"{classname}.{async_method_name}"
        )
        warn(msg, DeprecationWarning, stacklevel=1)
        async_method = getattr(class_instance, async_method_name)
        asyncio.run(async_method(value))
        return True
    return False
