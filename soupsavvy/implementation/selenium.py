"""
Module with `selenium` implementations compatible with soupsavvy interfaces.
- `SeleniumElement` class is an adapter making `selenium` tree,
compatible with `IElement` interface and usable across the library.
- `SeleniumBrowser` class is an adapter making `selenium` WebDriver
compatible with `IBrowser`.
"""

from __future__ import annotations

from itertools import islice
from typing import Iterable, Optional, Pattern, Union

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from typing_extensions import Self

import soupsavvy.exceptions as exc
import soupsavvy.implementation.snippets.js.selenium as js
from soupsavvy.implementation.snippets import css, xpath
from soupsavvy.interfaces import IBrowser, IElement
from soupsavvy.selectors.css.api import SeleniumCSSApi
from soupsavvy.selectors.xpath.api import SeleniumXPathApi


class SeleniumElement(IElement[WebElement]):
    """
    Implementation of `IElement` for `selenium` tree.
    Adapter for `selenium` objects, that makes them usable across the library.

    Example
    -------
    >>> from soupsavvy.implementation.selenium import SeleniumElement
    ... from selenium.ISeleniumDriver.common.by import By
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
    ) -> list[Self]:
        attrs = attrs or {}
        js_attrs = {k: None if isinstance(v, Pattern) else v for k, v in attrs.items()}

        driver: WebDriver = self.node.parent
        matched_elements: list[WebElement] = driver.execute_script(
            js.FILTER_NODES_SCRIPT,
            self.node,
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

    def find_subsequent_siblings(self, limit: Optional[int] = None) -> list[Self]:
        iterator = self.node.find_elements(
            By.XPATH, xpath.FIND_SUBSEQUENT_SIBLINGS_SELECTOR
        )
        return list(islice(self._map(iterator), limit))

    def find_ancestors(self, limit: Optional[int] = None) -> list[Self]:
        driver: WebDriver = self.node.parent
        iterator = driver.execute_script(
            js.FIND_ANCESTORS_SCRIPT,
            self.node,
            limit,
        )
        return list(self._map(iterator))

    @property
    def children(self) -> Iterable[Self]:
        iterator = self.node.find_elements(By.XPATH, xpath.FIND_ALL_CHILDREN_SELECTOR)
        return self._map(iterator)

    @property
    def descendants(self) -> Iterable[Self]:
        iterator = self.node.find_elements(
            By.CSS_SELECTOR, css.FIND_ALL_DESCENDANTS_SELECTOR
        )
        return self._map(iterator)

    @property
    def parent(self) -> Optional[Self]:
        driver: WebDriver = self.node.parent
        element = driver.execute_script(js.FIND_PARENT_NODE_SCRIPT, self.node)
        return self.from_node(element) if element is not None else None

    def get_attribute(self, name: str) -> Optional[str]:
        return self.node.get_attribute(name)

    @property
    def name(self) -> str:
        return self.node.tag_name

    def __str__(self) -> str:
        return self.node.get_attribute("outerHTML") or ""

    @property
    def text(self) -> str:
        return self.node.text

    def css(self, selector: str) -> SeleniumCSSApi:
        return SeleniumCSSApi(selector)

    def xpath(self, selector: str) -> SeleniumXPathApi:
        return SeleniumXPathApi(selector)


class SeleniumBrowser(IBrowser[WebDriver, SeleniumElement]):
    """
    Implementation of `IBrowser` for `selenium` WebDriver.
    Adapter for `selenium` WebDriver, that makes them usable across the library.

    Example
    -------
    >>> from soupsavvy.implementation.selenium import SeleniumBrowser
    ... from selenium import webdriver
    ... driver = webdriver.Chrome()
    ... browser = SeleniumBrowser(driver)
    """

    def navigate(self, url: str) -> None:
        self.browser.get(url)

    def click(self, element: SeleniumElement) -> None:
        self.browser.execute_script(js.CLICK_ELEMENT_SCRIPT, element.node)

    def send_keys(
        self, element: SeleniumElement, value: str, clear: bool = True
    ) -> None:
        if clear:
            element.node.clear()

        element.node.send_keys(value)

    def get_document(self) -> SeleniumElement:
        elements = self.browser.find_elements(by=By.TAG_NAME, value="html")

        if not elements:
            raise exc.TagNotFoundException("Could not find <html> element on the page.")

        return SeleniumElement(elements[0])

    def close(self) -> None:
        self.browser.quit()

    def get_current_url(self) -> str:
        return self.browser.current_url
