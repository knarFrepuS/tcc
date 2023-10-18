#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
"""Provides handling of individual zones."""
from __future__ import annotations

from datetime import datetime as dt
import json
import logging
from typing import TYPE_CHECKING, NoReturn

from .exceptions import InvalidSchedule
from .const import API_STRFTIME, URL_BASE

if TYPE_CHECKING:
    from .controlsystem import ControlSystem
    from .typing import _ZoneIdT


MAPPING = [
    ("dailySchedules", "DailySchedules"),
    ("dayOfWeek", "DayOfWeek"),
    ("temperature", "TargetTemperature"),
    ("timeOfDay", "TimeOfDay"),
    ("switchpoints", "Switchpoints"),
    ("dhwState", "DhwState"),
]

_LOGGER = logging.getLogger(__name__)


class ZoneBase:
    """Provide the base for temperatureZone / domesticHotWater Zones."""

    _id: str  # zoneId or dhwId
    _type: str  # temperatureZone or domesticHotWater

    def __init__(self, tcs: ControlSystem, config: dict):
        self.tcs = tcs  # parent
        self.client = tcs.gateway.location.client
        self._client = tcs.gateway.location.client._client

    @property
    def zone_type(self) -> NoReturn:
        raise NotImplementedError("ZoneBase.zone_type is deprecated, use ._type")

    async def schedule(self) -> NoReturn:
        raise NotImplementedError(
            "ZoneBase.schedule() is deprecrated, use .get_schedule()"
        )

    async def get_schedule(self) -> dict:
        """Get the schedule for this dhw/zone object."""

        _LOGGER.debug(f"Getting schedule of {self._id} ({self._type})...")

        url = f"{self._type}/{self._id}/schedule"
        response_json = await self._client("GET", f"{URL_BASE}/{url}")

        response_text = json.dumps(response_json)  # FIXME
        for from_val, to_val in MAPPING:  # an anachronism from evohome-client
            response_text = response_text.replace(from_val, to_val)

        result: dict = json.loads(response_text)
        # change the day name string to a number offset (0 = Monday)
        for day_of_week, schedule in enumerate(result["DailySchedules"]):
            schedule["DayOfWeek"] = day_of_week

        return result

    async def set_schedule(self, zone_schedule: str) -> None:
        """Set the schedule for this dhw/zone object."""

        _LOGGER.debug(f"Setting schedule of {self._id} ({self._type})...")

        try:
            json.loads(zone_schedule)

        except ValueError as exc:
            raise InvalidSchedule(f"zone_schedule must be valid JSON: {exc}")

        url = f"{self._type}/{self._id}/schedule"
        await self._client("PUT", f"{URL_BASE}/{url}", json=zone_schedule)


class Zone(ZoneBase):
    """Provide the access to an individual zone."""

    zoneId: _ZoneIdT

    name: str  # TODO: check if is OK here
    setpointStatus: dict  # TODO
    temperatureStatus: dict  # TODO

    _type = "temperatureZone"

    def __init__(self, tcs: ControlSystem, config: dict) -> None:
        super().__init__(tcs, config)

        self.__dict__.update(config)
        assert self.zoneId, "Invalid config dict"

        self._id = self.zoneId

    async def _set_heat_setpoint(self, heat_setpoint: dict) -> None:
        """TODO"""

        url = f"temperatureZone/{self.zoneId}/heatSetpoint"  # f"{_type}/{_id}/heatS..."
        await self._client("PUT", f"{URL_BASE}/{url}", json=heat_setpoint)

    async def set_temperature(
        self, temperature: float, /, *, until: None | dt = None
    ) -> None:
        """Set the temperature of the given zone."""

        if until is None:
            mode = {
                "SetpointMode": "PermanentOverride",
                "HeatSetpointValue": temperature,
                "TimeUntil": None,
            }
        else:
            mode = {
                "SetpointMode": "TemporaryOverride",
                "HeatSetpointValue": temperature,
                "TimeUntil": until.strftime(API_STRFTIME),
            }

        await self._set_heat_setpoint(mode)

    async def cancel_temp_override(self) -> None:
        """Cancel an override to the zone temperature."""

        mode = {
            "SetpointMode": "FollowSchedule",
            "HeatSetpointValue": 0.0,
            "TimeUntil": None,
        }

        await self._set_heat_setpoint(mode)
