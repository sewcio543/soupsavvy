"""
Module with functionality to convert user-provided objects to `soupsavvy`
compatible elements.
"""

import importlib
from typing import Any

from soupsavvy.interfaces import IElement


def to_soupsavvy(element: Any) -> IElement:
    """
    Converts a given element to a `soupsavvy` compatible componment.

    Type of the input element it detected by the function and wraped it in a
    corresponding `soupsavvy` element implementation. It supports the following
    element types:

    - `BeautifulSoup` Tag
    - `lxml` HtmlElement
    - `Selenium` WebElement

    If the element is already a `soupsavvy` Element, it is returned as is.

    Parameters
    ----------
    element : Any
        The element to be converted to a `soupsavvy` element.
        Must be one of the supported element types.

    Returns
    -------
    IElement
        A `soupsavvy` element corresponding to the input element. The returned
        element will be compatible with the `soupsavvy` selector system.

    Raises
    ------
    TypeError
        If the provided element type is not supported.

    Example
    -------
    >>> from bs4 import BeautifulSoup
    ... from soupsavvy import to_soupsavvy
    ... soup = BeautifulSoup("<div>Example</div>", "html.parser")
    ... element = to_soupsavvy(soup)
    """
    if isinstance(element, IElement):
        return element

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

    # Check the type of the element
    if Tag and isinstance(element, Tag):
        from soupsavvy.implementation.bs4 import SoupElement

        return SoupElement(element)
    elif HtmlElement and isinstance(element, HtmlElement):
        from soupsavvy.implementation.lxml import LXMLElement

        return LXMLElement(element)
    elif WebElement and isinstance(element, WebElement):
        from soupsavvy.implementation.selenium import SeleniumElement

        return SeleniumElement(element)
    else:
        raise TypeError("Unsupported element type")
