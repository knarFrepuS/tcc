#!/usr/bin/env python3
"""evohome-async - validate the handling of vendor APIs (URLs)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

import evohomeasync as ev1

from .conftest import _DBG_USE_REAL_AIOHTTP
from .const import ExitTestReason

if TYPE_CHECKING:
    from collections.abc import Awaitable


async def _test_client_apis(evo: ev1.EvohomeClient) -> None:
    """Instantiate a client, and logon to the vendor API."""

    user_data = await evo._populate_user_data()
    assert user_data == evo.user_info

    full_data = await evo._populate_locn_data()
    assert full_data == evo.location_data

    temps = await evo.get_temperatures()

    assert temps

    # for _ in range(3):
    #     await asyncio.sleep(5)
    #     _ = await evo.get_temperatures()


async def test_client_apis(evo2: Awaitable[ev1.EvohomeClient]) -> None:
    """Test _populate_user_data() & _populate_full_data()"""

    if not _DBG_USE_REAL_AIOHTTP:
        pytest.skip(ExitTestReason.NOT_IMPLEMENTED)

    try:
        await _test_client_apis(await evo2)
    except ev1.AuthenticationFailedError as err:
        pytest.fail(ExitTestReason.AUTHENTICATE_FAIL + f": {err}")
