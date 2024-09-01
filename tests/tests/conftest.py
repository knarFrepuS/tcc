#!/usr/bin/env python3
"""Tests for evohome-async - validate the schema of HA's debug JSON (newer ver)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Self

import aiohttp
import pytest
import pytest_asyncio

from evohomeasync2.schema import SCH_FULL_CONFIG, SCH_LOCN_STATUS, SCH_USER_ACCOUNT

from .helpers import TokenManager

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable

    import voluptuous as vol


type JsonValueType = (
    dict[str, JsonValueType] | list[JsonValueType] | str | int | float | bool | None
)
type JsonArrayType = list[JsonValueType]
type JsonObjectType = dict[str, JsonValueType]

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


@lru_cache
def load_fixture(install: str, file_name: str) -> JsonArrayType | JsonObjectType:
    """Load a file fixture."""

    try:
        try:
            text = (FIXTURES_DIR / install / file_name).read_text()
        except FileNotFoundError:
            text = (FIXTURES_DIR / "default" / file_name).read_text()

    except FileNotFoundError:
        pytest.skip(f"Fixture {file_name} not found in {FIXTURES_DIR / install}")

    return json.loads(text)  # type: ignore[no-any-return]


def user_account_fixture(install: str) -> JsonObjectType:
    """Load the JSON of the user installation."""
    return load_fixture(install, "user_account.json")  # type: ignore[return-value]


def user_locations_config_fixture(install: str) -> JsonArrayType:
    """Load the JSON of the config of a user's installation (a list of locations)."""
    return load_fixture(install, "user_locations.json")  # type: ignore[return-value]


def location_status_fixture(install: str, loc_id: str) -> JsonObjectType:
    """Load the JSON of the status of a location."""
    return load_fixture(install, f"status_{loc_id}.json")  # type: ignore[return-value]


def broker_get(install: str) -> Callable:
    """Return a mock of Broker.get()."""

    async def get(
        self: Self,  # type: ignore[misc]
        url: str,
        schema: vol.Schema | None = None,
    ) -> JsonArrayType | JsonObjectType:
        if "userAccount" in url:  # EvohomeClient.user_account
            return SCH_USER_ACCOUNT(user_account_fixture(install))  # type: ignore[no-any-return]

        if "installationInfo" in url:  # EvohomeClient._installation
            return SCH_FULL_CONFIG(user_locations_config_fixture(install))  # type: ignore[no-any-return]

        if "status" in url:  # Location.refresh_status
            return SCH_LOCN_STATUS(location_status_fixture(install, url.split("/")[1]))  # type: ignore[no-any-return]

        pytest.fail(f"Unexpected/unknown URL: {url}")

    return get


@pytest_asyncio.fixture
async def client_session() -> AsyncGenerator[aiohttp.ClientSession, None]:
    """Yield a vanilla aiohttp.ClientSession."""

    client_session = aiohttp.ClientSession()

    try:
        yield client_session
    finally:
        await client_session.close()


@pytest.fixture
async def token_manager(
    client_session: aiohttp.ClientSession,
) -> AsyncGenerator[TokenManager, None]:
    """Yield a token manager with vanilla credentials."""

    token_manager = TokenManager("user@mail.com", "password", client_session)
    await token_manager.restore_access_token()

    try:
        yield token_manager
    finally:
        await token_manager.save_access_token()
