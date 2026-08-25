import logging


def _get() -> logging.Logger:
    return logging.getLogger("davsdk.bestpractices")


def make_verbose() -> None:
    _get().setLevel(logging.DEBUG)


def warn(msg: str) -> None:
    _get().warning(msg)


def info(msg: str) -> None:
    _get().warning(msg)
