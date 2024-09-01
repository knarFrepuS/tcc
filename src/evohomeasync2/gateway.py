#!/usr/bin/env python3
"""Provides handling of TCC gateways."""

from __future__ import annotations

from typing import TYPE_CHECKING, Final, NoReturn

from . import exceptions as exc
from .schema import SCH_GWY_STATUS
from .schema.const import (
    SZ_GATEWAY,
    SZ_GATEWAY_ID,
    SZ_GATEWAY_INFO,
    SZ_IS_WI_FI,
    SZ_MAC,
    SZ_SYSTEM_ID,
    SZ_TEMPERATURE_CONTROL_SYSTEMS,
)
from .system import System
from .zone import ActiveFaultsMixin, EntityBase

if TYPE_CHECKING:
    import voluptuous as vol

    from . import Location
    from .schema import _EvoDictT


class _GatewayDeprecated:  # pragma: no cover
    """Deprecated attributes and methods removed from the evohome-client namespace."""

    @property
    def gatewayId(self) -> NoReturn:  # noqa: N802
        raise exc.DeprecationError(f"{self}: .gatewayId is deprecated, use .id")


class Gateway(_GatewayDeprecated, ActiveFaultsMixin, EntityBase):
    """Instance of a location's gateway."""

    STATUS_SCHEMA: Final[vol.Schema] = SCH_GWY_STATUS
    TYPE: Final = SZ_GATEWAY  # used for RESTful API calls

    def __init__(self, location: Location, config: _EvoDictT, /) -> None:
        super().__init__(config[SZ_GATEWAY_INFO][SZ_GATEWAY_ID], location)

        self.location = location

        self._config: Final[_EvoDictT] = config[SZ_GATEWAY_INFO]
        self._status: _EvoDictT = {}

        self.systems: list[System] = []
        self.system_by_id: dict[str, System] = {}

        tcs_config: _EvoDictT
        for tcs_config in config[SZ_TEMPERATURE_CONTROL_SYSTEMS]:
            tcs = System(self, tcs_config)

            self.systems.append(tcs)
            self.system_by_id[tcs.id] = tcs

    @property
    def mac(self) -> str:
        ret: str = self._config[SZ_MAC]
        return ret

    @property
    def is_wifi(self) -> bool:
        ret: bool = self._config[SZ_IS_WI_FI]
        return ret

    def _update_status(self, status: _EvoDictT) -> None:
        super()._update_status(status)  # process active faults

        self._status = status

        for tcs_status in self._status[SZ_TEMPERATURE_CONTROL_SYSTEMS]:
            if tcs := self.system_by_id.get(tcs_status[SZ_SYSTEM_ID]):
                tcs._update_status(tcs_status)  # noqa: SLF001

            else:
                self._logger.warning(
                    f"{self}: system_id='{tcs_status[SZ_SYSTEM_ID]}' not known"
                    ", (has the gateway configuration been changed?)"
                )
