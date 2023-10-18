#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#


class volErrorInvalid(Exception):  # used as a proxy for vol.error.Invalid
    pass


class EvoBaseError(Exception):
    pass


class AuthenticationError(EvoBaseError):
    """Exception raised when unable to get an access_token."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class InvalidSchedule(EvoBaseError):
    """The schedule is invalid."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class SingleTcsError(EvoBaseError):
    """There is not exactly one TCS available."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)
