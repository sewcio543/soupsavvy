"""
Module with `lxml` implementation of `IElement`.
`LXMLElement` class is an adapter making `lxml` tree,
compatible with `IElement` interface and usable across the library.
"""

from __future__ import annotations

from collections.abc import Iterable
from itertools import islice
from typing import Optional, Pattern, Union

import lxml.etree as etree
from lxml.etree import _Element as HtmlElement

from soupsavvy.interfaces import IElement
from soupsavvy.selectors.css.api import CSSSelectApi
from soupsavvy.selectors.xpath.api import LXMLXpathApi


class LXMLElement(IElement):
    """
    Implementation of `IElement` for `lxml` tree.
    Adapter for `lxml` objects, that makes them usable across the library.

    Example
    -------
    >>> from soupsavvy.implementation.lxml import LXMLElement
    ... from lxml.etree import fromstring
    ... node = fromstring("<html><body><div>example</div></body></html>")
    ... element = LXMLElement(node)
    """

    _NODE_TYPE = HtmlElement

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
        generator = (
            element
            for element in iterator
            if self._match(element, name=name, attrs=attrs or {})
        )
        return list(islice(self._map(generator), limit))

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

            if isinstance(value, Pattern):
                if not value.search(attribute):
                    return False
            else:
                if value not in attribute.split():
                    return False

        if name is not None and element.tag != name:
            return False

        return True

    def find_subsequent_siblings(
        self, limit: Optional[int] = None
    ) -> list[LXMLElement]:
        iterator = self._node.itersiblings(None)
        return list(islice(self._map(iterator), limit))

    def find_ancestors(self, limit: Optional[int] = None) -> list[LXMLElement]:
        iterator = self._node.iterancestors(None)
        return list(islice(self._map(iterator), limit))

    def get_attribute(self, name: str) -> Optional[str]:
        return self.node.attrib.get(name)

    def css(self, selector: str) -> CSSSelectApi:
        return CSSSelectApi(selector)

    def xpath(self, selector) -> LXMLXpathApi:
        return LXMLXpathApi(selector)

    @property
    def children(self) -> Iterable[LXMLElement]:
        iterator = self._node.iterchildren(None)
        return self._map(iterator)

    @property
    def descendants(self) -> Iterable[LXMLElement]:
        iterator = self._node.iterdescendants(None)
        return self._map(iterator)

    @property
    def parent(self) -> Optional[LXMLElement]:
        parent = self._node.getparent()
        return LXMLElement(parent) if parent is not None else None

    @property
    def name(self) -> str:
        return self._node.tag

    @property
    def text(self) -> str:
        texts = (text for text in self._node.itertext() if text is not None)
        return "".join(texts)

    def __str__(self) -> str:
        return etree.tostring(self._node, method="html", with_tail=False).decode(
            "utf-8"
        )

    @property
    def node(self) -> HtmlElement:
        return self._node

    def get(self) -> HtmlElement:
        return self.node
