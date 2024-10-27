from __future__ import annotations

import warnings
from typing import Any

import soupsavvy.exceptions as exc
from soupsavvy.interfaces import IElement, SelectionApi


class LXMLXpathApi(SelectionApi):
    """Interface for `lxml` xpath API for html elements."""

    def __init__(self, selector: Any) -> None:
        from lxml.etree import XPath, XPathSyntaxError

        if not isinstance(selector, XPath):
            try:
                selector = XPath(selector)
            except XPathSyntaxError as e:
                raise exc.InvalidXPathSelector(
                    f"Parsing XPath '{selector}' failed"
                ) from e

        super().__init__(selector)

    def select(self, element: IElement) -> list[IElement]:
        from lxml.etree import _Element as HtmlElement

        selected = self.selector(element.node)

        if not isinstance(selected, list) or (
            selected and all(not isinstance(match, HtmlElement) for match in selected)
        ):
            warnings.warn(
                "XPath expression does not target elements, "
                f"no results will be found: {selected}",
                UserWarning,
            )
            return []

        return [element.from_node(node) for node in selected]


class SeleniumXPathApi(SelectionApi):
    """Interface for `selenium` xpath API for web elements."""

    def select(self, element: IElement) -> list[IElement]:
        from selenium.common.exceptions import InvalidSelectorException
        from selenium.webdriver.common.by import By

        try:
            found = element.node.find_elements(By.XPATH, self.selector)
        except InvalidSelectorException as e:
            raise exc.InvalidXPathSelector(
                f"CSS selector constructed from provided parameters "
                f"is not valid: {self.selector}"
            ) from e

        return [element.from_node(node) for node in found]
