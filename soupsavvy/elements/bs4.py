from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Optional, Pattern, Union

from bs4 import Tag

import soupsavvy.exceptions as exc
from soupsavvy.interfaces import IElement

try:
    import soupsieve as sv
except ImportError as e:
    raise ImportError(
        "`soupsavvy.elements.bs4` requires `soupsieve` package to be installed."
    ) from e

try:
    from lxml.html import HtmlElement
    from lxml.html.soupparser import _convert_tree as to_lxml
except ImportError as e:
    raise ImportError(
        "`soupsavvy.elements.bs4` requires `lxml` package to be installed."
    ) from e


class SoupElement(IElement):
    def __init__(self, tag: Tag) -> None:
        self.tag = tag

    def find_all(
        self,
        name: Optional[str] = None,
        attrs: Optional[dict[str, Union[str, Pattern[str]]]] = None,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[SoupElement]:
        return [
            SoupElement(element)
            for element in self.tag.find_all(
                name=name, attrs=attrs or {}, recursive=recursive, limit=limit
            )
        ]

    def find_next_siblings(self, limit: Optional[int] = None) -> list[SoupElement]:
        return [
            SoupElement(element) for element in self.tag.find_next_siblings(limit=limit)  # type: ignore
        ]

    def find_parents(self, limit: Optional[int] = None) -> list[SoupElement]:
        return [SoupElement(element) for element in self.tag.find_parents(limit=limit)]

    @property
    def children(self) -> Iterable[SoupElement]:
        return (
            SoupElement(element)
            for element in self.tag.children
            if isinstance(element, Tag)
        )

    @property
    def descendants(self) -> Iterable[SoupElement]:
        return (
            SoupElement(element)
            for element in self.tag.descendants
            if isinstance(element, Tag)
        )

    @property
    def parent(self) -> Optional[SoupElement]:
        parent = self.tag.parent
        return SoupElement(parent) if parent is not None else None

    def get_text(self, separator: str = "", strip: bool = False) -> str:
        return self.tag.get_text(separator=separator, strip=strip)

    def get_attribute_list(self, name: str) -> list[str]:
        return self.tag.get_attribute_list(name)

    def prettify(self) -> str:
        return self.tag.prettify()

    @property
    def name(self) -> str:
        return self.tag.name

    def to_lxml(self) -> HtmlElement:
        return to_lxml(self.tag, None)  # type: ignore

    @property
    def text(self) -> str:
        strings = list(self.tag.strings)
        return strings[0] if strings else ""

    def css(self, selector: str) -> Callable[[SoupElement], list[SoupElement]]:
        try:
            compiled = sv.compile(selector)
        except sv.SelectorSyntaxError:
            raise exc.InvalidCSSSelector(
                "CSS selector constructed from provided parameters "
                f"is not valid: {selector}"
            )

        def select(element: SoupElement) -> list[SoupElement]:
            return [SoupElement(tag) for tag in compiled.select(element.tag)]

        return select

    def __str__(self) -> str:
        return str(self.tag)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.tag!r})"

    def __hash__(self):
        """Hashes bs4.Tag instance by id."""
        return id(self.tag)

    def __eq__(self, other):
        """
        Checks equality of itself with another object.

        For object to be equal to UniqueTag, it should be an instance of UniqueTag
        and have the same hash value, meaning it has to wrap the same bs4.Tag instance.
        In any other case, returns False.
        """
        return isinstance(other, SoupElement) and hash(self) == hash(other)
