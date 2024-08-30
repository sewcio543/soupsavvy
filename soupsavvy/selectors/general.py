"""
Module for general purpose selectors.

Classes
-------
TypeSelector - combines type and attribute selectors
PatternSelector - matches elements based on text content and selector
UniversalSelector - universal selector (*)
"""

import itertools
from dataclasses import dataclass
from typing import Optional, Pattern

from bs4 import SoupStrainer, Tag

import soupsavvy.selectors.namespace as ns
from soupsavvy.selectors.base import SelectableCSS, SoupSelector
from soupsavvy.selectors.tag_utils import TagIterator
from soupsavvy.utils.deprecation import deprecated_class


@dataclass
class TypeSelector(SoupSelector, SelectableCSS):
    """
    Component for finding elements based on tag name.
    `soupsavvy` counterpart of css type selector.

    Example
    -------
    >>> TypeSelector("div")

    matches all elements that have "div" tag name.

    Example
    -------
    >>> <div class="widget">Hello World</div> ✔️
    >>> <a href="/shop">Hello World</a> ❌

    It's soupsavvy counterpart of passing name to bs4 find methods.

    Example
    -------
    >>> soup.find_all("div")

    Returns the same result as:

    Example
    -------
    >>> TypeSelector("div").find_all(soup)

    Parameters
    ----------
    name : str
        HTML tag name ex. "a", "div".

    Notes
    -----
    For more information about type selectors see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/Type_selectors
    """

    name: str

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
        params = {ns.NAME: self.name}
        return tag.find_all(**params, recursive=recursive, limit=limit)

    @property
    def css(self) -> str:
        # css selector for tag name is just the tag name ex. "div"
        return self.name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TypeSelector):
            return False

        # TypeSelectors produce the same results if names of the tag are the same
        return self.name == other.name


@dataclass
class PatternSelector(SoupSelector):
    """
    Class representing HTML element with specific string pattern for text.
    Provides elements matching with text matching the pattern.

    Example
    -------
    >>> PatternSelector(pattern="Hello World")

    matches all element with exact text content "Hello World".

    Example
    -------
    >>> <div>Hello World</div> ✔️
    >>> <div>Hello Python</div> ❌
    >>> <div>Hello World 3</div> ❌

    Parameters
    ----------
    pattern: str | Pattern
        A pattern to match text of the element. Can be a string for exact match
        or Pattern for any more complex regular expressions.

    Notes
    -----
    Selector uses re.search function to match text content
    if compiled regex is passed as pattern.
    Providing 're.compile(r"[0-9]")' as pattern will much any element with a digit in text.

    Example
    -------
    >>> import re
    >>> PatternSelector(pattern=re.compile(r"[0-9]"))

    Example
    -------
    >>> <div>Hello World 123</div> ✔️
    >>> <div>Hello World</div> ❌

    Due to bs4 implementation, element does not match the pattern if it has any children.
    Only leaf nodes can be returned by PatternSelector find methods.

    Example
    -------
    >>> <div>Hello World<span></span></div> ❌
    """

    pattern: ns.PatternType

    def __post_init__(self) -> None:
        """Sets up compiled regex pattern used for SoupStrainer in find methods."""
        self._pattern = (
            str(self.pattern) if not isinstance(self.pattern, Pattern) else self.pattern
        )

    def find_all(
        self, tag: Tag, recursive: bool = True, limit: Optional[int] = None
    ) -> list[Tag]:
        iterator = TagIterator(tag, recursive=recursive)
        strainer = SoupStrainer(string=self._pattern)  # type: ignore
        filter_ = filter(strainer.search_tag, iterator)
        return list(itertools.islice(filter_, limit))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PatternSelector):
            return False

        return self._pattern == other._pattern


@dataclass
class UniversalSelector(SoupSelector, SelectableCSS):
    """
    Class representing a wildcard tag that matches ny and all types of elements
    in html page.

    UniversalSelector implements SelectableCSS interface with wildcard css selector "*",
    aka. universal selector, that matches all elements in html page.

    Example
    -------
    >>> any_element = UniversalSelector()
    >>> any_element.selector
    "*"

    Notes
    -----
    For more information on universal selector see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/Universal_selectors
    """

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
        return tag.find_all(recursive=recursive, limit=limit)

    @property
    def css(self) -> str:
        """Returns wildcard css selector matching all elements in the markup."""
        return ns.CSS_SELECTOR_WILDCARD

    def __eq__(self, other: object) -> bool:
        # UniversalSelector is always the same
        return isinstance(other, UniversalSelector)


@deprecated_class(
    f"AnyTagSelector is deprecated, use {UniversalSelector.__name__} class instead."
)
class AnyTagSelector(UniversalSelector):
    """Alias for UniversalSelector class. Deprecated component."""


class SelfSelector(SoupSelector):
    """
    Class representing a selector that matches the element itself.
    Convenience component that can be used for compatibility.

    Example
    -------
    >>> SelfSelector()

    always matches the tag that is passed to the find methods.

    Can be used in user-defined model for scope if element itself is the scope.
    """

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
        return [tag]

    def __eq__(self, other: object) -> bool:
        # needs to be the same type
        return isinstance(other, SelfSelector)
