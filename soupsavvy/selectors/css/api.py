from __future__ import annotations

from typing import TYPE_CHECKING

import soupsavvy.exceptions as exc
from soupsavvy.interfaces import Element, SelectionApi

if TYPE_CHECKING:
    from soupsavvy.implementation.bs4 import SoupElement
    from soupsavvy.implementation.selenium import SeleniumElement


class SoupsieveApi(SelectionApi):
    """Interface for `soupsieve` css API for soup."""

    def __init__(self, selector) -> None:
        import soupsieve as sv

        try:
            compiled = sv.compile(selector)
        except sv.SelectorSyntaxError:
            raise exc.InvalidCSSSelector(
                "CSS selector constructed from provided parameters "
                f"is not valid: {selector}"
            )
        super().__init__(compiled)

    def select(self, element: SoupElement) -> list[SoupElement]:
        return [element.from_node(node) for node in self.selector.select(element.node)]


class CSSSelectApi(SelectionApi):
    """Interface for `cssselect` css API for lxml."""

    def __init__(self, selector) -> None:
        from cssselect.parser import SelectorError
        from lxml.cssselect import CSSSelector

        try:
            compiled = CSSSelector(selector)
        except SelectorError as e:
            raise exc.InvalidCSSSelector(
                "CSS selector constructed from provided parameters "
                f"is not valid: {selector}"
            ) from e

        super().__init__(compiled)

    def select(self, element: Element) -> list[Element]:
        return [element.from_node(node) for node in self.selector(element.node)]


class SeleniumCSSApi(SelectionApi):
    """Interface for `selenium` css API for web elements."""

    def select(self, element: SeleniumElement) -> list[SeleniumElement]:
        from selenium.common.exceptions import InvalidSelectorException
        from selenium.webdriver.common.by import By

        try:
            found = element.node.find_elements(By.CSS_SELECTOR, self.selector)
        except InvalidSelectorException as e:
            raise exc.InvalidCSSSelector(
                f"CSS selector constructed from provided parameters "
                f"is not valid: {self.selector}"
            ) from e

        return [element.from_node(node) for node in found]
