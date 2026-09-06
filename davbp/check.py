"""
Utilities for handling the individual checks for the DAV/Tools dashboard
"""

import typing
from davbp.Repository import Repository as Repo


class Check(typing.Protocol):
    """
    A generic pass/fail check
    """

    @property
    def name(self) -> str:
        """
        Return the name of the check
        """

    def run(self, repo: Repo) -> bool:
        """
        Run the check

        Args:
            repo (Repo): The source repository

        Returns
            Returns True if the check passed. False, otherwise.
        """


class CheckResult:
    """
    The result of running a specific check
    """

    def __init__(self, name: str, result: bool):
        self.name = name
        self.result = result


_all_checks: [Check] = []


def register_check(check: Check) -> None:
    """
    Register the dashboard check `check` to be run

    This should be called by a module adding a new check
    """

    _all_checks.append(check)
    _all_checks.sort(key=lambda x: x.name)


def run_checks(repo: Repo) -> [CheckResult]:
    """
    Run all checks register with `register_check`

    Args:
        repo (Repo): The source repository

    Returns
        List of check results
    """

    return [CheckResult(c.name, c.run(repo)) for c in _all_checks]
