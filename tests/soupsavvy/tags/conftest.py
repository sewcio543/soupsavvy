"""Common fixtures for tags components tests."""

from bs4 import BeautifulSoup as BS
from bs4 import Tag

from soupsavvy.tags.base import SelectableSoup

# default bs4 parser
PARSER = "lxml"


def to_bs(html: str, parser: str = PARSER) -> BS:
    """Converts raw string html to BeautifulSoup object."""
    return BS(html, parser)


def strip(markup: str) -> str:
    """Converts raw string html to format matching str(BS) format."""
    return markup.replace("  ", "").strip("\n")


def find_body_element(bs: Tag) -> Tag:
    """Helper function to find body element in bs4.Tag object."""
    return bs.find("body")  # type: ignore


class MockLinkSelector(SelectableSoup):
    """
    Mock selector class for testing purposes.
    Find every instance of link tag (with tag name 'a').
    Delegates the task to bs4.Tag.find_all method.
    """

    def find_all(self, tag: Tag, recursive: bool = True, limit=None) -> list[Tag]:
        return tag.find_all("a", recursive=recursive, limit=limit)


class MockDivSelector(SelectableSoup):
    """
    Mock selector class for testing purposes.
    Find every instance of div tag (with tag name 'div').
    Delegates the task to bs4.Tag.find_all method.
    """

    def find_all(self, tag: Tag, recursive: bool = True, limit=None) -> list[Tag]:
        return tag.find_all("div", recursive=recursive, limit=limit)
