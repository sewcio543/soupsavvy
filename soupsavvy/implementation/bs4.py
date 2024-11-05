from __future__ import annotations

from collections.abc import Iterable
from typing import Optional, Pattern, Union

from bs4 import Tag

from soupsavvy.interfaces import IElement, SelectionApi
from soupsavvy.selectors.css.api import SoupsieveApi


class SoupElement(IElement):
    def __init__(self, node: Tag) -> None:
        self._node = node

    @property
    def node(self) -> Tag:
        return self._node

    @classmethod
    def from_node(cls, node: Tag) -> SoupElement:
        return SoupElement(node)

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

    @property
    def children(self) -> Iterable[SoupElement]:
        return (
            SoupElement(element)
            for element in self.node.children
            if isinstance(element, Tag)
        )

    @property
    def descendants(self) -> Iterable[SoupElement]:
        return (
            SoupElement(element)
            for element in self.node.descendants
            if isinstance(element, Tag)
        )

    @property
    def parent(self) -> Optional[SoupElement]:
        parent = self.node.parent
        return SoupElement(parent) if parent is not None else None

    def get_attribute(self, name: str) -> Optional[str]:
        attr = self.node.get(name)

        if isinstance(attr, list):
            attr = " ".join(attr)

        return attr

    @property
    def name(self) -> str:
        return self.node.name

    @property
    def text(self) -> str:
        return self.node.text

    @staticmethod
    def css(selector: str) -> SelectionApi:
        return SoupsieveApi(selector)

    def __str__(self) -> str:
        return str(self._node)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._node!r})"

    def __hash__(self):
        return id(self._node)

    def __eq__(self, other):
        return isinstance(other, SoupElement) and self.node == other.node
