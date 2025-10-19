from __future__ import annotations

import re
from itertools import islice
from typing import Iterable, Optional, Pattern, Union

from playwright.sync_api import ElementHandle, Page
from typing_extensions import Self

import soupsavvy.exceptions as exc
import soupsavvy.implementation.snippets.js.playwright as js
from soupsavvy.implementation.snippets import css, xpath
from soupsavvy.interfaces import IBrowser, IElement
from soupsavvy.selectors.css.api import PlaywrightCSSApi
from soupsavvy.selectors.xpath.api import PlaywrightXPathApi

_UID_REGEX = re.compile(r'\s*_uid="[^"]*"')


class PlaywrightElement(IElement[ElementHandle]):
    """
    Implementation of `IElement` for `playwright` tree.
    Adapter for `playwright` handles, that makes them usable across the library.

    Example
    -------
    >>> from soupsavvy.implementation.playwright import PlaywrightElement
    >>> from playwright.sync_api import sync_playwright
    >>> with sync_playwright() as p:
    ...     browser = p.chromium.launch()
    ...     page = browser.new_page()
    ...     page.goto("https://example.com")
    ...     element = page.query_selector("h1")
    ...     playwright_element = PlaywrightElement(element)
    """

    _NODE_TYPE = ElementHandle

    def __init__(self, node: ElementHandle, *args, **kwargs):
        super().__init__(node, *args, **kwargs)

        # playwright does not guarantee the same identity for handles
        # from different queries, it needs to be worked around
        self._id = self.node.evaluate(js.ADD_IDENTIFIER_SCRIPT)

    def find_all(
        self,
        name: Optional[str] = None,
        attrs: Optional[dict[str, Union[str, Pattern[str]]]] = None,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Self]:
        attrs = attrs or {}
        js_attrs = {k: None if isinstance(v, Pattern) else v for k, v in attrs.items()}

        found = self.node.evaluate_handle(
            js.FILTER_NODES_SCRIPT,
            [name, js_attrs, recursive],
        )
        matched_elements = [
            e.as_element()
            for e in found.get_properties().values()
            if e.as_element() is not None
        ]

        def match(element: ElementHandle) -> bool:
            return all(
                value.search(element.get_attribute(attr) or "")
                for attr, value in attrs.items()
                if isinstance(value, Pattern)
            )

        return list(islice(self._map(filter(match, matched_elements)), limit))

    def find_subsequent_siblings(self, limit: Optional[int] = None) -> list[Self]:
        iterator = self.node.query_selector_all(
            f"xpath={xpath.FIND_SUBSEQUENT_SIBLINGS_SELECTOR}"
        )
        return list(islice(self._map(iterator), limit))

    def find_ancestors(self, limit: Optional[int] = None) -> list[Self]:
        js_handle = self.node.evaluate_handle(
            js.FIND_ANCESTORS_SCRIPT,
            limit,
        )
        ancestors = [
            prop.as_element()
            for prop in js_handle.get_properties().values()
            if prop.as_element() is not None
        ]
        return list(self._map(ancestors))

    @property
    def children(self) -> Iterable[Self]:
        iterator = self.node.query_selector_all(
            f"xpath={xpath.FIND_ALL_CHILDREN_SELECTOR}"
        )
        return self._map(iterator)

    @property
    def descendants(self) -> Iterable[Self]:
        iterator = self.node.query_selector_all(css.FIND_ALL_DESCENDANTS_SELECTOR)
        return self._map(iterator)

    @property
    def parent(self) -> Optional[Self]:
        handle = self.node.evaluate_handle(js.PARENT_ELEMENT_SCRIPT)
        element = handle.as_element()

        if element is None:
            return None

        return self.from_node(element)

    def get_attribute(self, name: str) -> Optional[str]:
        # get live JS property first, then html attribute
        property_ = self.node.evaluate(js.GET_ATTRIBUTE_SCRIPT, name)

        if property_ is not None:
            return property_

        return self.node.get_attribute(name)

    @property
    def name(self) -> str:
        return self.node.evaluate(js.TAG_NAME_SCRIPT).lower()

    def __str__(self) -> str:
        html = self.node.evaluate(js.OUTER_HTML_SCRIPT)
        return _UID_REGEX.sub("", html)

    @property
    def text(self) -> str:
        return self.node.text_content() or ""

    def css(self, selector: str):
        return PlaywrightCSSApi(selector)

    def xpath(self, selector: str):
        return PlaywrightXPathApi(selector)

    def __hash__(self) -> int:
        return hash((self._id, self.__class__))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self._id == other._id


class PlaywrightBrowser(IBrowser[Page, PlaywrightElement]):
    """
    Implementation of `IBrowser` for `playwright` Page.
    Adapter for Playwright's `Page` object, allowing unified use across soupsavvy.

    Example
    -------
    >>> from playwright.sync_api import sync_playwright
    >>> from soupsavvy.implementation.playwright import PlaywrightBrowser
    ...
    >>> with sync_playwright() as p:
    ...     browser = p.chromium.launch()
    ...     page = browser.new_page()
    ...     pw_browser = PlaywrightBrowser(page)
    ...     pw_browser.navigate("https://example.com")
    """

    def navigate(self, url: str) -> None:
        self.browser.goto(url)

    def click(self, element: PlaywrightElement) -> None:
        self.browser.evaluate(js.CLICK_ELEMENT_SCRIPT, element.node)

    def send_keys(
        self, element: PlaywrightElement, value: str, clear: bool = True
    ) -> None:
        if clear:
            element.node.fill("")

        element.node.type(value)

    def get_document(self) -> PlaywrightElement:
        element = self.browser.query_selector("html")

        if element is None:
            raise exc.TagNotFoundException("Could not find <html> element on the page.")

        return PlaywrightElement(element)

    def close(self) -> None:
        self.browser.close()

    def get_current_url(self) -> str:
        return self.browser.url
