#!/usr/bin/env python3
"""evohome-async - validate the handling of vendor APIs (URLs)."""

from __future__ import annotations

from datetime import datetime as dt, timedelta as td
from http import HTTPMethod, HTTPStatus

import pytest

import evohomeasync2 as evo2
from evohomeasync2 import ControlSystem, Gateway, HotWater, Location
from evohomeasync2.const import API_STRFTIME, DhwState, ZoneMode
from evohomeasync2.schema.const import (
    S2_MODE,
    S2_STATE,
    S2_STATE_STATUS,
    S2_UNTIL,
    S2_UNTIL_TIME,
)
from evohomeasync2.schema.helpers import pascal_case

from .conftest import _DBG_USE_REAL_AIOHTTP, skipif_auth_failed
from .helpers import should_fail, should_work

#######################################################################################


async def _test_task_id(evo: evo2.EvohomeClientNew) -> None:
    """Test the task_id returned when using the vendor's RESTful APIs.

    This test can be used to prove that JSON keys are can be camelCase or PascalCase.
    """

    loc: Location
    gwy: Gateway
    tcs: ControlSystem

    _ = await evo.update(dont_update_status=True)

    dhw: HotWater | None = None

    for loc in evo.locations:
        for gwy in loc.gateways:
            for tcs in gwy.control_systems:
                if tcs.hotwater:
                    # if (dhw := tcs.hotwater) and dhw.temperatureStatus['isAvailable']:
                    dhw = tcs.hotwater
                    break

    else:  # No available DHW found
        pytest.skip("No available DHW found")

    assert dhw is not None  # type: ignore[unreachable]

    GET_URL = f"{dhw.TYPE}/{dhw.id}/status"
    PUT_URL = f"{dhw.TYPE}/{dhw.id}/state"

    #
    # PART 0: Get initial state...
    old_status = await should_work(evo, HTTPMethod.GET, GET_URL)
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
        S2_MODE: old_status[S2_STATE_STATUS][S2_MODE],
        S2_STATE: old_status[S2_STATE_STATUS][S2_STATE],
        S2_UNTIL_TIME: old_status[S2_STATE_STATUS].get(S2_UNTIL),
    }  # NOTE: untilTime/until

    #
    # PART 1: Try the basic functionality...
    # new_mode = {S2_MODE: ZoneMode.PERMANENT_OVERRIDE, S2_STATE: DhwState.OFF, S2_UNTIL_TIME: None}
    new_mode = {
        S2_MODE: ZoneMode.TEMPORARY_OVERRIDE,
        S2_STATE: DhwState.ON,
        S2_UNTIL_TIME: (dt.now() + td(hours=1)).strftime(API_STRFTIME),
    }

    result = await should_work(evo, HTTPMethod.PUT, PUT_URL, json=new_mode)
    assert isinstance(result, dict | list)  # mypy
    # {'id': '840367013'}  # HTTP 201/Created

    task_id = result[0]["id"] if isinstance(result, list) else result["id"]
    url_tsk = f"commTasks?commTaskId={task_id}"

    assert int(task_id)

    status = await should_work(evo, HTTPMethod.GET, url_tsk)
    # {'commtaskId': '840367013', 'state': 'Created'}
    # {'commtaskId': '840367013', 'state': 'Succeeded'}

    assert isinstance(status, dict)  # mypy
    assert status["commtaskId"] == task_id
    assert status["state"] in ("Created", "Running", "Succeeded")

    # async with asyncio.timeout(30):
    #     _ = await wait_for_comm_task(evo, task_id)

    #
    # PART 2A: Try different capitalisations of the JSON keys...
    new_mode = {
        S2_MODE: ZoneMode.TEMPORARY_OVERRIDE,
        S2_STATE: DhwState.ON,
        S2_UNTIL_TIME: (dt.now() + td(hours=1)).strftime(API_STRFTIME),
    }
    _ = await should_work(evo, HTTPMethod.PUT, PUT_URL, json=new_mode)  # HTTP 201

    # async with asyncio.timeout(30):
    #     _ = await wait_for_comm_task(evo, task_id)

    status = await should_work(evo, HTTPMethod.GET, GET_URL)

    new_mode = {  # NOTE: different capitalisation, until time
        pascal_case(S2_MODE): ZoneMode.TEMPORARY_OVERRIDE,
        pascal_case(S2_STATE): DhwState.ON,
        pascal_case(S2_UNTIL_TIME): (dt.now() + td(hours=2)).strftime(API_STRFTIME),
    }
    _ = await should_work(evo, HTTPMethod.PUT, PUT_URL, json=new_mode)

    # async with asyncio.timeout(30):
    #     _ = await wait_for_comm_task(evo, task_id)

    status = await should_work(evo, HTTPMethod.GET, GET_URL)

    #
    # PART 3: Restore the original mode
    _ = await should_work(evo, HTTPMethod.PUT, PUT_URL, json=old_mode)

    # async with asyncio.timeout(30):
    #    _ = await wait_for_comm_task(evo, task_id)

    status = await should_work(evo, HTTPMethod.GET, GET_URL)

    # assert status # != old_status

    #
    # PART 4A: Try bad JSON...
    bad_mode = {
        S2_STATE: ZoneMode.TEMPORARY_OVERRIDE,
        S2_MODE: DhwState.OFF,
        S2_UNTIL_TIME: None,
    }
    _ = await should_fail(
        evo, HTTPMethod.PUT, PUT_URL, json=bad_mode, status=HTTPStatus.BAD_REQUEST
    )

    # _ = [{
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


@skipif_auth_failed
async def test_task_id(evohome_v2: evo2.EvohomeClientNew) -> None:
    """Test /location/{loc.id}/status"""

    if not _DBG_USE_REAL_AIOHTTP:
        pytest.skip("Test is only valid with a real server")

    try:
        await _test_task_id(evohome_v2)

    except evo2.AuthenticationFailedError:
        if not _DBG_USE_REAL_AIOHTTP:
            raise
        pytest.skip("Unable to authenticate")
