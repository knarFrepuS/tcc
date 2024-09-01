#!/usr/bin/env python3
"""evohome-async - test config."""

import os
import tempfile
from collections.abc import AsyncGenerator, Awaitable
from pathlib import Path
from typing import Final

import pytest
import pytest_asyncio

import evohomeasync as ev1
import evohomeasync2 as ev2

from . import faked_server as faked
from .faked_server import FakedServer

# normally, we want these debug flags to be False
_DBG_USE_REAL_AIOHTTP = False
_DBG_DISABLE_STRICT_ASSERTS = False  # of response content-type, schema

if _DBG_USE_REAL_AIOHTTP:
    import aiohttp

    from evohomeasync2.client import TOKEN_CACHE
else:
    from .faked_server import aiohttp  # type: ignore[no-redef]

    # so we don't pollute a real token cache with fake tokens
    TOKEN_CACHE: Final = Path(tempfile.gettempdir()) / ".evo-cache.tst"  # type: ignore[misc]


#######################################################################################


@pytest.fixture(autouse=True)
def _patches_for_tests(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("evohomeasync2.broker.aiohttp", aiohttp)

    monkeypatch.setattr("evohomeasync.broker.aiohttp", aiohttp)


@pytest_asyncio.fixture
async def session() -> AsyncGenerator[aiohttp.ClientSession, None]:
    if _DBG_USE_REAL_AIOHTTP:
        client_session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
    else:
        client_session = aiohttp.ClientSession(faked_server=FakedServer(None, None))  # type: ignore[call-arg]

    try:
        yield client_session
    finally:
        await client_session.close()


@pytest.fixture
def evo1(
    user_credentials: tuple[str, str],
    session: aiohttp.ClientSession | faked.ClientSession,
) -> Awaitable[ev1.EvohomeClient]:
    from .helpers import instantiate_client_v1  # HACK: to avoid circular imports

    return instantiate_client_v1(*user_credentials, session=session)


@pytest.fixture
def user_credentials() -> tuple[str, str]:
    username: str = os.getenv("TEST_USERNAME") or "username@email.com"
    password: str = os.getenv("TEST_PASSWORD") or "password"

    return username, password


@pytest.fixture
def evo2(
    user_credentials: tuple[str, str],
    session: aiohttp.ClientSession | faked.ClientSession,
) -> Awaitable[ev2.EvohomeClient]:
    from .helpers import instantiate_client_v2  # HACK: to avoid circular imports

    return instantiate_client_v2(user_credentials, session)
