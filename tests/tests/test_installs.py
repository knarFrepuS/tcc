#!/usr/bin/env python3
"""Tests for evohome-async - validate the schemas of vendor's RESTful JSON."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import patch

import yaml

import evohomeasync2 as ev2

from .conftest import FIXTURES_DIR, TokenManager, broker_get
from .helpers import get_property_methods

if TYPE_CHECKING:
    import pytest
    from pytest_snapshot.plugin import Snapshot  # type: ignore[import-untyped]


_DEPRECATED_ATTRS = ("locationId", "gatewayId", "systemId", "zoneId", "zone_type")


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    folders = [
        p.name
        for p in FIXTURES_DIR.glob("*")
        if p.is_dir() and not p.name.startswith("_")
    ]
    metafunc.parametrize("install", sorted(folders))


async def test_system_snapshot(  # type: ignore[no-any-unimported]
    install: str, token_manager: TokenManager, snapshot: Snapshot
) -> None:
    """Test the user account schema against the corresponding JSON."""

    def obj_to_dict(obj: object) -> dict[str, Any]:
        return {
            attr: getattr(obj, attr)
            for attr in get_property_methods(obj)
            if attr not in _DEPRECATED_ATTRS
        }

    with patch("evohomeasync2.broker.Broker.get", broker_get(install)):
        evo = ev2.EvohomeClient(token_manager, token_manager.websession)

        await evo.login()

    assert evo

    loc = evo.locations[0]
    snapshot.assert_match(yaml.dump(obj_to_dict(loc), indent=4), "location.yml")

    gwy = loc.gateways[0]
    snapshot.assert_match(yaml.dump(obj_to_dict(gwy), indent=4), "gateway.yml")

    tcs = gwy.systems[0]
    snapshot.assert_match(yaml.dump(obj_to_dict(tcs), indent=4), "control_system.yml")

    dhw = tcs.hotwater
    snapshot.assert_match(yaml.dump(obj_to_dict(dhw), indent=4), "hot_water.yml")

    zones = {z.id: obj_to_dict(z) for z in tcs.zones}
    snapshot.assert_match(yaml.dump(zones, indent=4), "zones.yml")
