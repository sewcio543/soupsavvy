from __future__ import annotations

from itertools import islice
from typing import Iterable, Optional, Pattern, Union

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

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

        return list(
            islice(map(SeleniumElement, filter(match, matched_elements)), limit)
        )

    def find_subsequent_siblings(
        self, limit: Optional[int] = None
    ) -> list[SeleniumElement]:
        sibling_elements = self._node.find_elements(By.XPATH, "following-sibling::*")

        if limit is not None:
            sibling_elements = sibling_elements[:limit]

        return [SeleniumElement(e) for e in sibling_elements]

    def find_ancestors(self, limit: Optional[int] = None) -> list[SeleniumElement]:
        driver: WebDriver = self._node.parent
        matched_elements = driver.execute_script(
            _FIND_ANCESTORS_SCRIPT,
            self._node,
            limit,
        )
        return [SeleniumElement(el) for el in matched_elements]

    @property
    def children(self) -> Iterable[SeleniumElement]:
        return [SeleniumElement(e) for e in self._node.find_elements(By.XPATH, "./*")]

    @property
    def descendants(self) -> Iterable[SeleniumElement]:
        return [
            SeleniumElement(e) for e in self._node.find_elements(By.CSS_SELECTOR, "*")
        ]

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
