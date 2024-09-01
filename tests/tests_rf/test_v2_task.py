#!/usr/bin/env python3
"""evohome-async - validate the handling of vendor APIs (URLs)."""

from __future__ import annotations

import asyncio
from datetime import datetime as dt, timedelta as td
from http import HTTPMethod, HTTPStatus

import pytest

import evohomeasync2 as evo2
from evohomeasync2 import Gateway, Location, System
from evohomeasync2.const import API_STRFTIME, DhwState, ZoneMode
from evohomeasync2.schema.const import (
    SZ_MODE,
    SZ_STATE,
    SZ_STATE_STATUS,
    SZ_UNTIL,
    SZ_UNTIL_TIME,
)
from evohomeasync2.schema.helpers import pascal_case

from .conftest import _DBG_USE_REAL_AIOHTTP, aiohttp
from .const import ExitTestReason
from .helpers import (
    instantiate_client_v2,
    should_fail,
    should_work,
    wait_for_comm_task_v2 as wait_for_comm_task,
)

#######################################################################################


async def _test_task_id(evo: evo2.EvohomeClient) -> None:
    """Test the task_id returned when using the vendor's RESTful APIs.

    This test can be used to prove that JSON keys are can be camelCase or PascalCase.
    """

    loc: Location
    gwy: Gateway
    tcs: System

    _ = await evo.user_account()
    _ = await evo._installation(refresh_status=False)

    dhw = None

    for loc in evo.locations:
        for gwy in loc.gateways:
            for tcs in gwy.systems:
                if tcs.hotwater:
                    # if (dhw := tcs.hotwater) and dhw.temperatureStatus['isAvailable']:
                    dhw = tcs.hotwater
                    break
    if dhw is None:
        pytest.skip(ExitTestReason.NO_TESTABLE_DHW)

    get_url = f"{dhw.TYPE}/{dhw.id}/status"
    put_url = f"{dhw.TYPE}/{dhw.id}/state"

    #
    # PART 0: Get initial state...
    old_status = await should_work(evo, HTTPMethod.GET, get_url)
    assert isinstance(old_status, dict)  # mypy
    # {
    #     'dhwId': '3933910',
    #     'temperatureStatus': {'isAvailable': False},
    #     'stateStatus': {'state': 'Off', 'mode': 'FollowSchedule'},
    #     'activeFaults': []
    # }  # HTTP 200
    # {
    #     'dhwId': '3933910',
    #     'temperatureStatus': {'temperature': 21.0, 'isAvailable': True},
    #     'stateStatus': {
    #         'state': 'On',
    #         'mode': 'TemporaryOverride',
    #         'until': '2023-10-30T18:40:00Z'
    #     },
    #     'activeFaults': []
    # }  # HTTP 200

    old_mode = {
        SZ_MODE: old_status[SZ_STATE_STATUS][SZ_MODE],
        SZ_STATE: old_status[SZ_STATE_STATUS][SZ_STATE],
        SZ_UNTIL_TIME: old_status[SZ_STATE_STATUS].get(SZ_UNTIL),
    }  # NOTE: untilTime/until

    #
    # PART 1: Try the basic functionality...
    # new_mode = {SZ_MODE: ZoneMode.PERMANENT_OVERRIDE, SZ_STATE: DhwState.OFF, SZ_UNTIL_TIME: None}
    new_mode = {
        SZ_MODE: ZoneMode.TEMPORARY_OVERRIDE,
        SZ_STATE: DhwState.ON,
        SZ_UNTIL_TIME: (dt.now() + td(hours=1)).strftime(API_STRFTIME),
    }

    result = await should_work(evo, HTTPMethod.PUT, put_url, json=new_mode)
    assert isinstance(result, dict | list)  # mypy
    # {'id': '840367013'}  # HTTP 201/Created

    task_id = result[0]["id"] if isinstance(result, list) else result["id"]
    url_tsk = f"commTasks?commTaskId={task_id}"

    _ = await should_work(evo, HTTPMethod.GET, url_tsk)
    # {'commtaskId': '840367013', 'state': 'Created'}
    # {'commtaskId': '840367013', 'state': 'Succeeded'}

    # dtm = dt.now()
    async with asyncio.timeout(3):
        _ = await wait_for_comm_task(evo, task_id)
    # assert (dt.now() - dtm).total_seconds() < 2

    #
    # PART 2A: Try different capitalisations of the JSON keys...
    new_mode = {
        SZ_MODE: ZoneMode.TEMPORARY_OVERRIDE,
        SZ_STATE: DhwState.ON,
        SZ_UNTIL_TIME: (dt.now() + td(hours=1)).strftime(API_STRFTIME),
    }
    _ = await should_work(evo, HTTPMethod.PUT, put_url, json=new_mode)  # HTTP 201

    async with asyncio.timeout(3):
        _ = await wait_for_comm_task(evo, task_id)
    status = await should_work(evo, HTTPMethod.GET, get_url)

    new_mode = {  # NOTE: different capitalisation, until time
        pascal_case(SZ_MODE): ZoneMode.TEMPORARY_OVERRIDE,
        pascal_case(SZ_STATE): DhwState.ON,
        pascal_case(SZ_UNTIL_TIME): (dt.now() + td(hours=2)).strftime(API_STRFTIME),
    }
    _ = await should_work(evo, HTTPMethod.PUT, put_url, json=new_mode)
    _ = await wait_for_comm_task(evo, task_id)
    status = await should_work(evo, HTTPMethod.GET, get_url)

    #
    # PART 3: Restore the original mode
    _ = await should_work(evo, HTTPMethod.PUT, put_url, json=old_mode)
    _ = await wait_for_comm_task(evo, task_id)
    status = await should_work(evo, HTTPMethod.GET, get_url)

    assert status  # == old_status

    #
    # PART 4A: Try bad JSON...
    bad_mode = {
        SZ_STATE: ZoneMode.TEMPORARY_OVERRIDE,
        SZ_MODE: DhwState.OFF,
        SZ_UNTIL_TIME: None,
    }
    _ = await should_fail(
        evo, HTTPMethod.PUT, put_url, json=bad_mode, status=HTTPStatus.BAD_REQUEST
    )
    # x = [{
    #     "code": "InvalidInput", "message": """
    #         Error converting value 'TemporaryOverride'
    #         to type 'DomesticHotWater.Enums.EMEADomesticHotWaterState'.
    #         Path 'state', line 1, position 29.
    #     """
    # }, {
    #     "code": "InvalidInput", "message": """
    #         Error converting value 'Off'
    #         to type 'DomesticHotWater.Enums.EMEADomesticHotWaterSetpointMode'.
    #         Path 'mode', line 1, position 44.
    #     """
    # }]  # NOTE: message has been slightly edited for readability

    #
    # PART 4B: Try 'bad' task_id values...
    url_tsk = "commTasks?commTaskId=ABC"
    _ = await should_fail(
        evo, HTTPMethod.GET, url_tsk, status=HTTPStatus.BAD_REQUEST
    )  # [{"code": "InvalidInput", "message": "Invalid Input."}]

    url_tsk = "commTasks?commTaskId=12345678"
    _ = await should_fail(
        evo, HTTPMethod.GET, url_tsk, status=HTTPStatus.NOT_FOUND
    )  # [{"code": "CommTaskNotFound", "message": "Communication task not found."}]


#######################################################################################


async def test_task_id(
    user_credentials: tuple[str, str],
    session: aiohttp.ClientSession,
) -> None:
    """Test /location/{locationId}/status"""

    if not _DBG_USE_REAL_AIOHTTP:
        pytest.skip(ExitTestReason.NOT_IMPLEMENTED)

    try:
        await _test_task_id(await instantiate_client_v2(user_credentials, session))

    except evo2.AuthenticationFailedError as err:
        if not _DBG_USE_REAL_AIOHTTP:
            raise
        pytest.skip(ExitTestReason.AUTHENTICATE_FAIL + f": {err}")
