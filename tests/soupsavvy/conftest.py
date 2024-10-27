"""
Common fixtures and mocks for selectors and operations tests
that are shared across multiple test modules.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any, Optional

import pytest
from bs4 import BeautifulSoup
from lxml.etree import fromstring
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from soupsavvy.base import BaseOperation, SoupSelector
from soupsavvy.exceptions import BreakOperationException
from soupsavvy.implementation.bs4 import SoupElement
from soupsavvy.implementation.lxml import LXMLElement
from soupsavvy.implementation.selenium import SeleniumElement
from soupsavvy.interfaces import Element, IElement

# default bs4 parser
PARSER = "lxml"

ToElement = Callable[[str], IElement]

driver = None


@pytest.fixture
def to_element(request, implementation: str) -> Callable[[str], IElement]:
    if implementation == "bs4":
        return to_soup
    elif implementation == "lxml":
        return to_lxml
    elif implementation == "selenium":
        global driver

        if driver is None:
            driver = get_driver()

        return to_selenium
    else:
        raise ValueError(f"Unknown implementation type: {implementation}")


def to_soup(html: str, parser: str = PARSER) -> SoupElement:
    return find_body_element(SoupElement(BeautifulSoup(html, parser)))


def to_lxml(html: str, parser: str = PARSER) -> LXMLElement:
    root = fromstring(str(BeautifulSoup(html, parser)))
    return find_body_element(LXMLElement(root))


# HTML file path
HTML_FILE_PATH = os.path.join(os.path.dirname(__file__), "files", "example.html")


def get_driver() -> webdriver.Chrome:
    """Set up a single Chrome driver for the entire session."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-logging")
    options.add_argument("--silent")

    driver = webdriver.Chrome(options=options)
    driver.get(HTML_FILE_PATH)
    return driver


def to_selenium(html: str) -> SeleniumElement:
    """Function to replace HTML content and get the root element."""
    assert driver is not None, "Driver is not initialized"

    driver.execute_script("document.body.outerHTML = arguments[0];", html)
    body = driver.find_element(By.TAG_NAME, "body")
    return SeleniumElement(body)


def strip(markup: str) -> str:
    """Converts raw string html to format matching str(BS) format."""
    return markup.replace("  ", "").replace("\n", "")


def find_body_element(bs: Element) -> Element:
    """Helper function to find body element in bs4.Tag object."""
    return bs.find_all("body")[0]


class MockSelector(SoupSelector):
    """Mock class for testing SoupSelector interface."""

    def __eq__(self, x: object) -> bool:
        return id(self) == id(x)

    def __hash__(self) -> int:
        return hash(id(self))

    def find_all(
        self, tag: IElement, recursive: bool = True, limit=None
    ) -> list[IElement]:
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

    def find_all(
        self, tag: IElement, recursive: bool = True, limit=None
    ) -> list[IElement]:
        return tag.find_all("a", recursive=recursive, limit=limit)


class MockDivSelector(_MockSimpleComparable):
    """
    Mock selector class for testing purposes.
    Find every instance of div tag (with tag name 'div').
    Delegates the task to bs4.Tag.find_all method.
    """

    def find_all(
        self, tag: IElement, recursive: bool = True, limit=None
    ) -> list[IElement]:
        return tag.find_all("div", recursive=recursive, limit=limit)


class MockClassMenuSelector(_MockSimpleComparable):
    """
    Mock selector class for testing purposes.
    Find every element that has class attribute set to 'menu'.
    """

    def find_all(
        self, tag: IElement, recursive: bool = True, limit=None
    ) -> list[IElement]:
        return tag.find_all(attrs={"class": "menu"}, recursive=recursive, limit=limit)


class MockClassWidgetSelector(_MockSimpleComparable):
    """
    Mock selector class for testing purposes.
    Find every element that has class attribute set to 'widget'.
    """

    def find_all(
        self, tag: IElement, recursive: bool = True, limit=None
    ) -> list[IElement]:
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

    def _execute(self, arg: Optional[IElement]) -> Optional[str]:
        if arg is None and self.skip_none:
            return None

        return arg.get_text()  # type: ignore


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
