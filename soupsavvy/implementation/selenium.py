from __future__ import annotations

from typing import Iterable, Optional, Pattern, Union

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from soupsavvy.interfaces import IElement
from soupsavvy.selectors.css.api import SeleniumCSSApi
from soupsavvy.selectors.xpath.api import SeleniumXPathApi


class SeleniumElement(IElement):
    def __init__(self, node: WebElement) -> None:
        self._node = node

    @property
    def node(self) -> WebElement:
        return self._node

    @classmethod
    def from_node(cls, node: WebElement) -> SeleniumElement:
        return SeleniumElement(node)

    def find_all(
        self,
        name: Optional[str] = None,
        attrs: Optional[dict[str, Union[str, Pattern[str]]]] = None,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[SeleniumElement]:
        """Find all elements matching tag name and attributes with support for exact and regex matching."""

        def matches(element: WebElement) -> bool:
            """Checks if an element matches given attributes with exact or regex matching."""
            if name is not None and name != element.tag_name:
                return False

            if attrs is None:
                return True

            for attr, value in attrs.items():
                actual = self._get_attribute_list(attr, element=element)

                if actual[0] is None:
                    return False

                if isinstance(value, Pattern):
                    if not value.search(" ".join(actual)):
                        return False
                else:
                    if value not in actual:
                        return False
            return True

        # Filter elements based on attributes match and limit if specified
        iterator = self.descendants if recursive else self.children
        matched_elements = [
            SeleniumElement(e._node) for e in iterator if matches(e._node)
        ]
        return matched_elements[:limit] if limit else matched_elements

    def find_next_siblings(self, limit: Optional[int] = None) -> list[SeleniumElement]:
        sibling_elements = self._node.find_elements(By.XPATH, "following-sibling::*")

        if limit is not None:
            sibling_elements = sibling_elements[:limit]

        return [SeleniumElement(e) for e in sibling_elements]

    def find_ancestors(self, limit: Optional[int] = None) -> list[SeleniumElement]:
        parents = []
        driver: WebDriver = self._node.parent
        current_element = self._node

        while True:
            current_element = driver.execute_script(
                "return arguments[0].parentNode;", current_element
            )

            if current_element is None:
                # skip root element
                parents = parents[:-1]
                break

            parents.append(SeleniumElement(current_element))

            if limit and len(parents) >= limit:
                break

        return parents

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
        return SeleniumElement(element)

    def get_text(self, separator: str = "", strip: bool = False) -> str:
        text = self._node.text

        if strip:
            text = text.strip()

        return text.replace("\n", separator)

    def _get_attribute_list(self, name: str, element: WebElement) -> list:
        value = element.get_dom_attribute(name)

        if value is None:
            return [value]
        elif value == "":
            return [value]

        return value.split()

    def get_attribute_list(self, name: str) -> list[str]:
        return self._get_attribute_list(name, element=self._node)

    def prettify(self) -> str:
        return self._node.get_attribute("outerHTML") or ""

    @property
    def name(self) -> str:
        return self._node.tag_name

    # def to_lxml(self) -> HtmlElement:
    #     raise NotImplementedError("Conversion to lxml is not supported with Selenium.")

    def __hash__(self) -> int:
        return hash(self._node)

    def __str__(self) -> str:
        return self._node.get_attribute("outerHTML") or ""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({str(self)})"

    @property
    def text(self) -> str:
        if self.children:
            return ""

        return self._node.text

    def css(self, selector: str) -> SeleniumCSSApi:
        return SeleniumCSSApi(selector)

    def xpath(self, selector: str) -> SeleniumXPathApi:
        return SeleniumXPathApi(selector)
