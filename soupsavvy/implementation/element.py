import importlib
from typing import Any

from soupsavvy.interfaces import IElement


def to_soupsavvy(element: Any) -> IElement:
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
