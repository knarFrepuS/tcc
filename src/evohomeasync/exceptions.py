#!/usr/bin/env python3
"""evohomeasync provides an async client for the v0 Resideo TCC API."""

from __future__ import annotations


class EvohomeBaseError(Exception):
    """The base exception class for evohome-async."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class EvohomeError(EvohomeBaseError):
    """The base exception class for evohome-async."""


class InvalidSchemaError(EvohomeError):
    """The config/status JSON is invalid (e.g. missing an entity id)."""


class SystemConfigBaseError(EvohomeError):
    """The system configuration is missing/invalid."""


class RequestFailedError(EvohomeError):
    """The API request failed for some reason (no/invalid/unexpected response).

    Could be caused by any aiohttp.ClientError, for example: ConnectionError.  If the
    cause was a ClientResponseError, then the `status` attr will have an integer value.
    """

    def __init__(self, message: str, status: int | None = None) -> None:
        super().__init__(message)
        self.status = status  # iff cause was aiohttp.ClientResponseError


class RateLimitExceededError(RequestFailedError):
    """API request failed because the vendor's API rate limit was exceeded."""


class AuthenticationFailedError(RequestFailedError):
    """Unable to authenticate (unable to obtain an access token).

    The cause could be any FailedRequest, including RateLimitExceeded.
    """
