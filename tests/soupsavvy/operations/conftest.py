"""Module with configuration for `soupsavvy` operations tests."""

from typing import Any, Optional

from bs4 import Tag

from soupsavvy.operations.base import BaseOperation


class BaseMockOperation(BaseOperation):
    """
    Base class for mock operations used in tests.
    Implements equality check based on class type.
    """

    def __eq__(self, x: Any) -> bool:
        return isinstance(x, self.__class__)


class MockTextOperation(BaseMockOperation):
    """Mock operation that returns text of the tag, using .text attribute."""

    def __init__(self, skip_none: bool = False) -> None:
        """
        Initializes MockTextOperation with optional skip_none parameter.

        Parameters
        ----------
        skip_none : bool, optional
            If True, skips None values and returns None when executing, by default False.
        """
        self.skip_none = skip_none

    def _execute(self, arg: Optional[Tag]) -> Optional[str]:
        if arg is None and self.skip_none:
            return None

        return arg.text  # type: ignore


class MockIntOperation(BaseMockOperation):
    """Mock operation that converts the argument to integer."""

    def _execute(self, arg: str) -> int:
        return int(arg)


class MockPlus10Operation(BaseMockOperation):
    """Mock operation that adds 10 to the argument."""

    def _execute(self, arg: int) -> int:
        return arg + 10
