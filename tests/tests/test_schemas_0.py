#!/usr/bin/env python3
"""Tests for evohome-async - validate the schema of HA's debug JSON (older ver)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from evohomeasync2 import Location
from evohomeasync2.schema import SCH_LOCN_STATUS
from evohomeasync2.schema.config import SCH_TCS_CONFIG, SCH_TIME_ZONE
from evohomeasync2.schema.const import (
    S2_GATEWAY_ID,
    S2_GATEWAY_INFO,
    S2_GATEWAYS,
    S2_LOCATION_ID,
    S2_LOCATION_INFO,
    S2_TEMPERATURE_CONTROL_SYSTEMS,
    S2_TIME_ZONE,
)

from .conftest import ClientStub
from .helpers import TEST_DIR

WORK_DIR = f"{TEST_DIR}/schemas_0"

# NOTE: JSON from HA is not compliant with vendor schema, but is useful to test against
CONFIG_FILE_NAME = "config.json"
STATUS_FILE_NAME = "status.json"


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    def id_fnc(folder_path: Path) -> str:
        return folder_path.name

    folders = [
        p for p in Path(WORK_DIR).glob("*") if p.is_dir() and not p.name.startswith("_")
    ]
    metafunc.parametrize("folder", sorted(folders), ids=id_fnc)


def test_config_refresh(folder: Path) -> None:
    """Test the loading a config, then an update_status() on top of that."""

    if not Path(folder).joinpath(CONFIG_FILE_NAME).is_file():
        pytest.skip(f"No {CONFIG_FILE_NAME} in: {folder.name}")

    if not Path(folder).joinpath(STATUS_FILE_NAME).is_file():
        pytest.skip(f"No {STATUS_FILE_NAME} in: {folder.name}")

    with open(Path(folder).joinpath(CONFIG_FILE_NAME)) as f:
        config: dict = json.load(f)  # is camelCase, as per vendor's schema

    with open(Path(folder).joinpath(STATUS_FILE_NAME)) as f:
        status: dict = json.load(f)  # is camelCase, as per vendor's schema

    # hack because old JSON from HA's evohome integration didn't have location_id, etc.
    if not config[S2_LOCATION_INFO].get(S2_LOCATION_ID):
        config[S2_LOCATION_INFO][S2_LOCATION_ID] = status[S2_LOCATION_ID]

    # hack because the JSON is from HA's evohome integration, not vendor's TCC servers
    if not config[S2_GATEWAYS][0].get(S2_GATEWAY_ID):
        config[S2_GATEWAYS][0][S2_GATEWAY_INFO] = {
            S2_GATEWAY_ID: status[S2_GATEWAYS][0][S2_GATEWAY_ID]
        }

    loc = Location(ClientStub(), config)
    loc._update_status(status)


def test_config_schemas(folder: Path) -> None:
    """Test the config schema for a location."""

    if not Path(folder).joinpath(CONFIG_FILE_NAME).is_file():
        pytest.skip(f"No {CONFIG_FILE_NAME} in: {folder.name}")

    with open(Path(folder).joinpath(CONFIG_FILE_NAME)) as f:
        config: dict = json.load(f)  # is camelCase, as per vendor's schema

    _ = SCH_TIME_ZONE(config[S2_LOCATION_INFO][S2_TIME_ZONE])
    for gwy_config in config[S2_GATEWAYS]:
        for tcs_config in gwy_config[S2_TEMPERATURE_CONTROL_SYSTEMS]:
            _ = SCH_TCS_CONFIG(tcs_config)


def test_status_schemas(folder: Path) -> None:
    """Test the status schema for a location."""

    if not Path(folder).joinpath(STATUS_FILE_NAME).is_file():
        pytest.skip(f"No {STATUS_FILE_NAME} in: {folder.name}")

    with open(Path(folder).joinpath(STATUS_FILE_NAME)) as f:
        status: dict = json.load(f)  # is camelCase, as per vendor's schema

    _ = SCH_LOCN_STATUS(status)
