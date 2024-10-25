from __future__ import annotations

from collections.abc import Iterable
from itertools import islice
from typing import Optional, Pattern, Union

from bs4 import Tag

from soupsavvy.interfaces import IElement

try:
    from lxml.etree import tostring
    from lxml.html import HtmlElement
    from lxml.html.soupparser import _convert_tree as to_lxml
except ImportError as e:
    raise ImportError(
        "`soupsavvy.selectors.xpath` requires `lxml` package to be installed."
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


class LXMLElement(IElement):
    def __init__(self, tag: HtmlElement) -> None:
        self.tag = tag

    def find_all(
        self,
        name: Optional[str] = None,
        attrs: Optional[dict[str, Union[str, Pattern[str]]]] = None,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[LXMLElement]:
        iterator = (
            self.tag.iterdescendants(None) if recursive else self.tag.iterchildren(None)
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
        conditions = [
            all(element.attrib.get(attr) == value for attr, value in attrs.items())
        ]
        if name is not None:
            conditions.append(element.tag == name)

        return all(conditions)

    def find_next_siblings(self, limit: Optional[int] = None) -> list[LXMLElement]:
        iterator = self.tag.itersiblings(None)
        return list(
            islice((LXMLElement(element) for element in iterator), limit),
        )

    def find_parents(self, limit: Optional[int] = None) -> list[LXMLElement]:
        return [LXMLElement(element) for element in self.tag.iterancestors(None)]

    @property
    def children(self) -> Iterable[LXMLElement]:
        return (LXMLElement(element) for element in self.tag.iterchildren(None))

    @property
    def descendants(self) -> Iterable[LXMLElement]:
        return (LXMLElement(element) for element in self.tag.iterdescendants(None))

    @property
    def parent(self) -> Optional[LXMLElement]:
        parent = self.tag.getparent()
        return LXMLElement(parent) if parent is not None else None

    def get_text(self, separator: str = "", strip: bool = False) -> str:
        return self.tag.get_text(separator=separator, strip=strip)

    def get_attribute_list(self, name: str) -> list[str]:
        return self.tag.attrib[name].split(" ")

    def prettify(self) -> str:
        return ""

    @property
    def name(self) -> str:
        return self.tag.tag

    def to_lxml(self) -> HtmlElement:
        return self.tag

    def __str__(self) -> str:
        return str(tostring(self.tag))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.tag!r})"

    def __hash__(self):
        """Hashes bs4.Tag instance by id."""
        return hash(self.tag)

    def __eq__(self, other):
        """
        Checks equality of itself with another object.

        For object to be equal to UniqueTag, it should be an instance of UniqueTag
        and have the same hash value, meaning it has to wrap the same bs4.Tag instance.
        In any other case, returns False.
        """
        return isinstance(other, LXMLElement) and self.tag is other.tag
