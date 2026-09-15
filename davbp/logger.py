"""
Simple logging facilities
"""

import logging


def _get() -> logging.Logger:
    """
    Return a reference to a global logger
    """
    return logging.getLogger("davsdk.bestpractices")


def make_verbose() -> None:
    """
    Make the logger as verbose as possible
    """
    _get().setLevel(logging.DEBUG)


def warn(msg: str) -> None:
    """
    Emit a warning
    """
    _get().warning(msg)


def info(msg: str) -> None:
    """
    Emit an info message

    This currently uses `logging.warning` because `logging.info`
    doesn't produce output even when the level is set to `DEBUG`.
    This is inconsistent with the documented behavior.
    """
    _get().warning(msg)
