"""
Module with `selenium` implementation of `IElement`.
`SeleniumElement` class is an adapter making `selenium` tree,
compatible with `IElement` interface and usable across the library.
"""

from __future__ import annotations

from itertools import islice
from pathlib import Path
from typing import Iterable, Optional, Pattern, Union

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from soupsavvy.interfaces import IElement
from soupsavvy.selectors.css.api import SeleniumCSSApi
from soupsavvy.selectors.xpath.api import SeleniumXPathApi

_SCRIPTS_DIR = Path(
    "soupsavvy",
    "implementation",
    "scripts",
)
_FIND_ALL_SCRIPT = Path(_SCRIPTS_DIR, "find_all.js").read_text()
_FIND_ANCESTORS_SCRIPT = Path(_SCRIPTS_DIR, "find_ancestors.js").read_text()


class SeleniumElement(IElement):
    """
    Implementation of `IElement` for `selenium` tree.
    Adapter for `selenium` objects, that makes them usable across the library.

    Example
    -------
    >>> from soupsavvy.implementation.selenium import SeleniumElement
    ... from selenium.webdriver.common.by import By
    ... node = driver.find_element(By.TAG_NAME, "div")
    ... element = SeleniumElement(node)
    """

    _NODE_TYPE = WebElement

    def find_all(
        self,
        name: Optional[str] = None,
        attrs: Optional[dict[str, Union[str, Pattern[str]]]] = None,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[SeleniumElement]:
        attrs = attrs or {}
        js_attrs = {k: None if isinstance(v, Pattern) else v for k, v in attrs.items()}

        driver: WebDriver = self.node.parent
        matched_elements: list[WebElement] = driver.execute_script(
            _FIND_ALL_SCRIPT,
            self._node,
            name,
            js_attrs,
            recursive,
        )

        def match(element: WebElement) -> bool:
            return all(
                value.search(element.get_attribute(attr) or "")
                for attr, value in attrs.items()
                if isinstance(value, Pattern)
            )

        return list(islice(self._map(filter(match, matched_elements)), limit))

    def find_subsequent_siblings(
        self, limit: Optional[int] = None
    ) -> list[SeleniumElement]:
        iterator = self._node.find_elements(By.XPATH, "following-sibling::*")
        return list(islice(self._map(iterator), limit))

    def find_ancestors(self, limit: Optional[int] = None) -> list[SeleniumElement]:
        driver: WebDriver = self._node.parent
        iterator = driver.execute_script(
            _FIND_ANCESTORS_SCRIPT,
            self._node,
            limit,
        )
        return list(self._map(iterator))

    @property
    def children(self) -> Iterable[SeleniumElement]:
        iterator = self._node.find_elements(By.XPATH, "./*")
        return self._map(iterator)

    @property
    def descendants(self) -> Iterable[SeleniumElement]:
        iterator = self._node.find_elements(By.CSS_SELECTOR, "*")
        return self._map(iterator)

    @property
    def parent(self) -> Optional[SeleniumElement]:
        driver: WebDriver = self._node.parent
        element = driver.execute_script("return arguments[0].parentNode;", self.node)
        return SeleniumElement(element) if element is not None else None

    def get_attribute(self, name: str) -> Optional[str]:
        return self.node.get_dom_attribute(name)

    @property
    def name(self) -> str:
        return self._node.tag_name

    def __str__(self) -> str:
        return self._node.get_attribute("outerHTML") or ""

    @property
    def text(self) -> str:
        return self._node.text

    def css(self, selector: str) -> SeleniumCSSApi:
        return SeleniumCSSApi(selector)

    def xpath(self, selector: str) -> SeleniumXPathApi:
        return SeleniumXPathApi(selector)
