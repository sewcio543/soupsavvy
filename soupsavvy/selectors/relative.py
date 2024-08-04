"""
Module that contains relative selectors and utility components.
"""

from typing import Optional

from bs4 import Tag

from soupsavvy.selectors.base import SoupSelector
from soupsavvy.selectors.tag_utils import TagResultSet


class RelativeSelector(SoupSelector):
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

    In css such selectors can be used in :has pseudo-class, where selector
    is anchored to the element:

    Example
    -------
    >>> div:has(> a, + p)

    Selects any div tag that has a direct child 'a' tag or a next sibling 'p' tag.
    """

    def __init__(self, selector: SoupSelector) -> None:
        """
        Initializes RelativeSelector instance with specified selector.

        Parameters
        ----------
        selector : SoupSelector
            Selector that is used to find tags relative to the anchor tag.
        """
        self._check_selector_type(selector)
        self.selector = selector

    def __eq__(self, other: object) -> bool:
        # check for RelativeSelector type for type checking sake
        if not isinstance(other, RelativeSelector):
            return False
        elif type(self) is not type(other):
            # checking for exact type match - isinstance(other, self.__class__)
            # when other is subclass of self.__class__ would call other.__eq__(self)
            # which is not desired behavior, as it returns False
            return False

        return self.selector == other.selector

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.selector})"

    def __repr__(self) -> str:
        return str(self)


class BaseRelativeSibling(RelativeSelector):
    """
    Base class with implementation for relative sibling selectors,
    searches for next sibling(s) of the anchor tag.
    Child class needs to define '_limit' class attribute to specify
    how many next siblings to search for.
    """

    # limit of next siblings to check
    _limit: Optional[int] = None

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
        search = tag.parent or tag
        # find al sibling tags that match the selector
        matching = TagResultSet(
            self.selector.find_all(search, recursive=False),
        )
        # find n next sibling tags
        next_ = TagResultSet(tag.find_next_siblings(limit=self._limit))  # type: ignore
        # find intersection between two sets
        matches = matching & next_
        return matches.fetch(limit)


class RelativeChild(RelativeSelector):
    """
    RelativeChild selector is used to find tags matching selector that are
    direct children of the tag that is being searched.

    For RelativeChild selector, with TagSelector targeting 'p' tag.

    Example
    -------
    >>> RelativeChild(TagSelector("p"))

    when 'div' element is passed into find methods:

    Example
    -------
    >>> <div><p></p><a></a></div> ✔️
    >>> <div><a><p></p></a></div> ❌
    >>> <div><a></a></div> ❌

    Returns element only if it is a direct child of the anchor element
    and matches the selector.

    RelativeChild selector is equivalent to using '>' combinator in css selectors:

    Example
    -------
    >>> div > p { color: red; }

    It can be created with Anchor instance as well with use of '>' operator:

    Example
    -------
    >>> Anchor > TagSelector("p")

    Which is equivalent to the first example and returns RelativeChild selector.

    Notes
    -------
    Behavior of RelativeChild selector is equivalent to using find methods of
    selector with recursive=False parameter and is implemented to support
    'has' and ChildCombinator selector.
    """

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
        return self.selector.find_all(tag, recursive=False, limit=limit)


class RelativeDescendant(RelativeSelector):
    """
    RelativeDescendant selector is used to find tags matching selector that are
    descendants of the tag that is being searched.

    For RelativeDescendant selector, with TagSelector targeting 'p' tag,

    Example
    -------
    >>> RelativeDescendant(TagSelector("p"))

    when 'div' element is passed into find methods:

    Example
    -------
    >>> <div><p></p><a></a></div> ✔️
    >>> <div><a><p></p></a></div> ✔️
    >>> <div><a></a></div> ❌
    >>> <div></div><p></p> ❌

    Returns element only if it is a descendant of the anchor element
    and matches the selector.

    RelativeDescendant selector is equivalent to using whitespace " " combinator
    in css selectors.

    Example
    -------
    >>> div p { color: red; }

    It can be created with Anchor instance as well with use of '>>' operator:

    Example
    -------
    >>> Anchor >> TagSelector("p")

    Which is equivalent to the first example and returns RelativeDescendant selector.

    Notes
    -------
    Behavior of RelativeDescendant selector is equivalent to using find methods of
    selector with default recursive=True parameter and is implemented to support
    'has' and DescendantCombinator selector.
    """

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
        return self.selector.find_all(tag, recursive=True, limit=limit)


class RelativeNextSibling(BaseRelativeSibling):
    """
    RelativeNextSibling selector is used to find tags matching selector that are
    next siblings of the tag that is being searched.

    For RelativeNextSibling selector, with TagSelector targeting 'p' tag,

    Example
    -------
    >>> RelativeNextSibling(TagSelector("p"))

    when 'div' element is passed into find methods:

    Example
    -------
    >>> <div></div><p></p> ✔️
    >>> <div></div><a></a><p></p>  ❌
    >>> <p></p><div></div> ❌

    Returns element only if it is a next sibling of the anchor element
    and matches the selector.

    RelativeNextSibling selector is equivalent to using + combinator in css selectors.

    Example
    -------
    >>> div + p { color: red; }

    It can be created with Anchor instance as well with use of '+' operator:

    Example
    -------
    >>> Anchor + TagSelector("p")

    Which is equivalent to the first example and returns RelativeNextSibling selector.
    """

    _limit = 1


class RelativeSubsequentSibling(BaseRelativeSibling):
    """
    RelativeSubsequentSibling selector is used to find tags matching selector that are
    subsequent siblings of the tag that is being searched.

    For RelativeSubsequentSibling selector, with TagSelector targeting 'p' tag,

    Example
    -------
    >>> RelativeSubsequentSibling(TagSelector("p"))

    when 'div' element is passed into find methods:

    Example
    -------
    >>> <div></div><p></p> ✔️
    >>> <div></div><a></a><p></p> ✔️
    >>> <p></p><div></div> ❌
    >>> <div></div><span><p></p></span> ❌

    Returns element only if it is a subsequent sibling of the anchor element
    and matches the selector.

    RelativeSubsequentSibling selector is equivalent
    to using ~ combinator in css selectors.

    Example
    -------
    >>> div ~ p { color: red; }

    It can be created with Anchor instance as well with use of '*' operator:

    Example
    -------
    >>> Anchor * TagSelector("p")

    Which is equivalent to the first example
    and returns RelativeSubsequentSibling selector.
    """

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
