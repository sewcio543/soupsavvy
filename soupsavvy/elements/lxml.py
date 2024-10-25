from __future__ import annotations

from collections.abc import Callable, Iterable
from itertools import islice
from typing import Optional, Pattern, Union

from lxml.etree import _Element as HtmlElement
from lxml.etree import tostring

from soupsavvy.interfaces import IElement


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
        for attr, value in attrs.items():
            attributes = self._get_attribute_list(attr, element=element)
            first = attributes[0]

            if first is None:
                return False

            if value is None and first is not None:
                continue

            if isinstance(value, Pattern):
                if not value.search(" ".join(attributes)):
                    return False
            else:
                if value not in attributes:
                    return False

        if name is not None and element.tag != name:
            return False

        return True

    def find_next_siblings(self, limit: Optional[int] = None) -> list[LXMLElement]:
        iterator = self.tag.itersiblings(None)
        return list(
            islice((LXMLElement(element) for element in iterator), limit),
        )

    def find_parents(self, limit: Optional[int] = None) -> list[LXMLElement]:
        iterator = self.tag.iterancestors(None)
        return list(
            islice((LXMLElement(element) for element in iterator), limit),
        )

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
        texts = (text for text in self.tag.itertext() if text is not None)

        if strip:
            texts = (text.strip() for text in texts if text != "\n")

        return separator.join(texts)  # type: ignore

    def _get_attribute_list(self, name: str, element: HtmlElement) -> list:
        value = element.attrib.get(name)

        if value is None:
            return [value]
        elif value == "":
            return [value]

        return value.split()

    def get_attribute_list(self, name: str) -> list[str]:
        return self._get_attribute_list(name, element=self.tag)

    def prettify(self) -> str:
        return ""

    @property
    def name(self) -> str:
        return self.tag.tag

    def to_lxml(self) -> HtmlElement:
        return self.tag

    @property
    def text(self) -> str:
        return self.tag.text or ""

    def css(self, selector: str) -> Callable[[LXMLElement], list[LXMLElement]]:
        from lxml.cssselect import CSSSelector

        compiled = CSSSelector(selector)

        def select(element: LXMLElement) -> list[LXMLElement]:
            return [LXMLElement(tag) for tag in compiled(element.tag)]  # type: ignore

        return select

    def __str__(self) -> str:
        return tostring(self.tag, method="htmlElement", with_tail=False).decode("utf-8")

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
