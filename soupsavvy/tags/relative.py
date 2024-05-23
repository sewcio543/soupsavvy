"""
Module that contains relative selectors and utility components.
"""

from typing import Callable, Optional

from bs4 import Tag

from soupsavvy.tags.base import SelectableSoup
from soupsavvy.tags.tag_utils import TagResultSet

Operator = Callable[[SelectableSoup, SelectableSoup], SelectableSoup]


class RelativeSelector(SelectableSoup):
    """
    Base class for relative selectors, that are used to find tags relative
    to the tag that is being searched, which is considered an anchor.

    CSS definition of relative selectors states that it is a selector representing
    an element relative to one or more anchor elements preceded by a combinator.

    In this use case, the anchor element is the tag that is being searched, and
    the combinator is the logic of specific relative selector that is used.

    Example
    -------
    >>> selector = Anchor > TagSelector("div")
    >>> selector.find_all(tag)

    Uses RelativeChild selector to find any div tag that is a direct child of the
    tag that is being searched (passed as an argument).
    """

    def __init__(self, selector: SelectableSoup) -> None:
        """
        Initializes RelativeSelector instance with specified selector.

        Parameters
        ----------
        selector : SelectableSoup
            Selector that is used to find tags relative to the anchor tag.
        """
        self.selector = selector


class BaseRelativeSibling(RelativeSelector):
    _limit: Optional[int] = None

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
        search = tag.parent or tag
        matching = TagResultSet(
            self.selector.find_all(search, recursive=False),
        )
        next_ = TagResultSet(tag.find_next_siblings(limit=self._limit))  # type: ignore
        matches = matching.intersection(next_)
        return matches.tags[:limit]


class RelativeChild(RelativeSelector):
    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
        return self.selector.find_all(tag, recursive=False, limit=limit)


class RelativeDescendant(RelativeSelector):
    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
        return self.selector.find_all(tag, recursive=True, limit=limit)


class RelativeNextSibling(BaseRelativeSibling):
    _limit = 1


class RelativeSubsequentSibling(BaseRelativeSibling):
    _limit = None


class _Anchor:
    """
    Anchor components is a way to create relative selectors in a more
    readable way by using operators.

    _Anchor is an internal class and it's advisable to use the Anchor
    instance instead, which can be considered like a singleton.

    Component supports the following operators:
    * `>`: RelativeChild

    Example
    -------
    >>> Anchor > TagSelector("div")

    Creates a RelativeChild selector, that selects any div tag that is a direct
    child of the tag that is being searched.

    * `>>`: RelativeDescendant

    Example
    -------
    >>> Anchor >> TagSelector("div")

    Creates a RelativeDescendant selector, that selects any div tag that is a descendant
    of the tag that is being searched. This is default behavior of selectors,
    and is equivalent to using the TagSelector directly, but is implemented
    for the sake of consistency.

    * `+`: RelativeNextSibling

    Example
    -------
    >>> Anchor + TagSelector("div")

    Creates a RelativeNextSibling selector, that selects any div tag that is next
    sibling of the tag that is being searched, it can logically return at most one tag.

    * `*`: RelativeSubsequentSibling

    Example
    -------
    >>> Anchor * TagSelector("div")

    Creates a RelativeSubsequentSibling selector, that selects any div tag
    that is a subsequent sibling of the tag that is being searched.

    This imitates css selector relative selectors that are used for example in
    :has pseudo-class, that accepts relative selector list as an argument.

    Example
    -------
    >>> :has(> div, + a)

    This translated to soupsavvy would be:

    Example
    -------
    >>> HasSelector(Anchor > TagSelector("div"), Anchor + TagSelector("a"))

    Which would match any tag that has a direct child 'div' and a next sibling 'a' tag.
    Selected tag is the anchor tag that is being searched.

    Notes
    -------
    For more information on relative selectors, see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_selectors/Selector_structure#relative_selector
    """

    def __gt__(self, x) -> RelativeSelector:
        return RelativeChild(x)

    def __rshift__(self, x) -> RelativeSelector:
        return RelativeDescendant(x)

    def __add__(self, x) -> RelativeSelector:
        return RelativeNextSibling(x)

    def __mul__(self, x) -> RelativeSelector:
        return RelativeSubsequentSibling(x)


# instance of Anchor class with purpose to be used as a singleton
Anchor = _Anchor()
