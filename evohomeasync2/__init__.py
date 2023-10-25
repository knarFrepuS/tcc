#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
"""evohomeasync2 provides an async client for the updated Evohome API.

It is (largely) a faithful port of https://github.com/watchforstock/evohome-client

Further information at: https://evohome-client.readthedocs.io
"""
from __future__ import annotations

from http import HTTPStatus
import logging
from datetime import datetime as dt
from typing import TYPE_CHECKING, Any, NoReturn

import aiohttp

from . import exceptions
from .broker import Broker
from .controlsystem import ControlSystem
from .gateway import Gateway  # noqa: F401
from .hotwater import HotWater  # noqa: F401
from .location import Location
from .schema import SCH_FULL_CONFIG, SCH_USER_ACCOUNT
from .zone import Zone  # noqa: F401


if TYPE_CHECKING:
    from .typing import _FilePathT, _LocationIdT, _SystemIdT


_LOGGER = logging.getLogger(__name__)


class EvohomeClientDeprecated:
    """Deprecated attributes and methods removed from the evohome-client namespace."""

    async def full_installation(
        self, location_id: None | _LocationIdT = None
    ) -> NoReturn:
        # if location_id is None:
        #     location_id = self.installation_info[0]["locationInfo"]["locationId"]
        # url = f"location/{location_id}/installationInfo?"  # Specific location

        raise NotImplementedError(
            "EvohomeClient.full_installation() is deprecated, use .installation()"
        )

    async def gateway(self, *args, **kwargs) -> NoReturn:
        raise NotImplementedError("EvohomeClient.gateway() is deprecated")

    async def set_status_reset(self, *args, **kwargs) -> NoReturn:
        raise NotImplementedError(
            "EvohomeClient.set_status_reset() is deprecated, use .reset_mode()"
        )

    async def set_status_normal(self, *args, **kwargs) -> NoReturn:
        raise NotImplementedError(
            "EvohomeClient.set_status_normal() is deprecated, use .set_mode_auto()"
        )

    async def set_status_custom(self, *args, **kwargs) -> NoReturn:
        raise NotImplementedError(
            "EvohomeClient.set_status_custom() is deprecated, use .set_mode_custom()"
        )

    async def set_status_eco(self, *args, **kwargs) -> NoReturn:
        raise NotImplementedError(
            "EvohomeClient.set_status_eco() is deprecated, use .set_mode_eco()"
        )

    async def set_status_away(self, *args, **kwargs) -> NoReturn:
        raise NotImplementedError(
            "EvohomeClient.set_status_away() is deprecated, use .set_mode_away()"
        )

    async def set_status_dayoff(self, *args, **kwargs) -> NoReturn:
        raise NotImplementedError(
            "EvohomeClient.set_status_dayoff() is deprecated, use .set_mode_dayoff()"
        )

    async def set_status_heatingoff(self, *args, **kwargs) -> NoReturn:
        raise NotImplementedError(
            "EvohomeClient.set_status_heatingoff() is deprecated, use .set_mode_heatingoff()"
        )

    async def zone_schedules_backup(self, *args, **kwargs) -> NoReturn:
        raise NotImplementedError(
            "EvohomeClient.zone_schedules_backup() is deprecated, use .backup_schedules()"
        )

    async def zone_schedules_restore(self, *args, **kwargs) -> NoReturn:
        raise NotImplementedError(
            "EvohomeClient.zone_schedules_restore() is deprecated, use .restore_schedules()"
        )


class EvohomeClient(EvohomeClientDeprecated):
    """Provide access to the v2 Evohome API."""

    _full_config: dict[str, Any] = None  # type: ignore[assignment]  # installation_info (all locations of user)
    _user_account: dict[str, Any] = None  # type: ignore[assignment]  # account_info

    def __init__(
        self,
        username: str,
        password: str,
        /,
        *,
        debug: bool = False,
        refresh_token: None | str = None,
        access_token: None | str = None,
        access_token_expires: None | dt = None,
        session: None | aiohttp.ClientSession = None,
    ) -> None:
        """Construct the EvohomeClient object."""

        if debug:
            _LOGGER.setLevel(logging.DEBUG)
            _LOGGER.debug("Debug mode is explicitly enabled.")

        self._broker = Broker(
            username,
            password,
            refresh_token=refresh_token,
            access_token=access_token,
            access_token_expires=access_token_expires,
            session=session,
            logger=_LOGGER,
        )
        self._logger = _LOGGER

        self.locations: list[Location] = []

    @property
    def refresh_token(self) -> str:
        return self._broker.refresh_token

    @property
    def access_token(self) -> str:
        return self._broker.access_token

    @property
    def access_token_expires(self) -> dt:
        return self._broker.access_token_expires

    async def login(self) -> None:
        """Retrieve the user account and installation details.

        Will authenticate as required.
        """

        try:  # the cached access_token may be valid, but is not authorized
            await self.user_account()

        except exceptions.AuthenticationError as exc:
            if exc.status != HTTPStatus.UNAUTHORIZED or not self.access_token:
                raise

            self._logger.warning(
                "Unauthorized access_token (will try re-authenticating)."
            )
            self.access_token = None
            await self.user_account(force_update=True)

        await self.installation()

    @property  # user_account
    def account_info(self) -> dict:  # from the original evohomeclient namespace
        """Return the information of the user account."""
        return self._user_account

    async def user_account(self, force_update: bool = False) -> dict:
        """Return the user account information.

        If required/forced, retrieve that data from the vendor's API.
        """

        # There is usually no need to refresh this data (it is config, not state)
        if self._user_account and not force_update:
            return self._user_account

        self._user_account = await self._broker.get(
            "userAccount", schema=SCH_USER_ACCOUNT
        )  # except exceptions.FailedRequest

        return self._user_account

    @property  # full_config (all locations of user)
    def installation_info(self) -> dict:  # from the original evohomeclient namespace
        """Return the installation info (config) of all the user's locations."""
        return self._full_config

    async def installation(self, force_update: bool = False) -> dict:
        """Return the configuration of the user's locations their status.

        If required/forced, retrieve that data from the vendor's API.
        Note that the force_update flag will create new location entities (it includes
        `self.locations = []`).
        """

        # There is usually no need to refresh this data (it is config, not state)
        if self._full_config and not force_update:
            return self._full_config

        return await self._installation()  # aka self.installation_info

    async def _installation(self, refresh_status: bool = True) -> dict:
        """Return the configuration of the user's locations their status.

        The refresh_status flag is used for dev/test to disable retreiving the initial
        status of each location (and its child entities).
        """

        assert isinstance(self.account_info, dict)  # mypy

        # FIXME: shouldn't really be starting again with new objects?
        self.locations = []  # for now, need to clear this before GET

        url = f"location/installationInfo?userId={self.account_info['userId']}"
        url += "&includeTemperatureControlSystems=True"

        self._full_config: list = await self._broker.get(
            url, schema=SCH_FULL_CONFIG
        )  # except exceptions.FailedRequest

        # populate each freshly instantiated location with its initial status
        for loc_data in self._full_config:
            loc = Location(self, loc_data)
            self.locations.append(loc)
            if refresh_status:
                await loc.refresh_status()

        return self._full_config

    def _get_single_heating_system(self) -> ControlSystem:
        """If there is a single location/gateway/TCS, return it, or raise an exception.

        Most systems will have only one TCS.
        """

        if not self.locations or len(self.locations) != 1:
            raise exceptions.NoDefaultTcsError(
                "There is not a single location (only) for this account"
            )

        if len(self.locations[0]._gateways) != 1:  # type: ignore[index]
            raise exceptions.NoDefaultTcsError(
                "There is not a single gateway (only) for this account/location"
            )

        if len(self.locations[0]._gateways[0]._control_systems) != 1:  # type: ignore[index]
            raise exceptions.NoDefaultTcsError(
                "There is not a single TCS (only) for this account/location/gateway"
            )

        return self.locations[0]._gateways[0]._control_systems[0]  # type: ignore[index]

    @property
    def system_id(self) -> _SystemIdT:  # an evohome-client anachronism, deprecate?
        """Return the ID of the 'default' TCS (assumes only one loc/gwy/TCS)."""
        return self._get_single_heating_system().systemId

    async def reset_mode(self) -> None:
        """Reset the mode of the default TCS and its zones."""
        await self._get_single_heating_system().reset_mode()

    async def set_mode_auto(self) -> None:
        """Set the default TCS into auto mode."""
        await self._get_single_heating_system().set_mode_auto()

    async def set_mode_away(self, /, *, until: None | dt = None) -> None:
        """Set the default TCS into away mode."""
        await self._get_single_heating_system().set_mode_away(until=until)

    async def set_mode_custom(self, /, *, until: None | dt = None) -> None:
        """Set the default TCS into custom mode."""
        await self._get_single_heating_system().set_mode_custom(until=until)

    async def set_mode_dayoff(self, /, *, until: None | dt = None) -> None:
        """Set the default TCS into day off mode."""
        await self._get_single_heating_system().set_mode_dayoff(until=until)

    async def set_mode_eco(self, /, *, until: None | dt = None) -> None:
        """Set the default TCS into eco mode."""
        await self._get_single_heating_system().set_mode_eco(until=until)

    async def set_mode_heatingoff(self, /, *, until: None | dt = None) -> None:
        """Set the default TCS into heating off mode."""
        await self._get_single_heating_system().set_mode_heatingoff(until=until)

    async def temperatures(self) -> list[dict]:
        """Return the current temperatures and setpoints of the default TCS."""
        return await self._get_single_heating_system().temperatures()

    async def backup_schedules(self, filename: _FilePathT) -> None:
        """Backup all schedules from the default control system to the file."""
        await self._get_single_heating_system().backup_schedules(filename)

    async def restore_schedules(
        self, filename: _FilePathT, match_by_name: bool = False
    ) -> None:
        """Restore all schedules from the file to the control system.

        There is the option to match schedules to their zone/dhw by name rather than id.
        """

        await self._get_single_heating_system().restore_schedules(
            filename, match_by_name=match_by_name
        )
