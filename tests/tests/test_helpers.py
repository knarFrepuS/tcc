#!/usr/bin/env python3
"""Tests for evohome-async - validate the helper functions."""

from __future__ import annotations

import json

import pytest

from evohomeasync2.broker import convert_json
from evohomeasync2.schema.helpers import camel_case, pascal_case
from evohomeasync2.schema.schedule import (
    SCH_GET_SCHEDULE_DHW,
    SCH_GET_SCHEDULE_ZONE,
    SCH_PUT_SCHEDULE_DHW,
    SCH_PUT_SCHEDULE_ZONE,
    convert_to_get_schedule,
    convert_to_put_schedule,
)

from .helpers import TEST_DIR

WORK_DIR = TEST_DIR / "schedules"


def test_get_schedule_zon() -> None:
    """Convert a zone's get schedule to snake_case, and back again."""

    with (WORK_DIR / "schedule_zone_get.json").open() as f:
        get_schedule = json.load(f)

    assert get_schedule == SCH_GET_SCHEDULE_ZONE(get_schedule)

    put_schedule = convert_to_put_schedule(get_schedule)
    assert put_schedule == SCH_PUT_SCHEDULE_ZONE(put_schedule)

    assert get_schedule == convert_to_get_schedule(put_schedule)


def test_get_schedule_dhw() -> None:
    """Convert a dhw's get schedule to snake_case, and back again."""

    with (WORK_DIR / "schedule_dhw_get.json").open() as f:
        get_schedule = json.load(f)

    assert get_schedule == SCH_GET_SCHEDULE_DHW(get_schedule)

    put_schedule = convert_to_put_schedule(get_schedule)
    assert put_schedule == SCH_PUT_SCHEDULE_DHW(put_schedule)

    assert get_schedule == convert_to_get_schedule(put_schedule)


def test_case_converters() -> None:
    """Test helper functions."""

    camel_case_str = "testString"
    pascal_case_str = "TestString"

    assert camel_case(camel_case_str) == camel_case_str
    assert camel_case(pascal_case_str) == camel_case_str
    assert pascal_case(camel_case_str) == pascal_case_str
    assert pascal_case(pascal_case_str) == pascal_case_str

    assert camel_case(pascal_case(camel_case_str)) == camel_case_str
    assert pascal_case(camel_case(pascal_case_str)) == pascal_case_str


@pytest.mark.skip("This is a WIP")
def test_json_snakator() -> None:
    """Confirm the recursive snake_case converter works as expected."""

    assert convert_json({"UpperCase": "lowerCase"}) == {"upper_case": "lower_case"}
    assert convert_json({"UpperCase": ["lowerCase"]}) == {"upper_case": ["lower_case"]}
