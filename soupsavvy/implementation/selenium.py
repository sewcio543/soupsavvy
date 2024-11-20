from __future__ import annotations

from importlib.resources import files
from itertools import islice
from typing import Iterable, Optional, Pattern, Union

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from soupsavvy.interfaces import IElement
from soupsavvy.selectors.css.api import SeleniumCSSApi
from soupsavvy.selectors.xpath.api import SeleniumXPathApi

_SCRIPTS_DIR = files("soupsavvy.implementation.scripts")
_FIND_ALL_SCRIPT = _SCRIPTS_DIR.joinpath("find_all.js").read_text()
_FIND_ANCESTORS_SCRIPT = _SCRIPTS_DIR.joinpath("find_ancestors.js").read_text()


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
            for attr, value in attrs.items():
                if not isinstance(value, Pattern):
                    continue

                actual = element.get_attribute(attr)
                if actual is None:
                    return False

                if not value.search(actual):
                    return False

            return True

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
