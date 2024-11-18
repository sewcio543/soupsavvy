"""
Module with `bs4` implementation of `IElement`.
`SoupElement` class is an adapter making `bs4` tree,
compatible with `IElement` interface and usable across the library.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Optional, Pattern, Union

import bs4

from soupsavvy.interfaces import IElement, SelectionApi
from soupsavvy.selectors.css.api import SoupsieveApi


class SoupElement(IElement):
    """
    Implementation of `IElement` for `BeautifulSoup` tree.
    Adapter for `bs4` objects, that makes them usable across the library.

    Example
    -------
    >>> from soupsavvy.implementation.bs4 import SoupElement
    ... from bs4 import BeautifulSoup
    ... node = BeautifulSoup("<div>example</div>", "html.parser")
    ... element = SoupElement(node)
    """

    _NODE_TYPE = bs4.Tag

    def find_all(
        self,
        name: Optional[str] = None,
        attrs: Optional[dict[str, Union[str, Pattern[str]]]] = None,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[SoupElement]:
        return [
            SoupElement(element)
            for element in self.node.find_all(
                name=name, attrs=attrs or {}, recursive=recursive, limit=limit
            )
        ]

    def find_subsequent_siblings(
        self, limit: Optional[int] = None
    ) -> list[SoupElement]:
        return [
            SoupElement(element) for element in self.node.find_next_siblings(limit=limit)  # type: ignore
        ]

    def find_ancestors(self, limit: Optional[int] = None) -> list[SoupElement]:
        return [SoupElement(element) for element in self.node.find_parents(limit=limit)]

    def get_attribute(self, name: str) -> Optional[str]:
        attr = self.node.get(name)

        if isinstance(attr, list):
            attr = " ".join(attr)

        return attr

    @staticmethod
    def css(selector: str) -> SelectionApi:
        return SoupsieveApi(selector)

    @property
    def children(self) -> Iterable[SoupElement]:
        return (
            SoupElement(element)
            for element in self.node.children
            if isinstance(element, bs4.Tag)
        )

    @property
    def descendants(self) -> Iterable[SoupElement]:
        return (
            SoupElement(element)
            for element in self.node.descendants
            if isinstance(element, bs4.Tag)
        )

    @property
    def parent(self) -> Optional[SoupElement]:
        parent = self.node.parent
        return SoupElement(parent) if parent is not None else None

    @property
    def name(self) -> str:
        return self.node.name

    @property
    def text(self) -> str:
        return self.node.text

    def __hash__(self):
        return id(self._node)
