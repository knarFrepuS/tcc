#!/usr/bin/env python3
"""Tests for evohome-async - validate the schedule schemas."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from evohomeasync2.schema.schedule import (
    SCH_GET_SCHEDULE_DHW,
    SCH_GET_SCHEDULE_ZONE,
    SCH_PUT_SCHEDULE_DHW,
    SCH_PUT_SCHEDULE_ZONE,
    convert_to_get_schedule,
    convert_to_put_schedule,
)

from .helpers import TEST_DIR

if TYPE_CHECKING:
    import voluptuous as vol

WORK_DIR = TEST_DIR / "schedules"


def _test_schedule_schema(file_name: str, schema: vol.Schema) -> dict:
    def read_dict_from_file(file_name: str) -> dict:
        with (WORK_DIR / file_name).open() as f:
            data: dict = json.load(f)
        return data

    return schema(read_dict_from_file(file_name))  # type: ignore[no-any-return]


def test_schema_schedule_dhw() -> None:
    """Test the schedule schema for dhw."""

    get_sched = _test_schedule_schema("schedule_dhw_get.json", SCH_GET_SCHEDULE_DHW)
    put_sched = _test_schedule_schema("schedule_dhw_put.json", SCH_PUT_SCHEDULE_DHW)

    assert put_sched == convert_to_put_schedule(get_sched)
    assert get_sched == convert_to_get_schedule(put_sched)


def test_schema_schedule_zone() -> None:
    """Test the schedule schema for zones."""

    get_sched = _test_schedule_schema("schedule_zone_get.json", SCH_GET_SCHEDULE_ZONE)
    put_sched = _test_schedule_schema("schedule_zone_put.json", SCH_PUT_SCHEDULE_ZONE)

    assert put_sched == convert_to_put_schedule(get_sched)
    assert get_sched == convert_to_get_schedule(put_sched)
