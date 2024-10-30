from __future__ import annotations

from collections.abc import Iterable
from itertools import islice
from typing import Optional, Pattern, Union

from lxml.etree import _Element as HtmlElement
from lxml.etree import tostring

from soupsavvy.interfaces import IElement
from soupsavvy.selectors.css.api import CSSSelectApi
from soupsavvy.selectors.xpath.api import LXMLXpathApi


class LXMLElement(IElement):
    def __init__(self, node: HtmlElement) -> None:
        self._node = node

    @property
    def node(self) -> HtmlElement:
        return self._node

    def find_all(
        self,
        name: Optional[str] = None,
        attrs: Optional[dict[str, Union[str, Pattern[str]]]] = None,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[LXMLElement]:
        iterator = (
            self._node.iterdescendants(None)
            if recursive
            else self._node.iterchildren(None)
        )

        return list(
            islice(
                (
                    LXMLElement(element)
                    for element in iterator
                    if self._match(element, name=name, attrs=attrs or {})
                ),
                limit,
            ),
        )

    def _match(
        self,
        element: HtmlElement,
        name: Optional[str],
        attrs: dict[str, Union[str, Pattern[str]]],
    ) -> bool:
        for attr, value in attrs.items():
            attribute = element.attrib.get(attr)

            if attribute is None:
                return False

            if value is None and attribute is not None:
                continue

            if isinstance(value, Pattern):
                if not value.search(attribute):
                    return False
            else:
                if value not in attribute.split():
                    return False

        if name is not None and element.tag != name:
            return False

        return True

    def find_next_siblings(self, limit: Optional[int] = None) -> list[LXMLElement]:
        iterator = self._node.itersiblings(None)
        return list(
            islice((LXMLElement(element) for element in iterator), limit),
        )

    def find_ancestors(self, limit: Optional[int] = None) -> list[LXMLElement]:
        iterator = self._node.iterancestors(None)
        return list(
            islice((LXMLElement(element) for element in iterator), limit),
        )

    @property
    def children(self) -> Iterable[LXMLElement]:
        return (LXMLElement(element) for element in self._node.iterchildren(None))

    @property
    def descendants(self) -> Iterable[LXMLElement]:
        return (LXMLElement(element) for element in self._node.iterdescendants(None))

    @property
    def parent(self) -> Optional[LXMLElement]:
        parent = self._node.getparent()
        return LXMLElement(parent) if parent is not None else None

    def get_text(self, separator: str = "", strip: bool = False) -> str:
        texts = (text for text in self._node.itertext() if text is not None)
        return separator.join(texts)  # type: ignore

    def get_attribute(self, name: str) -> Optional[str]:
        return self.node.attrib.get(name)

    def prettify(self) -> str:
        return ""

    @property
    def name(self) -> str:
        return self._node.tag

    @property
    def text(self) -> str:
        texts = (text for text in self._node.itertext() if text is not None)
        return "".join(texts)

    def css(self, selector: str) -> CSSSelectApi:
        return CSSSelectApi(selector)

    def xpath(self, selector) -> LXMLXpathApi:
        return LXMLXpathApi(selector)

    def __str__(self) -> str:
        return tostring(self._node, method="html", with_tail=False).decode("utf-8")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._node!r})"

    def __hash__(self):
        """Hashes bs4.Tag instance by id."""
        return hash(self._node)

    def __eq__(self, other):
        """
        Checks equality of itself with another object.

        For object to be equal to UniqueTag, it should be an instance of UniqueTag
        and have the same hash value, meaning it has to wrap the same bs4.Tag instance.
        In any other case, returns False.
        """
        return isinstance(other, LXMLElement) and self._node is other._node
