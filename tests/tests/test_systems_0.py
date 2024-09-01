#!/usr/bin/env python3
"""Tests for evohome-async - validate the schemas of vendor's RESTful JSON."""

from __future__ import annotations

from typing import TYPE_CHECKING

from evohomeasync2.schema import SCH_FULL_CONFIG, SCH_LOCN_STATUS, SCH_USER_ACCOUNT

from .helpers import TEST_DIR, fixture_file

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

WORK_DIR = TEST_DIR / "systems_0"


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    def id_fnc(folder_path: Path) -> str:
        return folder_path.name

    folders = [
        p for p in WORK_DIR.glob("*") if p.is_dir() and not p.name.startswith("_")
    ]
    metafunc.parametrize("folder", sorted(folders), ids=id_fnc)


def test_user_account(folder: Path) -> None:
    """Test the user account schema against the corresponding JSON."""

    _ = SCH_USER_ACCOUNT(fixture_file(folder, "user_account.json"))


def test_user_locations(folder: Path) -> None:
    """Test the user locations config schema against the corresponding JSON."""

    _ = SCH_FULL_CONFIG(fixture_file(folder, "user_locations.json"))


def test_location_status(folder: Path) -> None:
    """Test the location status schema against the corresponding JSON."""

    for p in folder.glob("status_*.json"):
        _ = SCH_LOCN_STATUS(fixture_file(folder, p.name))
