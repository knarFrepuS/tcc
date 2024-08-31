#!/usr/bin/env python3
"""Tests for evohome-async - helper functions."""

from __future__ import annotations

import inspect
import logging
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent


class ClientStub:
    broker = None
    _logger = logging.getLogger(__name__)


class GatewayStub:
    _broker = None
    _logger = logging.getLogger(__name__)
    location = None


def get_property_methods(obj: object) -> list[str]:
    """Return a list of property methods of an object."""
    return [
        name
        for name, value in inspect.getmembers(obj.__class__)
        if isinstance(value, property)
    ]
