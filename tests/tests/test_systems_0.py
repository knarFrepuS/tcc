#!/usr/bin/env python3
"""Tests for evohome-async - validate the schemas of vendor's RESTful JSON."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from evohomeasync2.schema import SCH_FULL_CONFIG, SCH_LOCN_STATUS, SCH_USER_ACCOUNT

from .helpers import TEST_DIR

if TYPE_CHECKING:
    from pathlib import Path

    import voluptuous as vol


WORK_DIR = TEST_DIR / "systems_0"


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    def id_fnc(folder_path: Path) -> str:
        return folder_path.name

    folders = [
        p for p in WORK_DIR.glob("*") if p.is_dir() and not p.name.startswith("_")
    ]
    metafunc.parametrize("folder", sorted(folders), ids=id_fnc)


def _test_schema(folder: Path, schema: vol.Schema, file_name: str) -> None:
    if not (folder / file_name).is_file():
        pytest.skip(f"No {file_name} in: {folder.name}")

    with (folder / file_name).open() as f:
        data: dict = json.load(f)

    _ = schema(data)


def test_user_account(folder: Path) -> None:
    """Test the user account schema against the corresponding JSON."""
    _test_schema(folder, SCH_USER_ACCOUNT, "user_account.json")


def test_user_locations(folder: Path) -> None:
    """Test the user locations config schema against the corresponding JSON."""
    _test_schema(folder, SCH_FULL_CONFIG, "user_locations.json")


def test_location_status(folder: Path) -> None:
    """Test the location status schema against the corresponding JSON."""
    for p in folder.glob("status_*.json"):
        _test_schema(folder, SCH_LOCN_STATUS, p.name)
