"""
Common fixtures and mocks for selectors and operations tests
that are shared across multiple test modules.
"""

from typing import Any, Optional

from bs4 import BeautifulSoup, Tag

from soupsavvy.base import BaseOperation, SoupSelector
from soupsavvy.exceptions import BreakOperationException

# default bs4 parser
PARSER = "lxml"


def to_bs(html: str, parser: str = PARSER) -> BeautifulSoup:
    """Converts raw string html to BeautifulSoup object."""
    return BeautifulSoup(html, parser)


def strip(markup: str) -> str:
    """Converts raw string html to format matching str(BS) format."""
    return markup.replace("  ", "").replace("\n", "")


def find_body_element(bs: Tag) -> Tag:
    """Helper function to find body element in bs4.Tag object."""
    return bs.find("body")  # type: ignore


class MockSelector(SoupSelector):
    """Mock class for testing SoupSelector interface."""

    def __eq__(self, x: object) -> bool:
        return id(self) == id(x)

    def __hash__(self) -> int:
        return hash(id(self))

    def find_all(self, tag: Tag, recursive: bool = True, limit=None) -> list[Tag]:
        return []


class _MockSimpleComparable(MockSelector):
    """
    Mock class for testing SoupSelector interface, that provides simple __eq__ method.
    Instances are equal if they are of the same class.
    """

    def __eq__(self, x: object) -> bool:
        return isinstance(x, self.__class__)


class MockLinkSelector(_MockSimpleComparable):
    """
    Mock selector class for testing purposes.
    Find every instance of link tag (with tag name 'a').
    Delegates the task to bs4.Tag.find_all method.
    """

    def find_all(self, tag: Tag, recursive: bool = True, limit=None) -> list[Tag]:
        return tag.find_all("a", recursive=recursive, limit=limit)


class MockDivSelector(_MockSimpleComparable):
    """
    Mock selector class for testing purposes.
    Find every instance of div tag (with tag name 'div').
    Delegates the task to bs4.Tag.find_all method.
    """

    def find_all(self, tag: Tag, recursive: bool = True, limit=None) -> list[Tag]:
        return tag.find_all("div", recursive=recursive, limit=limit)


class MockClassMenuSelector(_MockSimpleComparable):
    """
    Mock selector class for testing purposes.
    Find every element that has class attribute set to 'menu'.
    """

    def find_all(self, tag: Tag, recursive: bool = True, limit=None) -> list[Tag]:
        return tag.find_all(attrs={"class": "menu"}, recursive=recursive, limit=limit)


class MockClassWidgetSelector(_MockSimpleComparable):
    """
    Mock selector class for testing purposes.
    Find every element that has class attribute set to 'widget'.
    """

    def find_all(self, tag: Tag, recursive: bool = True, limit=None) -> list[Tag]:
        return tag.find_all(attrs={"class": "widget"}, recursive=recursive, limit=limit)


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


class MockBreakOperation(BaseMockOperation):
    """
    Mock class for breaking operation, it raises BreakOperationException,
    which is used to break the execution of the pipeline.
    """

    def __init__(self, operation: BaseOperation) -> None:
        """Initializes MockBreakOperation with operation to execute"""
        self.operation = operation

    def _execute(self, arg: Any) -> Any:
        result = self.operation.execute(arg)
        raise BreakOperationException(result)
