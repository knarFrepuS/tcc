#!/usr/bin/env python3
"""evohomeasync provides an async client for the *original* Evohome TCC API.

It is an async port of https://github.com/watchforstock/evohome-client

Further information at: https://evohome-client.readthedocs.io
"""

from __future__ import annotations

from .base import EvohomeClient  # noqa: F401
from .exceptions import (  # noqa: F401
    AuthenticationFailed,
    EvohomeError,
    InvalidSchema,
    RateLimitExceeded,
    RequestFailed,
)

__version__ = "1.2.0"
