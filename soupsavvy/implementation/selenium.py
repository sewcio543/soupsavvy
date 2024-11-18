from __future__ import annotations

import re
from typing import Iterable, Optional, Pattern, Union

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from soupsavvy.interfaces import IElement
from soupsavvy.selectors.css.api import SeleniumCSSApi
from soupsavvy.selectors.xpath.api import SeleniumXPathApi


class SeleniumElement(IElement):
    _NODE_TYPE = WebElement

    # def find_all(
    #     self,
    #     name: Optional[str] = None,
    #     attrs: Optional[dict[str, Union[str, Pattern[str]]]] = None,
    #     recursive: bool = True,
    #     limit: Optional[int] = None,
    # ) -> list[SeleniumElement]:
    #     """Find all elements matching tag name and attributes with support for exact and regex matching."""

    #     def matches(element: WebElement) -> bool:
    #         """Checks if an element matches given attributes with exact or regex matching."""
    #         if name is not None and name != element.tag_name:
    #             return False

    #         if attrs is None:
    #             return True

    #         for attr, value in attrs.items():
    #             actual = element.get_dom_attribute(attr)

    #             if actual is None:
    #                 return False

    #             if isinstance(value, Pattern):
    #                 if not value.search(actual):  #
    #                     return False  #
    #             else:
    #                 if value not in actual.split():
    #                     return False  #
    #         return True

    #     # Filter elements based on attributes match and limit if specified
    #     iterator = self.descendants if recursive else self.children
    #     matched_elements = [
    #         SeleniumElement(e._node) for e in iterator if matches(e._node)
    #     ]
    #     return matched_elements[:limit] if limit else matched_elements

    def find_all(
        self,
        name: Optional[str] = None,
        attrs: Optional[dict[str, Union[str, Pattern[str]]]] = None,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[IElement]:
        """Optimized method to find all elements matching tag name and attributes."""
        js_script = """
            function findMatchingElements(root, tagName, attrs, recursive, limit) {
                function matchesAttributes(element, attrs) {
                    for (let [key, val] of Object.entries(attrs)) {
                        if (val === null) {
                            if (!element.hasAttribute(key)) {
                                return false;
                            }
                        } else {
                            let attrVal = element.getAttribute(key);
                            if (attrVal === null) {
                                return false;
                            }
                            let attrValues = attrVal.split(" ");
                            if (typeof val === 'string' && !attrValues.includes(val)) {
                                return false;
                            }
                            if (val instanceof RegExp && !attrValues.some(v => val.test(v))) {
                                return false;
                            }
                        }
                    }
                    return true;
                }

                function collectElements(element, recursive) {
                    let matches = [];
                    let elements = recursive ? element.getElementsByTagName(tagName || "*")
                                            : element.children;

                    for (let el of elements) {
                        if ((!tagName || el.tagName.toLowerCase() === tagName.toLowerCase()) &&
                            matchesAttributes(el, attrs)) {
                            matches.push(el);
                        }
                    }
                    return matches;
                }
                return collectElements(root, recursive);
            }

            return findMatchingElements(arguments[0], arguments[1], arguments[2], arguments[3], arguments[4]);
        """

        # Convert regex patterns to strings for JS; later process matches in Python if regex was specified
        js_attrs = {
            k: None if isinstance(v, Pattern) else v for k, v in (attrs or {}).items()
        }

        matched_elements: list[WebElement] = self._node.parent.execute_script(
            js_script, self._node, name, js_attrs, recursive, limit
        )

        # Filter regex attributes that JS could not process
        final_elements: list[IElement] = []

        for element in matched_elements:
            if all(
                (
                    value.search(
                        element.get_attribute(attr) or ""
                    )  # check if ti makes sense
                    if isinstance(value, Pattern)
                    else True
                )
                for attr, value in (attrs or {}).items()
            ):
                final_elements.append(SeleniumElement(element))

        return final_elements[:limit]

    def find_subsequent_siblings(self, limit: Optional[int] = None) -> list[IElement]:
        sibling_elements = self._node.find_elements(By.XPATH, "following-sibling::*")

        if limit is not None:
            sibling_elements = sibling_elements[:limit]

        return [SeleniumElement(e) for e in sibling_elements]

    # def find_ancestors(self, limit: Optional[int] = None) -> list[SeleniumElement]:
    #     parents = []
    #     driver: WebDriver = self._node.parent
    #     current_element = self._node

    #     while True:
    #         current_element = driver.execute_script(
    #             "return arguments[0].parentNode;", current_element
    #         )

    #         if current_element is None:
    #             # skip root element
    #             parents = parents[:-1]
    #             break

    #         parents.append(SeleniumElement(current_element))

    #         if limit and len(parents) >= limit:
    #             break

    #     return parents

    def find_ancestors(self, limit: Optional[int] = None) -> list[IElement]:
        driver: WebDriver = self._node.parent

        # JavaScript function to collect ancestors up to a limit
        js_script = """
            function findAncestors(element, limit) {
                let ancestors = [];
                let parent = element.parentNode;
                while (parent && parent.nodeType === 1) { // Element node
                    ancestors.push(parent);
                    if (limit && ancestors.length >= limit) break;
                    parent = parent.parentNode;
                }
                return ancestors;
            }
            return findAncestors(arguments[0], arguments[1]);
        """

        # Execute the JavaScript and get all ancestors at once
        matched_elements = driver.execute_script(js_script, self._node, limit)
        # Wrap matched elements in SeleniumElement instances
        return [SeleniumElement(el) for el in matched_elements]

    @property
    def children(self) -> Iterable[IElement]:
        return [SeleniumElement(e) for e in self._node.find_elements(By.XPATH, "./*")]

    @property
    def descendants(self) -> Iterable[IElement]:
        return [
            SeleniumElement(e) for e in self._node.find_elements(By.CSS_SELECTOR, "*")
        ]

    @property
    def parent(self) -> Optional[IElement]:
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
