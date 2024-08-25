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

    def _execute(self, arg: Optional[Tag]) -> Optional[str]:
        if arg is None:
            return None

        return arg.text


class MockIntOperation(BaseMockOperation):
    """Mock operation that converts the argument to integer."""

    def _execute(self, arg: str) -> int:
        return int(arg)
