#!/usr/bin/env python3
"""evohome-async - validate the handling of vendor APIs (URLs)."""

from __future__ import annotations

from http import HTTPMethod, HTTPStatus

import pytest

import evohomeasync as evohome

from . import _DEBUG_USE_REAL_AIOHTTP
from .helpers import aiohttp, instantiate_client_v1, should_fail_v1, should_work_v1


async def _test_url_locations(evo: evohome.EvohomeClient) -> None:
    # evo.broker._headers["sessionId"] = evo.user_info["sessionId"]  # what is this?
    user_id: int = evo.user_info["userID"]  # type: ignore[assignment]

    assert evo.broker.session_id

    url = f"locations?userId={user_id}&allData=True"
    _ = await should_work_v1(evo, HTTPMethod.GET, url)

    # why isn't this one METHOD_NOT_ALLOWED?
    _ = await should_fail_v1(evo, HTTPMethod.PUT, url, status=HTTPStatus.NOT_FOUND)

    url = f"locations?userId={user_id}"
    _ = await should_work_v1(evo, HTTPMethod.GET, url)

    url = "locations?userId=123456"
    _ = await should_fail_v1(evo, HTTPMethod.GET, url, status=HTTPStatus.UNAUTHORIZED)

    url = "locations?userId='123456'"
    _ = await should_fail_v1(evo, HTTPMethod.GET, url, status=HTTPStatus.BAD_REQUEST)

    url = "xxxxxxx"  # NOTE: a general test, not a test specific to the 'locations' URL
    _ = await should_fail_v1(
        evo,
        HTTPMethod.GET,
        url,
        status=HTTPStatus.NOT_FOUND,
        content_type="text/html",  # not the usual content-type
    )


async def _test_client_apis(evo: evohome.EvohomeClient):
    """Instantiate a client, and logon to the vendor API."""

    user_data = await evo._populate_user_data()
    assert user_data  # aka evo.user_data

    assert evo.user_info

    await evo._populate_locn_data()

    temps = await evo.get_temperatures()
    assert temps


async def test_locations(
    user_credentials: tuple[str, str], session: aiohttp.ClientSession
) -> None:
    """Test /locations"""

    if not _DEBUG_USE_REAL_AIOHTTP:
        pytest.skip("Mocked server not implemented")

    try:
        await _test_url_locations(
            await instantiate_client_v1(*user_credentials, session=session)
        )
    except evohome.AuthenticationFailed as err:
        pytest.skip(f"Unable to authenticate: {err}")


async def test_client_apis(
    user_credentials: tuple[str, str], session: aiohttp.ClientSession
) -> None:
    """Test _populate_user_data() & _populate_full_data()"""

    if not _DEBUG_USE_REAL_AIOHTTP:
        pytest.skip("Mocked server not implemented")

    try:
        await _test_client_apis(
            await instantiate_client_v1(*user_credentials, session=session)
        )
    except evohome.AuthenticationFailed:
        pytest.skip("Unable to authenticate")


USER_DATA = {
    "sessionId": "BE5F40A6-1234-1234-1234-A708947D638B",
    "userInfo": {
        "userID": 2263181,
        "username": "null@gmail.com",
        "firstname": "David",
        "lastname": "Smith",
        "streetAddress": "1 Main Street",
        "city": "London",
        "zipcode": "NW1 1AA",
        "country": "GB",
        "telephone": "",
        "userLanguage": "en-GB",
        "isActivated": True,
        "deviceCount": 0,
        "tenantID": 5,
        "securityQuestion1": "NotUsed",
        "securityQuestion2": "NotUsed",
        "securityQuestion3": "NotUsed",
        "latestEulaAccepted": False,
    },
}

FULL_DATA = {
    "locationID": 2738909,
    "name": "My Home",
    "streetAddress": "1 Main Street",
    "city": "London",
    "state": "",
    "country": "GB",
    "zipcode": "NW1 1AA",
    "type": "Residential",
    "hasStation": True,
    "devices": [
        {
            "gatewayId": 2499896,
            "deviceID": 3933910,
            "thermostatModelType": "DOMESTIC_HOT_WATER",
            "deviceType": 128,
            "name": "",
            "scheduleCapable": False,
            "holdUntilCapable": False,
            "thermostat": {
                "units": "Celsius",
                "indoorTemperature": 22.77,
                "outdoorTemperature": 128.0,
                "outdoorTemperatureAvailable": False,
                "outdoorHumidity": 128.0,
                "outdootHumidityAvailable": False,
                "indoorHumidity": 128.0,
                "indoorTemperatureStatus": "Measured",
                "indoorHumidityStatus": "NotAvailable",
                "outdoorTemperatureStatus": "NotAvailable",
                "outdoorHumidityStatus": "NotAvailable",
                "isCommercial": False,
                "allowedModes": ["DHWOn", "DHWOff"],
                "deadband": 0.0,
                "minHeatSetpoint": 5.0,
                "maxHeatSetpoint": 30.0,
                "minCoolSetpoint": 50.0,
                "maxCoolSetpoint": 90.0,
                "changeableValues": {"mode": "DHWOff", "status": "Scheduled"},
                "scheduleCapable": False,
                "vacationHoldChangeable": False,
                "vacationHoldCancelable": False,
                "scheduleHeatSp": 0.0,
                "scheduleCoolSp": 0.0,
            },
            "alertSettings": {
                "deviceID": 3933910,
                "tempHigherThanActive": True,
                "tempHigherThan": 30.0,
                "tempHigherThanMinutes": 0,
                "tempLowerThanActive": True,
                "tempLowerThan": 5.0,
                "tempLowerThanMinutes": 0,
                "faultConditionExistsActive": False,
                "faultConditionExistsHours": 0,
                "normalConditionsActive": True,
                "communicationLostActive": False,
                "communicationLostHours": 0,
                "communicationFailureActive": True,
                "communicationFailureMinutes": 15,
                "deviceLostActive": False,
                "deviceLostHours": 0,
            },
            "isUpgrading": False,
            "isAlive": True,
            "thermostatVersion": "02.00.19.33",
            "macID": "00D02DEE4E56",
            "locationID": 2738909,
            "domainID": 20054,
            "instance": 250,
        },
        {
            "gatewayId": 2499896,
            "deviceID": 3432579,
            "thermostatModelType": "EMEA_ZONE",
            "deviceType": 128,
            "name": "Bathroom Dn",
            "scheduleCapable": False,
            "holdUntilCapable": False,
            "thermostat": {
                "units": "Celsius",
                "indoorTemperature": 20.79,
                "outdoorTemperature": 128.0,
                "outdoorTemperatureAvailable": False,
                "outdoorHumidity": 128.0,
                "outdootHumidityAvailable": False,
                "indoorHumidity": 128.0,
                "indoorTemperatureStatus": "Measured",
                "indoorHumidityStatus": "NotAvailable",
                "outdoorTemperatureStatus": "NotAvailable",
                "outdoorHumidityStatus": "NotAvailable",
                "isCommercial": False,
                "allowedModes": ["Heat", "Off"],
                "deadband": 0.0,
                "minHeatSetpoint": 5.0,
                "maxHeatSetpoint": 35.0,
                "minCoolSetpoint": 50.0,
                "maxCoolSetpoint": 90.0,
                "changeableValues": {
                    "mode": "Off",
                    "heatSetpoint": {"value": 15.0, "status": "Scheduled"},
                    "vacationHoldDays": 0,
                },
                "scheduleCapable": False,
                "vacationHoldChangeable": False,
                "vacationHoldCancelable": False,
                "scheduleHeatSp": 0.0,
                "scheduleCoolSp": 0.0,
            },
            "alertSettings": {
                "deviceID": 3432579,
                "tempHigherThanActive": True,
                "tempHigherThan": 30.0,
                "tempHigherThanMinutes": 0,
                "tempLowerThanActive": True,
                "tempLowerThan": 5.0,
                "tempLowerThanMinutes": 0,
                "faultConditionExistsActive": False,
                "faultConditionExistsHours": 0,
                "normalConditionsActive": True,
                "communicationLostActive": False,
                "communicationLostHours": 0,
                "communicationFailureActive": True,
                "communicationFailureMinutes": 15,
                "deviceLostActive": False,
                "deviceLostHours": 0,
            },
            "isUpgrading": False,
            "isAlive": True,
            "thermostatVersion": "02.00.19.33",
            "macID": "00D02DEE4E56",
            "locationID": 2738909,
            "domainID": 20054,
            "instance": 4,
        },
        {
            "gatewayId": 2499896,
            "deviceID": 3449740,
            "thermostatModelType": "EMEA_ZONE",
            "deviceType": 128,
            "name": "Bathroom Up",
            "scheduleCapable": False,
            "holdUntilCapable": False,
            "thermostat": {
                "units": "Celsius",
                "indoorTemperature": 20.26,
                "outdoorTemperature": 128.0,
                "outdoorTemperatureAvailable": False,
                "outdoorHumidity": 128.0,
                "outdootHumidityAvailable": False,
                "indoorHumidity": 128.0,
                "indoorTemperatureStatus": "Measured",
                "indoorHumidityStatus": "NotAvailable",
                "outdoorTemperatureStatus": "NotAvailable",
                "outdoorHumidityStatus": "NotAvailable",
                "isCommercial": False,
                "allowedModes": ["Heat", "Off"],
                "deadband": 0.0,
                "minHeatSetpoint": 5.0,
                "maxHeatSetpoint": 35.0,
                "minCoolSetpoint": 50.0,
                "maxCoolSetpoint": 90.0,
                "changeableValues": {
                    "mode": "Off",
                    "heatSetpoint": {"value": 19.0, "status": "Scheduled"},
                    "vacationHoldDays": 0,
                },
                "scheduleCapable": False,
                "vacationHoldChangeable": False,
                "vacationHoldCancelable": False,
                "scheduleHeatSp": 0.0,
                "scheduleCoolSp": 0.0,
            },
            "alertSettings": {
                "deviceID": 3449740,
                "tempHigherThanActive": True,
                "tempHigherThan": 30.0,
                "tempHigherThanMinutes": 0,
                "tempLowerThanActive": True,
                "tempLowerThan": 5.0,
                "tempLowerThanMinutes": 0,
                "faultConditionExistsActive": False,
                "faultConditionExistsHours": 0,
                "normalConditionsActive": True,
                "communicationLostActive": False,
                "communicationLostHours": 0,
                "communicationFailureActive": True,
                "communicationFailureMinutes": 15,
                "deviceLostActive": False,
                "deviceLostHours": 0,
            },
            "isUpgrading": False,
            "isAlive": True,
            "thermostatVersion": "02.00.19.33",
            "macID": "00D02DEE4E56",
            "locationID": 2738909,
            "domainID": 20054,
            "instance": 7,
        },
        {
            "gatewayId": 2499896,
            "deviceID": 3432521,
            "thermostatModelType": "EMEA_ZONE",
            "deviceType": 128,
            "name": "Dead Zone",
            "scheduleCapable": False,
            "holdUntilCapable": False,
            "thermostat": {
                "units": "Celsius",
                "indoorTemperature": 128.0,
                "outdoorTemperature": 128.0,
                "outdoorTemperatureAvailable": False,
                "outdoorHumidity": 128.0,
                "outdootHumidityAvailable": False,
                "indoorHumidity": 128.0,
                "indoorTemperatureStatus": "NotAvailable",
                "indoorHumidityStatus": "NotAvailable",
                "outdoorTemperatureStatus": "NotAvailable",
                "outdoorHumidityStatus": "NotAvailable",
                "isCommercial": False,
                "allowedModes": ["Heat", "Off"],
                "deadband": 0.0,
                "minHeatSetpoint": 5.0,
                "maxHeatSetpoint": 35.0,
                "minCoolSetpoint": 50.0,
                "maxCoolSetpoint": 90.0,
                "changeableValues": {
                    "mode": "Off",
                    "heatSetpoint": {"value": 5.0, "status": "Scheduled"},
                    "vacationHoldDays": 0,
                },
                "scheduleCapable": False,
                "vacationHoldChangeable": False,
                "vacationHoldCancelable": False,
                "scheduleHeatSp": 0.0,
                "scheduleCoolSp": 0.0,
            },
            "alertSettings": {
                "deviceID": 3432521,
                "tempHigherThanActive": True,
                "tempHigherThan": 30.0,
                "tempHigherThanMinutes": 0,
                "tempLowerThanActive": True,
                "tempLowerThan": 5.0,
                "tempLowerThanMinutes": 0,
                "faultConditionExistsActive": False,
                "faultConditionExistsHours": 0,
                "normalConditionsActive": True,
                "communicationLostActive": False,
                "communicationLostHours": 0,
                "communicationFailureActive": True,
                "communicationFailureMinutes": 15,
                "deviceLostActive": False,
                "deviceLostHours": 0,
            },
            "isUpgrading": False,
            "isAlive": True,
            "thermostatVersion": "02.00.19.33",
            "macID": "00D02DEE4E56",
            "locationID": 2738909,
            "domainID": 20054,
            "instance": 0,
        },
        {
            "gatewayId": 2499896,
            "deviceID": 5333958,
            "thermostatModelType": "EMEA_ZONE",
            "deviceType": 128,
            "name": "Eh",
            "scheduleCapable": False,
            "holdUntilCapable": False,
            "thermostat": {
                "units": "Celsius",
                "indoorTemperature": 128.0,
                "outdoorTemperature": 128.0,
                "outdoorTemperatureAvailable": False,
                "outdoorHumidity": 128.0,
                "outdootHumidityAvailable": False,
                "indoorHumidity": 128.0,
                "indoorTemperatureStatus": "NotAvailable",
                "indoorHumidityStatus": "NotAvailable",
                "outdoorTemperatureStatus": "NotAvailable",
                "outdoorHumidityStatus": "NotAvailable",
                "isCommercial": False,
                "allowedModes": ["Heat", "Off"],
                "deadband": 0.0,
                "minHeatSetpoint": 5.0,
                "maxHeatSetpoint": 35.0,
                "minCoolSetpoint": 50.0,
                "maxCoolSetpoint": 90.0,
                "changeableValues": {
                    "mode": "Off",
                    "heatSetpoint": {"value": 21.0, "status": "Scheduled"},
                    "vacationHoldDays": 0,
                },
                "scheduleCapable": False,
                "vacationHoldChangeable": False,
                "vacationHoldCancelable": False,
                "scheduleHeatSp": 0.0,
                "scheduleCoolSp": 0.0,
            },
            "alertSettings": {
                "deviceID": 5333958,
                "tempHigherThanActive": True,
                "tempHigherThan": 30.0,
                "tempHigherThanMinutes": 0,
                "tempLowerThanActive": True,
                "tempLowerThan": 5.0,
                "tempLowerThanMinutes": 0,
                "faultConditionExistsActive": False,
                "faultConditionExistsHours": 0,
                "normalConditionsActive": True,
                "communicationLostActive": False,
                "communicationLostHours": 0,
                "communicationFailureActive": True,
                "communicationFailureMinutes": 15,
                "deviceLostActive": False,
                "deviceLostHours": 0,
            },
            "isUpgrading": False,
            "isAlive": True,
            "thermostatVersion": "02.00.19.33",
            "macID": "00D02DEE4E56",
            "locationID": 2738909,
            "domainID": 20054,
            "instance": 11,
        },
        {
            "gatewayId": 2499896,
            "deviceID": 3432577,
            "thermostatModelType": "EMEA_ZONE",
            "deviceType": 128,
            "name": "Front Room",
            "scheduleCapable": False,
            "holdUntilCapable": False,
            "thermostat": {
                "units": "Celsius",
                "indoorTemperature": 19.83,
                "outdoorTemperature": 128.0,
                "outdoorTemperatureAvailable": False,
                "outdoorHumidity": 128.0,
                "outdootHumidityAvailable": False,
                "indoorHumidity": 128.0,
                "indoorTemperatureStatus": "Measured",
                "indoorHumidityStatus": "NotAvailable",
                "outdoorTemperatureStatus": "NotAvailable",
                "outdoorHumidityStatus": "NotAvailable",
                "isCommercial": False,
                "allowedModes": ["Heat", "Off"],
                "deadband": 0.0,
                "minHeatSetpoint": 5.0,
                "maxHeatSetpoint": 35.0,
                "minCoolSetpoint": 50.0,
                "maxCoolSetpoint": 90.0,
                "changeableValues": {
                    "mode": "Off",
                    "heatSetpoint": {"value": 20.5, "status": "Scheduled"},
                    "vacationHoldDays": 0,
                },
                "scheduleCapable": False,
                "vacationHoldChangeable": False,
                "vacationHoldCancelable": False,
                "scheduleHeatSp": 0.0,
                "scheduleCoolSp": 0.0,
            },
            "alertSettings": {
                "deviceID": 3432577,
                "tempHigherThanActive": True,
                "tempHigherThan": 30.0,
                "tempHigherThanMinutes": 0,
                "tempLowerThanActive": True,
                "tempLowerThan": 5.0,
                "tempLowerThanMinutes": 0,
                "faultConditionExistsActive": False,
                "faultConditionExistsHours": 0,
                "normalConditionsActive": True,
                "communicationLostActive": False,
                "communicationLostHours": 0,
                "communicationFailureActive": True,
                "communicationFailureMinutes": 15,
                "deviceLostActive": False,
                "deviceLostHours": 0,
            },
            "isUpgrading": False,
            "isAlive": True,
            "thermostatVersion": "02.00.19.33",
            "macID": "00D02DEE4E56",
            "locationID": 2738909,
            "domainID": 20054,
            "instance": 2,
        },
        {
            "gatewayId": 2499896,
            "deviceID": 3449703,
            "thermostatModelType": "EMEA_ZONE",
            "deviceType": 128,
            "name": "Kids Room",
            "scheduleCapable": False,
            "holdUntilCapable": False,
            "thermostat": {
                "units": "Celsius",
                "indoorTemperature": 19.53,
                "outdoorTemperature": 128.0,
                "outdoorTemperatureAvailable": False,
                "outdoorHumidity": 128.0,
                "outdootHumidityAvailable": False,
                "indoorHumidity": 128.0,
                "indoorTemperatureStatus": "Measured",
                "indoorHumidityStatus": "NotAvailable",
                "outdoorTemperatureStatus": "NotAvailable",
                "outdoorHumidityStatus": "NotAvailable",
                "isCommercial": False,
                "allowedModes": ["Heat", "Off"],
                "deadband": 0.0,
                "minHeatSetpoint": 5.0,
                "maxHeatSetpoint": 35.0,
                "minCoolSetpoint": 50.0,
                "maxCoolSetpoint": 90.0,
                "changeableValues": {
                    "mode": "Off",
                    "heatSetpoint": {"value": 16.0, "status": "Scheduled"},
                    "vacationHoldDays": 0,
                },
                "scheduleCapable": False,
                "vacationHoldChangeable": False,
                "vacationHoldCancelable": False,
                "scheduleHeatSp": 0.0,
                "scheduleCoolSp": 0.0,
            },
            "alertSettings": {
                "deviceID": 3449703,
                "tempHigherThanActive": True,
                "tempHigherThan": 30.0,
                "tempHigherThanMinutes": 0,
                "tempLowerThanActive": True,
                "tempLowerThan": 5.0,
                "tempLowerThanMinutes": 0,
                "faultConditionExistsActive": False,
                "faultConditionExistsHours": 0,
                "normalConditionsActive": True,
                "communicationLostActive": False,
                "communicationLostHours": 0,
                "communicationFailureActive": True,
                "communicationFailureMinutes": 15,
                "deviceLostActive": False,
                "deviceLostHours": 0,
            },
            "isUpgrading": False,
            "isAlive": True,
            "thermostatVersion": "02.00.19.33",
            "macID": "00D02DEE4E56",
            "locationID": 2738909,
            "domainID": 20054,
            "instance": 6,
        },
        {
            "gatewayId": 2499896,
            "deviceID": 3432578,
            "thermostatModelType": "EMEA_ZONE",
            "deviceType": 128,
            "name": "Kitchen",
            "scheduleCapable": False,
            "holdUntilCapable": False,
            "thermostat": {
                "units": "Celsius",
                "indoorTemperature": 20.43,
                "outdoorTemperature": 128.0,
                "outdoorTemperatureAvailable": False,
                "outdoorHumidity": 128.0,
                "outdootHumidityAvailable": False,
                "indoorHumidity": 128.0,
                "indoorTemperatureStatus": "Measured",
                "indoorHumidityStatus": "NotAvailable",
                "outdoorTemperatureStatus": "NotAvailable",
                "outdoorHumidityStatus": "NotAvailable",
                "isCommercial": False,
                "allowedModes": ["Heat", "Off"],
                "deadband": 0.0,
                "minHeatSetpoint": 5.0,
                "maxHeatSetpoint": 35.0,
                "minCoolSetpoint": 50.0,
                "maxCoolSetpoint": 90.0,
                "changeableValues": {
                    "mode": "Off",
                    "heatSetpoint": {"value": 15.0, "status": "Scheduled"},
                    "vacationHoldDays": 0,
                },
                "scheduleCapable": False,
                "vacationHoldChangeable": False,
                "vacationHoldCancelable": False,
                "scheduleHeatSp": 0.0,
                "scheduleCoolSp": 0.0,
            },
            "alertSettings": {
                "deviceID": 3432578,
                "tempHigherThanActive": True,
                "tempHigherThan": 30.0,
                "tempHigherThanMinutes": 0,
                "tempLowerThanActive": True,
                "tempLowerThan": 5.0,
                "tempLowerThanMinutes": 0,
                "faultConditionExistsActive": False,
                "faultConditionExistsHours": 0,
                "normalConditionsActive": True,
                "communicationLostActive": False,
                "communicationLostHours": 0,
                "communicationFailureActive": True,
                "communicationFailureMinutes": 15,
                "deviceLostActive": False,
                "deviceLostHours": 0,
            },
            "isUpgrading": False,
            "isAlive": True,
            "thermostatVersion": "02.00.19.33",
            "macID": "00D02DEE4E56",
            "locationID": 2738909,
            "domainID": 20054,
            "instance": 3,
        },
        {
            "gatewayId": 2499896,
            "deviceID": 3432580,
            "thermostatModelType": "EMEA_ZONE",
            "deviceType": 128,
            "name": "Main Bedroom",
            "scheduleCapable": False,
            "holdUntilCapable": False,
            "thermostat": {
                "units": "Celsius",
                "indoorTemperature": 20.72,
                "outdoorTemperature": 128.0,
                "outdoorTemperatureAvailable": False,
                "outdoorHumidity": 128.0,
                "outdootHumidityAvailable": False,
                "indoorHumidity": 128.0,
                "indoorTemperatureStatus": "Measured",
                "indoorHumidityStatus": "NotAvailable",
                "outdoorTemperatureStatus": "NotAvailable",
                "outdoorHumidityStatus": "NotAvailable",
                "isCommercial": False,
                "allowedModes": ["Heat", "Off"],
                "deadband": 0.0,
                "minHeatSetpoint": 5.0,
                "maxHeatSetpoint": 35.0,
                "minCoolSetpoint": 50.0,
                "maxCoolSetpoint": 90.0,
                "changeableValues": {
                    "mode": "Off",
                    "heatSetpoint": {"value": 16.0, "status": "Scheduled"},
                    "vacationHoldDays": 0,
                },
                "scheduleCapable": False,
                "vacationHoldChangeable": False,
                "vacationHoldCancelable": False,
                "scheduleHeatSp": 0.0,
                "scheduleCoolSp": 0.0,
            },
            "alertSettings": {
                "deviceID": 3432580,
                "tempHigherThanActive": True,
                "tempHigherThan": 30.0,
                "tempHigherThanMinutes": 0,
                "tempLowerThanActive": True,
                "tempLowerThan": 5.0,
                "tempLowerThanMinutes": 0,
                "faultConditionExistsActive": False,
                "faultConditionExistsHours": 0,
                "normalConditionsActive": True,
                "communicationLostActive": False,
                "communicationLostHours": 0,
                "communicationFailureActive": True,
                "communicationFailureMinutes": 15,
                "deviceLostActive": False,
                "deviceLostHours": 0,
            },
            "isUpgrading": False,
            "isAlive": True,
            "thermostatVersion": "02.00.19.33",
            "macID": "00D02DEE4E56",
            "locationID": 2738909,
            "domainID": 20054,
            "instance": 5,
        },
        {
            "gatewayId": 2499896,
            "deviceID": 3432576,
            "thermostatModelType": "EMEA_ZONE",
            "deviceType": 128,
            "name": "Main Room",
            "scheduleCapable": False,
            "holdUntilCapable": False,
            "thermostat": {
                "units": "Celsius",
                "indoorTemperature": 20.14,
                "outdoorTemperature": 128.0,
                "outdoorTemperatureAvailable": False,
                "outdoorHumidity": 128.0,
                "outdootHumidityAvailable": False,
                "indoorHumidity": 128.0,
                "indoorTemperatureStatus": "Measured",
                "indoorHumidityStatus": "NotAvailable",
                "outdoorTemperatureStatus": "NotAvailable",
                "outdoorHumidityStatus": "NotAvailable",
                "isCommercial": False,
                "allowedModes": ["Heat", "Off"],
                "deadband": 0.0,
                "minHeatSetpoint": 5.0,
                "maxHeatSetpoint": 35.0,
                "minCoolSetpoint": 50.0,
                "maxCoolSetpoint": 90.0,
                "changeableValues": {
                    "mode": "Off",
                    "heatSetpoint": {"value": 15.0, "status": "Scheduled"},
                    "vacationHoldDays": 0,
                },
                "scheduleCapable": False,
                "vacationHoldChangeable": False,
                "vacationHoldCancelable": False,
                "scheduleHeatSp": 0.0,
                "scheduleCoolSp": 0.0,
            },
            "alertSettings": {
                "deviceID": 3432576,
                "tempHigherThanActive": True,
                "tempHigherThan": 30.0,
                "tempHigherThanMinutes": 0,
                "tempLowerThanActive": True,
                "tempLowerThan": 5.0,
                "tempLowerThanMinutes": 0,
                "faultConditionExistsActive": False,
                "faultConditionExistsHours": 0,
                "normalConditionsActive": True,
                "communicationLostActive": False,
                "communicationLostHours": 0,
                "communicationFailureActive": True,
                "communicationFailureMinutes": 15,
                "deviceLostActive": False,
                "deviceLostHours": 0,
            },
            "isUpgrading": False,
            "isAlive": True,
            "thermostatVersion": "02.00.19.33",
            "macID": "00D02DEE4E56",
            "locationID": 2738909,
            "domainID": 20054,
            "instance": 1,
        },
        {
            "gatewayId": 2499896,
            "deviceID": 3450733,
            "thermostatModelType": "EMEA_ZONE",
            "deviceType": 128,
            "name": "Spare Room",
            "scheduleCapable": False,
            "holdUntilCapable": False,
            "thermostat": {
                "units": "Celsius",
                "indoorTemperature": 18.81,
                "outdoorTemperature": 128.0,
                "outdoorTemperatureAvailable": False,
                "outdoorHumidity": 128.0,
                "outdootHumidityAvailable": False,
                "indoorHumidity": 128.0,
                "indoorTemperatureStatus": "Measured",
                "indoorHumidityStatus": "NotAvailable",
                "outdoorTemperatureStatus": "NotAvailable",
                "outdoorHumidityStatus": "NotAvailable",
                "isCommercial": False,
                "allowedModes": ["Heat", "Off"],
                "deadband": 0.0,
                "minHeatSetpoint": 5.0,
                "maxHeatSetpoint": 35.0,
                "minCoolSetpoint": 50.0,
                "maxCoolSetpoint": 90.0,
                "changeableValues": {
                    "mode": "Off",
                    "heatSetpoint": {"value": 16.0, "status": "Scheduled"},
                    "vacationHoldDays": 0,
                },
                "scheduleCapable": False,
                "vacationHoldChangeable": False,
                "vacationHoldCancelable": False,
                "scheduleHeatSp": 0.0,
                "scheduleCoolSp": 0.0,
            },
            "alertSettings": {
                "deviceID": 3450733,
                "tempHigherThanActive": True,
                "tempHigherThan": 30.0,
                "tempHigherThanMinutes": 0,
                "tempLowerThanActive": True,
                "tempLowerThan": 5.0,
                "tempLowerThanMinutes": 0,
                "faultConditionExistsActive": False,
                "faultConditionExistsHours": 0,
                "normalConditionsActive": True,
                "communicationLostActive": False,
                "communicationLostHours": 0,
                "communicationFailureActive": True,
                "communicationFailureMinutes": 15,
                "deviceLostActive": False,
                "deviceLostHours": 0,
            },
            "isUpgrading": False,
            "isAlive": True,
            "thermostatVersion": "02.00.19.33",
            "macID": "00D02DEE4E56",
            "locationID": 2738909,
            "domainID": 20054,
            "instance": 8,
        },
        {
            "gatewayId": 2499896,
            "deviceID": 5333957,
            "thermostatModelType": "EMEA_ZONE",
            "deviceType": 128,
            "name": "UFH",
            "scheduleCapable": False,
            "holdUntilCapable": False,
            "thermostat": {
                "units": "Celsius",
                "indoorTemperature": 128.0,
                "outdoorTemperature": 128.0,
                "outdoorTemperatureAvailable": False,
                "outdoorHumidity": 128.0,
                "outdootHumidityAvailable": False,
                "indoorHumidity": 128.0,
                "indoorTemperatureStatus": "NotAvailable",
                "indoorHumidityStatus": "NotAvailable",
                "outdoorTemperatureStatus": "NotAvailable",
                "outdoorHumidityStatus": "NotAvailable",
                "isCommercial": False,
                "allowedModes": ["Heat", "Off"],
                "deadband": 0.0,
                "minHeatSetpoint": 5.0,
                "maxHeatSetpoint": 35.0,
                "minCoolSetpoint": 50.0,
                "maxCoolSetpoint": 90.0,
                "changeableValues": {
                    "mode": "Off",
                    "heatSetpoint": {"value": 21.0, "status": "Scheduled"},
                    "vacationHoldDays": 0,
                },
                "scheduleCapable": False,
                "vacationHoldChangeable": False,
                "vacationHoldCancelable": False,
                "scheduleHeatSp": 0.0,
                "scheduleCoolSp": 0.0,
            },
            "alertSettings": {
                "deviceID": 5333957,
                "tempHigherThanActive": True,
                "tempHigherThan": 30.0,
                "tempHigherThanMinutes": 0,
                "tempLowerThanActive": True,
                "tempLowerThan": 5.0,
                "tempLowerThanMinutes": 0,
                "faultConditionExistsActive": False,
                "faultConditionExistsHours": 0,
                "normalConditionsActive": True,
                "communicationLostActive": False,
                "communicationLostHours": 0,
                "communicationFailureActive": True,
                "communicationFailureMinutes": 15,
                "deviceLostActive": False,
                "deviceLostHours": 0,
            },
            "isUpgrading": False,
            "isAlive": True,
            "thermostatVersion": "02.00.19.33",
            "macID": "00D02DEE4E56",
            "locationID": 2738909,
            "domainID": 20054,
            "instance": 10,
        },
        {
            "gatewayId": 2499896,
            "deviceID": 5333955,
            "thermostatModelType": "EMEA_ZONE",
            "deviceType": 128,
            "name": "Zv",
            "scheduleCapable": False,
            "holdUntilCapable": False,
            "thermostat": {
                "units": "Celsius",
                "indoorTemperature": 128.0,
                "outdoorTemperature": 128.0,
                "outdoorTemperatureAvailable": False,
                "outdoorHumidity": 128.0,
                "outdootHumidityAvailable": False,
                "indoorHumidity": 128.0,
                "indoorTemperatureStatus": "NotAvailable",
                "indoorHumidityStatus": "NotAvailable",
                "outdoorTemperatureStatus": "NotAvailable",
                "outdoorHumidityStatus": "NotAvailable",
                "isCommercial": False,
                "allowedModes": ["Heat", "Off"],
                "deadband": 0.0,
                "minHeatSetpoint": 5.0,
                "maxHeatSetpoint": 35.0,
                "minCoolSetpoint": 50.0,
                "maxCoolSetpoint": 90.0,
                "changeableValues": {
                    "mode": "Off",
                    "heatSetpoint": {"value": 21.0, "status": "Scheduled"},
                    "vacationHoldDays": 0,
                },
                "scheduleCapable": False,
                "vacationHoldChangeable": False,
                "vacationHoldCancelable": False,
                "scheduleHeatSp": 0.0,
                "scheduleCoolSp": 0.0,
            },
            "alertSettings": {
                "deviceID": 5333955,
                "tempHigherThanActive": True,
                "tempHigherThan": 30.0,
                "tempHigherThanMinutes": 0,
                "tempLowerThanActive": True,
                "tempLowerThan": 5.0,
                "tempLowerThanMinutes": 0,
                "faultConditionExistsActive": False,
                "faultConditionExistsHours": 0,
                "normalConditionsActive": True,
                "communicationLostActive": False,
                "communicationLostHours": 0,
                "communicationFailureActive": True,
                "communicationFailureMinutes": 15,
                "deviceLostActive": False,
                "deviceLostHours": 0,
            },
            "isUpgrading": False,
            "isAlive": True,
            "thermostatVersion": "02.00.19.33",
            "macID": "00D02DEE4E56",
            "locationID": 2738909,
            "domainID": 20054,
            "instance": 9,
        },
    ],
    "oneTouchButtons": [],
    "weather": {
        "condition": "NightClear",
        "temperature": 9.0,
        "units": "Celsius",
        "humidity": 87,
        "phrase": "Clear",
    },
    "daylightSavingTimeEnabled": True,
    "timeZone": {
        "id": "GMT Standard Time",
        "displayName": "(UTC+00:00) Dublin, Edinburgh, Lisbon, London",
        "offsetMinutes": 0,
        "currentOffsetMinutes": 0,
        "usingDaylightSavingTime": True,
    },
    "oneTouchActionsSuspended": False,
    "isLocationOwner": True,
    "locationOwnerID": 2263181,
    "locationOwnerName": "David Smith",
    "locationOwnerUserName": "null@gmail.com",
    "canSearchForContractors": True,
    "contractor": {
        "info": {"contractorID": 1839},
        "monitoring": {"levelOfAccess": "Partial", "contactPreferences": []},
    },
}
