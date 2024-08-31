#!/usr/bin/env python3
"""Tests for evohome-async - validate the schedule schemas."""

from __future__ import annotations

import json

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


def _read_dict_from_file(file_name: str) -> dict:
    with (WORK_DIR / file_name).open() as f:
        return json.load(f)  # type: ignore[no-any-return]


def test_schema_schedule_dhw() -> None:
    """Test the schedule schema for dhw."""

    get_sched = SCH_GET_SCHEDULE_DHW(_read_dict_from_file("schedule_dhw_get.json"))
    put_sched = SCH_PUT_SCHEDULE_DHW(_read_dict_from_file("schedule_dhw_put.json"))

    assert put_sched == convert_to_put_schedule(get_sched)
    assert get_sched == convert_to_get_schedule(put_sched)


def test_schema_schedule_zone() -> None:
    """Test the schedule schema for zones."""

    get_sched = SCH_GET_SCHEDULE_ZONE(_read_dict_from_file("schedule_zone_get.json"))
    put_sched = SCH_PUT_SCHEDULE_ZONE(_read_dict_from_file("schedule_zone_put.json"))

    assert put_sched == convert_to_put_schedule(get_sched)
    assert get_sched == convert_to_get_schedule(put_sched)
