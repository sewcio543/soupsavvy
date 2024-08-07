"""Common fixtures for tags components tests."""

from bs4 import BeautifulSoup as BS
from bs4 import Tag

from soupsavvy.tags.base import SoupSelector

# default bs4 parser
PARSER = "lxml"


def to_bs(html: str, parser: str = PARSER) -> BS:
    """Converts raw string html to BeautifulSoup object."""
    return BS(html, parser)


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
