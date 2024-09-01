#!/usr/bin/env python3
"""Tests for evohome-async - validate the schema of HA's debug JSON (newer ver)."""

from __future__ import annotations

from typing import TYPE_CHECKING

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

WORK_DIR = TEST_DIR / "schemas_1"

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

    refresh_config_with_status(
        fixture_file(folder, CONFIG_FILE_NAME),
        fixture_file(folder, STATUS_FILE_NAME),
    )


def test_config_schemas(folder: Path) -> None:
    """Test the config schema for a location."""

    validate_config_schema(fixture_file(folder, CONFIG_FILE_NAME))


def test_status_schemas(folder: Path) -> None:
    """Test the status schema for a location."""

    validate_status_schema(fixture_file(folder, STATUS_FILE_NAME))
