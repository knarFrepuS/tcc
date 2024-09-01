#!/usr/bin/env python3
"""evohome-async - test constants."""

from __future__ import annotations

from enum import StrEnum


class ExitTestReason(StrEnum):
    AUTHENTICATE_FAIL = "Failed to authenticate with the vendor server"
    MISSING_FIXTURE = "No {file} in {folder}"
    NO_TESTABLE_DHW = "No DHW found to test"
    NO_TESTABLE_ZONE = "No zone found to test"
    NOT_IMPLEMENTED = "This server API has not been faked"
