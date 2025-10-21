"""
Common fixtures and mocks for selectors and operations tests
that are shared across multiple test modules.
"""

from __future__ import annotations

import asyncio
import os
import sys

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import threading
from collections.abc import Callable
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any, Optional, cast

import pytest
from bs4 import BeautifulSoup
from lxml.etree import fromstring
from playwright.sync_api import Browser, Page, sync_playwright
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from soupsavvy.base import BaseOperation, SoupSelector
from soupsavvy.exceptions import BreakOperationException
from soupsavvy.implementation.bs4 import SoupElement
from soupsavvy.implementation.lxml import LXMLElement
from soupsavvy.implementation.playwright import PlaywrightElement
from soupsavvy.implementation.selenium import SeleniumElement
from soupsavvy.interfaces import IElement
from soupsavvy.models import BaseModel
from tests.conftest import BS4, LXML, PLAYWRIGHT, SELENIUM

# default bs4 parser
PARSER = "lxml"

ToElement = Callable[[str], IElement]

_driver_selenium = cast(WebDriver, None)
_playwright_page = cast(Page, None)


@pytest.fixture
def to_element(implementation: str) -> Callable[[str], IElement]:
    if implementation == BS4:
        return to_soup
    elif implementation == LXML:
        return to_lxml
    elif implementation == SELENIUM:
        return to_selenium
    elif implementation == PLAYWRIGHT:
        return to_playwright
    else:
        raise ValueError(f"Unknown implementation type: {implementation}")


def to_soup(html: str, parser: str = PARSER) -> IElement:
    return find_body_element(SoupElement(BeautifulSoup(html, parser)))


def to_lxml(html: str, parser: str = PARSER) -> IElement:
    root = fromstring(str(BeautifulSoup(html, parser)))
    return find_body_element(LXMLElement(root))


@pytest.fixture(scope="session", autouse=True)
def http_server(request):
    """Set up a simple HTTP server to serve the HTML file."""
    if request.config.getoption("--impl") != SELENIUM:
        yield
        return

    os.chdir(DIRECTORY)
    handler = SimpleHTTPRequestHandler
    httpd = HTTPServer(("localhost", PORT), handler)
    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True
    thread.start()
    yield


@pytest.fixture(scope="session", autouse=True)
def driver_selenium(request, http_server):
    """Set up a single Chrome driver used by selenium for the entire session."""
    if request.config.getoption("--impl") != SELENIUM:
        yield
        return

    global _driver_selenium

    _driver_selenium = get_driver()

    yield _driver_selenium

    _driver_selenium.quit()


# HTML file path
DIRECTORY = Path(os.getcwd(), "tests", "files")
FILE_NAME = "example.html"
PORT = 8000
URL = f"http://localhost:{PORT}/{FILE_NAME}"


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
    driver.get(URL)
    return driver


def insert(html: str, driver: WebDriver) -> None:
    driver.execute_script("document.body.innerHTML = arguments[0];", html)


def to_selenium(html: str) -> SeleniumElement:
    """Function to replace HTML content and get the root element."""
    insert(html, driver=_driver_selenium)
    body = _driver_selenium.find_element(By.TAG_NAME, "body")
    return SeleniumElement(body)


@pytest.fixture(scope="session")
def playwright_context():
    """Set up a Playwright browser context for the entire session."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


def initialize_playwright_page(playwright_context: Browser) -> Page:
    """Initializes a Playwright page."""
    global _playwright_page
    page = playwright_context.new_page()
    _playwright_page = page
    return page


@pytest.fixture(scope="session", autouse=True)
def playwright_page(request, playwright_context: Browser):
    """Set up a Playwright page for the entire session."""
    if request.config.getoption("--impl") != PLAYWRIGHT:
        yield
        return

    page = initialize_playwright_page(playwright_context)
    yield page
    page.close()


def to_playwright(html: str) -> PlaywrightElement:
    """Function to create a PlaywrightElement from HTML content."""
    _playwright_page.set_content(html)
    body = _playwright_page.query_selector("body")

    if body is None:
        raise ValueError("No body element found in the provided HTML.")

    return PlaywrightElement(body)


def strip(markup: str) -> str:
    """Converts raw string html to format matching str(BS) format."""
    return markup.replace("  ", "").replace("\n", "")


def find_body_element(bs: IElement) -> IElement:
    """Helper function to find body element in IElement object."""
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
    Find every instance of link element (with tag name 'a').
    """

    def find_all(
        self, tag: IElement, recursive: bool = True, limit=None
    ) -> list[IElement]:
        return tag.find_all("a", recursive=recursive, limit=limit)


class MockDivSelector(_MockSimpleComparable):
    """
    Mock selector class for testing purposes.
    Find every instance of div element (with tag name 'div').
    """

    def find_all(
        self, tag: IElement, recursive: bool = True, limit=None
    ) -> list[IElement]:
        return tag.find_all("div", recursive=recursive, limit=limit)


class MockSpanSelector(_MockSimpleComparable):
    """
    Mock selector class for testing purposes.
    Find every instance of span element (with tag name 'span').
    """

    def find_all(
        self, tag: IElement, recursive: bool = True, limit=None
    ) -> list[IElement]:
        return tag.find_all("span", recursive=recursive, limit=limit)


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
    """Mock operation that returns text of the element, using .text attribute."""

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


class MockModel(BaseModel):
    """Mock model class for testing purposes."""

    __scope__ = MockDivSelector()

    name = cast(str, MockLinkSelector() | MockTextOperation())
