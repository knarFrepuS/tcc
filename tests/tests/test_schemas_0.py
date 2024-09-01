#!/usr/bin/env python3
"""Tests for evohome-async - validate the schema of HA's debug JSON (older ver)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from evohomeasync2.schema.const import (
    SZ_GATEWAY_ID,
    SZ_GATEWAY_INFO,
    SZ_GATEWAYS,
    SZ_LOCATION_ID,
    SZ_LOCATION_INFO,
)

from .helpers import (
    TEST_DIR,
    fixture_file,
    refresh_config_with_status,
    validate_config_schema,
    validate_status_schema,
)

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

WORK_DIR = TEST_DIR / "schemas_0"

# NOTE: JSON fom HA is not compliant with vendor schema, but is useful to test against
CONFIG_FILE_NAME = "config.json"
STATUS_FILE_NAME = "status.json"


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    def id_fnc(folder_path: Path) -> str:
        return folder_path.name

    folders = [
        p for p in WORK_DIR.glob("*") if p.is_dir() and not p.name.startswith("_")
    ]
    metafunc.parametrize("folder", sorted(folders), ids=id_fnc)


def test_config_refresh(folder: Path) -> None:
    """Test the loading a config, then an update_status() on top of that."""

    config = fixture_file(folder, CONFIG_FILE_NAME)
    status = fixture_file(folder, STATUS_FILE_NAME)

    # hack because old JSON from HA's evohome integration didn't have location_id, etc.
    if not config[SZ_LOCATION_INFO].get(SZ_LOCATION_ID):
        config[SZ_LOCATION_INFO][SZ_LOCATION_ID] = status[SZ_LOCATION_ID]

    # hack because the JSON is from HA's evohome integration, not vendor's TCC servers
    if not config[SZ_GATEWAYS][0].get(SZ_GATEWAY_ID):
        config[SZ_GATEWAYS][0][SZ_GATEWAY_INFO] = {
            SZ_GATEWAY_ID: status[SZ_GATEWAYS][0][SZ_GATEWAY_ID]
        }

    refresh_config_with_status(config, status)


def test_config_schemas(folder: Path) -> None:
    """Test the config schema for a location."""

    validate_config_schema(fixture_file(folder, CONFIG_FILE_NAME))


def test_status_schemas(folder: Path) -> None:
    """Test the status schema for a location."""

    validate_status_schema(fixture_file(folder, STATUS_FILE_NAME))
