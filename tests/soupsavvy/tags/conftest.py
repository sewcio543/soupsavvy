"""Common fixtures for tags components tests."""

from bs4 import BeautifulSoup as BS

# default bs4 parser
PARSER = "lxml"


def to_bs(html: str, parser: str = PARSER) -> BS:
    """Converts raw string html to BeautifulSoup object."""
    return BS(html, parser)


def strip(markup: str) -> str:
    """Converts raw string html to format matching str(BS) format."""
    return markup.replace("  ", "").strip("\n")
