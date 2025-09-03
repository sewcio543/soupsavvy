"""
Module with a converter, to transform any supported node into
an appropriate IElement instance.
This enables node to be used across `soupsavvy` with all its features.
"""

import importlib
from typing import Any

from soupsavvy.interfaces import IElement

SUPPORTED = ["bs4", "lxml", "selenium", "playwright"]


def to_soupsavvy(node: Any) -> IElement:
    """
    Converts node of supported type into an appropriate IElement instance
    making it usable across `soupsavvy` with all its features.

    Parameters
    ----------
    node : Any
        A node object of supported type, currently supported implementations are:
        "beautifulsoup4", "lxml", "selenium" and "playwright".

    Returns
    -------
    IElement
        An instance of IElement, wrapping the node object.

    Examples
    --------
    >>> from bs4 import BeautifulSoup
    ... from soupsavvy import to_soupsavvy
    ... soup = BeautifulSoup("<p>Hello, World!</p>", "html.parser")
    ... element = to_soupsavvy(soup)

    Raises
    ------
    TypeError
        If the node object is of an unsupported type.

    Notes
    -----
    If `IElement` is passed as an argument, it will be returned back.
    """
    if isinstance(node, IElement):
        return node

    try:
        bs4 = importlib.import_module("bs4")
        Tag = bs4.Tag
    except ImportError:
        Tag = None

    try:
        lxml = importlib.import_module("lxml.etree")
        HtmlElement = lxml._Element
    except ImportError:
        HtmlElement = None

    try:
        selenium = importlib.import_module("selenium.webdriver.remote.webelement")
        WebElement = selenium.WebElement
    except ImportError:
        WebElement = None

    try:
        playwright = importlib.import_module("playwright.sync_api")
        ElementHandle = playwright.ElementHandle
    except ImportError:
        ElementHandle = None

    # Check the type of the element
    if Tag and isinstance(node, Tag):
        from soupsavvy.implementation.bs4 import SoupElement

        return SoupElement(node)

    if HtmlElement and isinstance(node, HtmlElement):
        from soupsavvy.implementation.lxml import LXMLElement

        return LXMLElement(node)

    if WebElement and isinstance(node, WebElement):
        from soupsavvy.implementation.selenium import SeleniumElement

        return SeleniumElement(node)

    if ElementHandle and isinstance(node, ElementHandle):
        from soupsavvy.implementation.playwright import PlaywrightElement

        return PlaywrightElement(node)

    raise TypeError(f"Unsupported element type, expected one of {SUPPORTED}")
