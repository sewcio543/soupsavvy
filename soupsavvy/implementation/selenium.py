"""
Module with `selenium` implementation of `IElement`.
`SeleniumElement` class is an adapter making `selenium` tree,
compatible with `IElement` interface and usable across the library.
"""

from __future__ import annotations

from itertools import islice
from typing import Iterable, Optional, Pattern, Union

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from typing_extensions import Self

from soupsavvy.interfaces import IElement
from soupsavvy.selectors.css.api import SeleniumCSSApi
from soupsavvy.selectors.xpath.api import SeleniumXPathApi

# js scripts
# ----------

_FIND_ALL_SCRIPT = """
function findMatchingElements(root, tagName, attrs, recursive) {
  function matchesAttributes(element, attrs) {
    for (let [key, val] of Object.entries(attrs)) {
      let attrVal = element.getAttribute(key);

      if (attrVal === null) {
        return false;
      }

      if (typeof val === "string" && !attrVal.split(" ").includes(val)) {
        return false;
      }
    }
    return true;
  }

  function collectElements(element, recursive) {
    let matches = [];
    let elements = recursive ? element.querySelectorAll("*") : element.children;

    for (let el of elements) {
      if (
        (!tagName || el.tagName.toLowerCase() === tagName.toLowerCase()) &&
        matchesAttributes(el, attrs)
      ) {
        matches.push(el);
      }
    }
    return matches;
  }
  return collectElements(root, recursive);
}

return findMatchingElements(
  arguments[0],
  arguments[1],
  arguments[2],
  arguments[3]
);
"""

_FIND_ANCESTORS_SCRIPT = """
function findAncestors(element, limit) {
  let ancestors = [];
  let parent = element.parentNode;
  while (parent && parent.nodeType === 1) {
    ancestors.push(parent);
    if (limit && ancestors.length >= limit) break;
    parent = parent.parentNode;
  }
  return ancestors;
}
return findAncestors(arguments[0], arguments[1]);
"""


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
    ) -> list[Self]:
        attrs = attrs or {}
        js_attrs = {k: None if isinstance(v, Pattern) else v for k, v in attrs.items()}

        driver: WebDriver = self.node.parent
        matched_elements: list[WebElement] = driver.execute_script(
            _FIND_ALL_SCRIPT,
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
        iterator = self.node.find_elements(By.XPATH, "following-sibling::*")
        return list(islice(self._map(iterator), limit))

    def find_ancestors(self, limit: Optional[int] = None) -> list[Self]:
        driver: WebDriver = self.node.parent
        iterator = driver.execute_script(
            _FIND_ANCESTORS_SCRIPT,
            self.node,
            limit,
        )
        return list(self._map(iterator))

    @property
    def children(self) -> Iterable[Self]:
        iterator = self.node.find_elements(By.XPATH, "./*")
        return self._map(iterator)

    @property
    def descendants(self) -> Iterable[Self]:
        iterator = self.node.find_elements(By.CSS_SELECTOR, "*")
        return self._map(iterator)

    @property
    def parent(self) -> Optional[Self]:
        driver: WebDriver = self.node.parent
        element = driver.execute_script("return arguments[0].parentNode;", self.node)
        return self.from_node(element) if element is not None else None

    def get_attribute(self, name: str) -> Optional[str]:
        return self.node.get_dom_attribute(name)

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

    @property
    def node(self) -> WebElement:
        return self._node

    def get(self) -> WebElement:
        return self.node
