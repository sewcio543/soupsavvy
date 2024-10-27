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
            for element in self._node.find_all(
                name=name, attrs=attrs or {}, recursive=recursive, limit=limit
            )
        ]

    def find_next_siblings(self, limit: Optional[int] = None) -> list[SoupElement]:
        return [
            SoupElement(element) for element in self._node.find_next_siblings(limit=limit)  # type: ignore
        ]

    def find_ancestors(self, limit: Optional[int] = None) -> list[SoupElement]:
        return [
            SoupElement(element) for element in self._node.find_parents(limit=limit)
        ]

    @property
    def children(self) -> Iterable[SoupElement]:
        return (
            SoupElement(element)
            for element in self._node.children
            if isinstance(element, Tag)
        )

    @property
    def descendants(self) -> Iterable[SoupElement]:
        return (
            SoupElement(element)
            for element in self._node.descendants
            if isinstance(element, Tag)
        )

    @property
    def parent(self) -> Optional[SoupElement]:
        parent = self._node.parent
        return SoupElement(parent) if parent is not None else None

    def get_text(self, separator: str = "", strip: bool = False) -> str:
        return self._node.get_text(separator=separator, strip=strip)

    def get_attribute_list(self, name: str) -> list[str]:
        return self._node.get_attribute_list(name)

    def prettify(self) -> str:
        return self._node.prettify()

    @property
    def name(self) -> str:
        return self._node.name

    @property
    def text(self) -> str:
        nodes = list(self._node.strings)
        return nodes[0] if len(nodes) == 1 else ""

    @staticmethod
    def css(selector: str) -> SelectionApi:
        return SoupsieveApi(selector)

    def __str__(self) -> str:
        return str(self._node)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._node!r})"

    def __hash__(self):
        """Hashes bs4.Tag instance by id."""
        return id(self._node)

    def __eq__(self, other):
        """
        Checks equality of itself with another object.

        For object to be equal to UniqueTag, it should be an instance of UniqueTag
        and have the same hash value, meaning it has to wrap the same bs4.Tag instance.
        In any other case, returns False.
        """
        return isinstance(other, SoupElement) and hash(self) == hash(other)
