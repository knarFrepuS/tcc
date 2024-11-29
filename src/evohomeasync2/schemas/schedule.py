#!/usr/bin/env python3
"""evohomeasync schema - for RESTful API Account JSON."""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

import voluptuous as vol

from evohome.helpers import noop

from .const import (
    S2_COOL_SETPOINT,
    S2_DAILY_SCHEDULES,
    S2_DAY_OF_WEEK,
    S2_DHW_STATE,
    S2_HEAT_SETPOINT,
    S2_OFF,
    S2_ON,
    S2_SWITCHPOINTS,
    S2_TIME_OF_DAY,
    DayOfWeek,
)

if TYPE_CHECKING:
    from collections.abc import Callable


#
# These are returned from vendor's API (GET)...
def factory_schedule_dhw(fnc: Callable[[str], str] = noop) -> vol.Schema:
    """Factory for the DHW schedule schema."""

    SCH_GET_SWITCHPOINT_DHW: Final = vol.Schema(  # TODO: checkme
        {
            vol.Required(fnc(S2_DHW_STATE)): vol.Any(S2_ON, S2_OFF),
            vol.Required(fnc(S2_TIME_OF_DAY)): vol.Datetime(format="%H:%M:00"),
        },
        extra=vol.PREVENT_EXTRA,
    )

    SCH_GET_DAY_OF_WEEK_DHW: Final = vol.Schema(
        {
            vol.Required(fnc(S2_DAY_OF_WEEK)): vol.In(DayOfWeek),
            vol.Required(fnc(S2_SWITCHPOINTS)): [SCH_GET_SWITCHPOINT_DHW],
        },
        extra=vol.PREVENT_EXTRA,
    )

    return vol.Schema(
        {
            vol.Required(fnc(S2_DAILY_SCHEDULES)): [SCH_GET_DAY_OF_WEEK_DHW],
        },
        extra=vol.PREVENT_EXTRA,
    )


def factory_schedule_zone(fnc: Callable[[str], str] = noop) -> vol.Schema:
    """Factory for the zone schedule schema."""

    SCH_GET_SWITCHPOINT_ZONE: Final = vol.Schema(
        {
            vol.Optional(fnc(S2_COOL_SETPOINT)): float,  # an extrapolation
            vol.Required(fnc(S2_HEAT_SETPOINT)): vol.All(
                float, vol.Range(min=5, max=35)
            ),
            vol.Required(fnc(S2_TIME_OF_DAY)): vol.Datetime(format="%H:%M:00"),
        },
        extra=vol.PREVENT_EXTRA,
    )

    SCH_GET_DAY_OF_WEEK_ZONE: Final = vol.Schema(
        {
            # l.Required(fnc(S2_DAY_OF_WEEK)): vol.All(int, vol.Range(min=0, max=6)),  # 0 is Monday
            vol.Required(fnc(S2_DAY_OF_WEEK)): vol.In(DayOfWeek),
            vol.Required(fnc(S2_SWITCHPOINTS)): [SCH_GET_SWITCHPOINT_ZONE],
        },
        extra=vol.PREVENT_EXTRA,
    )

    return vol.Schema(
        {
            vol.Required(fnc(S2_DAILY_SCHEDULES)): [SCH_GET_DAY_OF_WEEK_ZONE],
        },
        extra=vol.PREVENT_EXTRA,
    )


#
# These are as to be provided to the vendor's API (PUT)...
# This is after modified by evohome-client (PUT), an evohome-client anachronism?
def _factory_put_schedule_dhw(fnc: Callable[[str], str] = noop) -> vol.Schema:
    """Factory for the zone schedule schema."""

    SCH_PUT_SWITCHPOINT_DHW: Final = vol.Schema(  # TODO: checkme
        {
            vol.Required(fnc(S2_DHW_STATE)): vol.Any(S2_ON, S2_OFF),
            vol.Required(fnc(S2_TIME_OF_DAY)): vol.Datetime(format="%H:%M:00"),
        },
        extra=vol.PREVENT_EXTRA,
    )

    SCH_PUT_DAY_OF_WEEK_DHW: Final = vol.Schema(
        {
            vol.Required(fnc(S2_DAY_OF_WEEK)): vol.All(
                int, vol.Range(min=0, max=6)
            ),  # 0 is Monday
            vol.Required(fnc(S2_SWITCHPOINTS)): [SCH_PUT_SWITCHPOINT_DHW],
        },
        extra=vol.PREVENT_EXTRA,
    )

    return vol.Schema(
        {
            vol.Required(fnc(S2_DAILY_SCHEDULES)): [SCH_PUT_DAY_OF_WEEK_DHW],
        },
        extra=vol.PREVENT_EXTRA,
    )


def _factory_put_schedule_zone(fnc: Callable[[str], str] = noop) -> vol.Schema:
    """Factory for the zone schedule schema."""

    SCH_PUT_SWITCHPOINT_ZONE: Final = vol.Schema(
        {  # NOTE: S2_HEAT_SETPOINT is not .capitalized()
            #
            vol.Required(S2_HEAT_SETPOINT): vol.All(float, vol.Range(min=5, max=35)),
            vol.Required(fnc(S2_TIME_OF_DAY)): vol.Datetime(format="%H:%M:00"),
        },
        extra=vol.PREVENT_EXTRA,
    )

    SCH_PUT_DAY_OF_WEEK_ZONE: Final = vol.Schema(
        {
            vol.Required(fnc(S2_DAY_OF_WEEK)): vol.All(
                int, vol.Range(min=0, max=6)
            ),  # 0 is Monday
            vol.Required(fnc(S2_SWITCHPOINTS)): [SCH_PUT_SWITCHPOINT_ZONE],
        },
        extra=vol.PREVENT_EXTRA,
    )

    return vol.Schema(
        {
            vol.Required(fnc(S2_DAILY_SCHEDULES)): [SCH_PUT_DAY_OF_WEEK_ZONE],
        },
        extra=vol.PREVENT_EXTRA,
    )
