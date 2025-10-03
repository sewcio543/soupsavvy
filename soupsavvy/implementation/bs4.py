"""
Module with `bs4` implementation of `IElement`.
`SoupElement` class is an adapter making `bs4` tree,
compatible with `IElement` interface and usable across the library.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Optional, Pattern, Union

import bs4
from typing_extensions import Self

from soupsavvy.interfaces import IElement, SelectionApi
from soupsavvy.selectors.css.api import SoupsieveApi


class SoupElement(IElement[bs4.Tag]):
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
    ) -> list[Self]:
        attrs = attrs or {}
        iterable = self.node.find_all(
            name=name, attrs=attrs, recursive=recursive, limit=limit
        )
        return list(self._map(iterable))

    def find_subsequent_siblings(self, limit: Optional[int] = None) -> list[Self]:
        return list(self._map(self.node.find_next_siblings(limit=limit)))

    def find_ancestors(self, limit: Optional[int] = None) -> list[Self]:
        return list(self._map(self.node.find_parents(limit=limit)))

    def get_attribute(self, name: str) -> Optional[str]:
        attr = self.node.get(name)

        if isinstance(attr, list):
            attr = " ".join(attr)

        return attr

    @staticmethod
    def css(selector: str) -> SelectionApi:
        return SoupsieveApi(selector)

    @property
    def children(self) -> Iterable[Self]:
        generator = (
            element
            for element in self.node.children
            if isinstance(element, self._NODE_TYPE)
        )
        return self._map(generator)

    @property
    def descendants(self) -> Iterable[Self]:
        generator = (
            element
            for element in self.node.descendants
            if isinstance(element, self._NODE_TYPE)
        )
        return self._map(generator)

    @property
    def parent(self) -> Optional[Self]:
        parent = self.node.parent
        return self.from_node(parent) if parent is not None else None

    @property
    def name(self) -> str:
        return self.node.name

    @property
    def text(self) -> str:
        return self.node.text

    def __hash__(self):
        return id(self._node)
