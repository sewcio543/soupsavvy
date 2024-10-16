"""
Module with miscellaneous selectors.

Classes
-------
- `TypeSelector` - combines type and attribute selectors
- `PatternSelector` - matches elements based on text content and selector
- `UniversalSelector` - universal selector (*)
- `SelfSelector` - matches the element itself
- `ExpressionSelector` - matches elements based on user-defined function
"""

import itertools
from collections.abc import Callable
from dataclasses import dataclass
from typing import Optional, Pattern

from bs4 import SoupStrainer, Tag
from typing_extensions import deprecated

import soupsavvy.selectors.namespace as ns
from soupsavvy.base import SelectableCSS, SoupSelector
from soupsavvy.utils.selector_utils import TagIterator


@dataclass
class TypeSelector(SoupSelector, SelectableCSS):
    """
    Selector for finding elements based on tag name (type).
    Counterpart of css type selectors.

    Example
    -------
    >>> TypeSelector("div")

    matches all elements that have "div" tag name.

    Example
    -------
    >>> <div class="widget">Hello World</div> ✔️
    >>> <a href="/shop">Hello World</a> ❌

    CSS counterpart can be represented as:

    Example
    -------
    >>> div

    And can be retrieved with `css` property.

    Example
    -------
    >>> TypeSelector("div").css
    "div"

    Parameters
    ----------
    name : str
        Tag name of the element ex. "a", "div".

    Notes
    -----
    For more information about type selectors, see:

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
    Selector for finding elements based on text content pattern.

    Example
    -------
    >>> PatternSelector(pattern="Hello World")

    matches all element with exact text content "Hello World".

    Example
    -------
    >>> <div>Hello World</div> ✔️
    >>> <div>Hello Python</div> ❌
    >>> <div>Hello World 3</div> ❌

    In case of using regex pattern, `re.search` is used to match the attribute value.

    Example
    -------
    >>> PatternSelector(pattern=re.compile(r"[0-9]+"))

    matches all elements with text content containing at least one digit.

    Example
    -------
    >>> <div>Hello World 123</div> ✔️
    >>> <div>Hello World</div> ❌

    Parameters
    ----------
    pattern: str | Pattern
        Pattern to match text of the element. Can be a string for exact match
        or `Pattern` for any more complex regular expressions.

    Notes
    -----
    Due to `bs4` implementation, element does not match the pattern if it has any children.
    Only leaf nodes can be returned by `PatternSelector` find methods.
    """

    pattern: ns.PatternType

    def __post_init__(self) -> None:
        """Sets up compiled regex pattern used for `SoupStrainer` in find methods."""
        self._pattern = (
            str(self.pattern) if not isinstance(self.pattern, Pattern) else self.pattern
        )

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
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
    Selector representing a wildcard pattern, that matches all elements in the html page.

    Example
    -------
    >>> UniversalSelector()

    CSS counterpart can be represented as:

    Example
    -------
    >>> *

    And can be retrieved with `css` property.

    Example
    -------
    >>> UniversalSelector().css
    "*"

    Notes
    -----
    For more information on universal selector, see:

    https://developer.mozilla.org/en-US/docs/Web/CSS/Universal_selectors
    """

    def find_all(
        self, tag: Tag, recursive: bool = True, limit: Optional[int] = None
    ) -> list[Tag]:
        return tag.find_all(recursive=recursive, limit=limit)

    @property
    def css(self) -> str:
        """Returns wildcard css selector matching all elements in the markup."""
        return ns.CSS_SELECTOR_WILDCARD

    def __eq__(self, other: object) -> bool:
        # UniversalSelector is always the same
        return isinstance(other, UniversalSelector)


@deprecated(f"'AnyTagSelector' is deprecated, use 'UniversalSelector' class instead.")
class AnyTagSelector(UniversalSelector):
    """Alias for `UniversalSelector` class. Deprecated component."""


class SelfSelector(SoupSelector):
    """
    Selector matching only the element itself.
    Convenience component that can be used for compatibility.

    Example
    -------
    >>> SelfSelector()

    always matches the tag that is passed to the find methods.

    Notes
    -----
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


@dataclass
class ExpressionSelector(SoupSelector):
    """
    Selector that matches elements based on a user-defined function (predicate),
    that is used as filter for `bs4` object.

    Applies predicate to each element and returns those that satisfy the condition.

    Parameters
    ----------
    f : Callable[[Tag], bool]
        A user-defined function (predicate) that determines whether
        the element should be selected.

    Examples
    --------
    >>> selector = ExpressionSelector(lambda x: x.name not in {"a", "div"})
    ... selector.find(soup)

    Notes
    -----
    Any exceptions should be handled inside provided function.
    If raised, it will be propagated to the caller.
    """

    f: Callable[[Tag], bool]

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
        iterator = TagIterator(tag, recursive=recursive)
        filter_ = filter(self.f, iterator)
        return list(itertools.islice(filter_, limit))

    def __eq__(self, other) -> bool:
        if not isinstance(other, ExpressionSelector):
            return False

        return self.f is other.f
