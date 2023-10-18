#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
"""Provides handling of a TCC location."""

from __future__ import annotations
import logging
from typing import TYPE_CHECKING

from .const import URL_BASE
from .gateway import Gateway
from .schema import SCH_LOCN_STATUS

if TYPE_CHECKING:
    from . import EvohomeClient
    from .typing import _LocationIdT


_LOGGER = logging.getLogger(__name__)


class Location:
    """Instance of an account's Location."""

    locationId: _LocationIdT
    name: str

    def __init__(self, client: EvohomeClient, config: dict) -> None:
        self.client = client
        self._client = client._client

        self.__dict__.update(config["locationInfo"])
        assert self.locationId, "Invalid config dict"

        self._gateways: list[Gateway] = []
        self.gateways: dict[str, Gateway] = {}  # gwy by id

        for gwy_config in config["gateways"]:
            gwy = Gateway(self, gwy_config)

            self._gateways.append(gwy)
            self.gateways[gwy.gatewayId] = gwy

    async def status(self) -> dict:
        """Retrieve the location status."""

        url = f"location/{self.locationId}/status?includeTemperatureControlSystems=True"
        response = await self._client("GET", f"{URL_BASE}/{url}")
        loc_status: dict = SCH_LOCN_STATUS(response)

        # Now update other elements
        for gwy_status in loc_status["gateways"]:
            gateway = self.gateways[gwy_status["gatewayId"]]

            tcs_status: dict  # mypy

            for tcs_status in gwy_status["temperatureControlSystems"]:
                tcs = gateway.control_systems[tcs_status["systemId"]]

                tcs.__dict__.update(
                    {
                        "systemModeStatus": tcs_status["systemModeStatus"],
                        "activeFaults": tcs_status["activeFaults"],
                    }
                )

                if dhw_status := tcs_status.get("dhw"):
                    tcs.hotwater.__dict__.update(dhw_status)

                for zone_status in tcs_status["zones"]:
                    zone = tcs.zones_by_id[zone_status["zoneId"]]
                    zone.__dict__.update(zone_status)

        return loc_status
