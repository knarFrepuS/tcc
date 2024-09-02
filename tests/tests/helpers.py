#!/usr/bin/env python3
"""Tests for evohome-async - helper functions."""

from __future__ import annotations

import inspect
import json
import logging
from datetime import datetime as dt
from functools import lru_cache
from pathlib import Path

import pytest

from evohomeasync2 import Location
from evohomeasync2.broker import AbstractTokenManager
from evohomeasync2.schema import SCH_LOCN_STATUS
from evohomeasync2.schema.config import SCH_TEMPERATURE_CONTROL_SYSTEM, SCH_TIME_ZONE
from evohomeasync2.schema.const import (
    SZ_GATEWAYS,
    SZ_LOCATION_INFO,
    SZ_TEMPERATURE_CONTROL_SYSTEMS,
    SZ_TIME_ZONE,
)

TEST_DIR = Path(__file__).resolve().parent


_LOGGER = logging.getLogger(__name__)


class ClientStub:
    broker = None
    _logger = _LOGGER


class GatewayStub:
    _broker = None
    _logger = _LOGGER
    location = None


class TokenManager(AbstractTokenManager):
    async def restore_access_token(self) -> None:
        """Restore the access token from the cache."""

        self.access_token = "access_token"  # noqa: S105
        self.access_token_expires = dt.max
        self.refresh_token = "refresh_token"  # noqa: S105

    async def save_access_token(self) -> None:
        """Save the access token to the cache."""


def get_property_methods(obj: object) -> list[str]:
    """Return a list of property methods of an object."""
    return [
        name
        for name, value in inspect.getmembers(obj.__class__)
        if isinstance(value, property)
    ]


@lru_cache
def fixture_file(folder: Path, file_name: str, /) -> dict:
    if not (folder / file_name).is_file():
        pytest.skip(f"Fixture {file_name} not found in {folder.name}")

    with (folder / file_name).open() as f:
        return json.load(f)  # type: ignore[no-any-return]


def refresh_config_with_status(config: dict, status: dict) -> None:
    """Create a location from a config, and update it with a status."""
    loc = Location(ClientStub(), config)
    loc._update_status(status)


def validate_config_schema(config: dict) -> None:
    _ = SCH_TIME_ZONE(config[SZ_LOCATION_INFO][SZ_TIME_ZONE])

    for gwy_config in config[SZ_GATEWAYS]:
        for tcs_config in gwy_config[SZ_TEMPERATURE_CONTROL_SYSTEMS]:
            _ = SCH_TEMPERATURE_CONTROL_SYSTEM(tcs_config)


def validate_status_schema(status: dict) -> None:
    _ = SCH_LOCN_STATUS(status)
