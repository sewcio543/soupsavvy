from __future__ import annotations

import re
from itertools import islice
from typing import Iterable, Optional, Pattern, Union

from playwright.sync_api import ElementHandle

from soupsavvy.interfaces import IElement
from soupsavvy.selectors.css.api import PlaywrightCSSApi
from soupsavvy.selectors.xpath.api import PlaywrightXPathApi

_UID_REGEX = re.compile(r'\s*_uid="[^"]*"')

_FIND_ANCESTORS_SCRIPT = """
(element, limit) => {
  function findAncestors(el, lim) {
    const ancestors = [];
    let parent = el.parentElement;
    while (parent && parent.nodeType === 1) {
      ancestors.push(parent);
      if (lim && ancestors.length >= lim) break;
      parent = parent.parentElement;
    }
    return ancestors;
  }
  return findAncestors(element, limit);
}
"""

_FIND_ALL_SCRIPT = """
(element, args) => {
  const [tagName, attrs, recursive] = args;

  function matchesAttributes(element, attrs) {
    for (const [key, val] of Object.entries(attrs)) {
      const attrVal = element.getAttribute(key);
      if (attrVal === null) return false;

      if (typeof val === "string" && !attrVal.split(" ").includes(val)) {
        return false;
      }
    }
    return true;
  }

  function collectElements(element, recursive) {
    const matches = [];
    const elements = recursive ? element.querySelectorAll("*") : element.children;

    for (const el of elements) {
      if (
        (!tagName || el.tagName.toLowerCase() === tagName.toLowerCase()) &&
        matchesAttributes(el, attrs)
      ) {
        matches.push(el);
      }
    }

    return matches;
  }

  return collectElements(element, recursive);
}
"""


class PlaywrightElement(IElement):
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

        # playwright does not guarantee the same identity for hadles
        # from different queries, it needs to be worked around
        self._id = self.node.evaluate(
            """
            el => {
                if (!el._uid) {
                    el._uid = Math.random().toString(36).substr(2, 9);
                }
                return el._uid;
            }
            """
        )

    def find_all(
        self,
        name: Optional[str] = None,
        attrs: Optional[dict[str, Union[str, Pattern[str]]]] = None,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[PlaywrightElement]:
        attrs = attrs or {}
        js_attrs = {k: None if isinstance(v, Pattern) else v for k, v in attrs.items()}

        found = self.node.evaluate_handle(
            _FIND_ALL_SCRIPT,
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

    def find_subsequent_siblings(
        self, limit: Optional[int] = None
    ) -> list[PlaywrightElement]:
        iterator = self.node.query_selector_all("xpath=following-sibling::*")
        return list(islice(self._map(iterator), limit))

    @property
    def node(self) -> ElementHandle:
        return self._node

    def get(self) -> ElementHandle:
        return self.node

    def find_ancestors(self, limit: Optional[int] = None) -> list[PlaywrightElement]:
        js_handle = self.node.evaluate_handle(
            _FIND_ANCESTORS_SCRIPT,
            limit,
        )
        ancestors = [
            prop.as_element()
            for prop in js_handle.get_properties().values()
            if prop.as_element() is not None
        ]
        return list(self._map(ancestors))

    @property
    def children(self) -> Iterable[PlaywrightElement]:
        iterator = self.node.query_selector_all("xpath=./*")
        return self._map(iterator)

    @property
    def descendants(self) -> Iterable[PlaywrightElement]:
        iterator = self.node.query_selector_all("*")
        return self._map(iterator)

    @property
    def parent(self) -> Optional[PlaywrightElement]:
        handle = self.node.evaluate_handle("el => el.parentElement")
        element = handle.as_element()

        if element is None:
            return None

        return PlaywrightElement(element)

    def get_attribute(self, name: str) -> Optional[str]:
        return self.node.get_attribute(name)

    @property
    def name(self) -> str:
        return self.node.evaluate("el => el.tagName").lower()

    def __str__(self) -> str:
        html = self.node.evaluate("el => el.outerHTML")
        return _UID_REGEX.sub("", html)

    @property
    def text(self) -> str:
        return self.node.text_content() or ""

    def css(self, selector: str):
        return PlaywrightCSSApi(selector)

    def xpath(self, selector: str):
        return PlaywrightXPathApi(selector)

    def __hash__(self) -> int:
        return hash(self._id)
