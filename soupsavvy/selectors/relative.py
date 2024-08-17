"""
Module that contains relative selectors and utility components.
"""

from typing import Callable, Optional

from bs4 import Tag

from soupsavvy.selectors.base import CompositeSoupSelector, SoupSelector, check_selector
from soupsavvy.selectors.tag_utils import TagIterator, TagResultSet


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
    >>> selector = Anchor > TypeSelector("div")
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
        self.selector = check_selector(selector)

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
    how many next siblings to search for and '_func' class attribute
    to specify which method to use for finding siblings.
    """

    # limit of next siblings to check
    _limit: Optional[int]
    # function to use for finding siblings
    _func: Callable[..., list]

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
        search = tag.find_parents()[0]
        # find all sibling tags that match the selector
        matching = TagResultSet(
            self.selector.find_all(search, recursive=False),
        )
        siblings = TagResultSet(self.__class__._func(tag, limit=self._limit))
        # find intersection between two sets
        matches = matching & siblings
        return matches.fetch(limit)


class BaseAncestorSelector(RelativeSelector):
    """
    Base class with implementation for ancestor selectors,
    searches for ancestor(s) of the anchor tag.
    Child class needs to define '_limit' class attribute to specify
    how many ancestors to search for.
    """

    _limit: Optional[int]

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
        limit = limit or self._limit
        # get max number of ancestors that can possibly be returned
        ancestors = tag.find_parents(limit=self._limit)

        if not ancestors:
            # if no ancestors, make no sense to search
            return []

        search = ancestors[-1].parent or ancestors[-1]
        # search within parent of last ancestor
        matching = TagResultSet(self.selector.find_all(search))
        matches = TagResultSet(ancestors) & matching
        return matches.fetch(limit)


class RelativeChild(RelativeSelector):
    """
    RelativeChild selector is used to find tags matching selector that are
    direct children of the tag that is being searched.

    For RelativeChild selector, with TypeSelector targeting 'p' tag.

    Example
    -------
    >>> RelativeChild(TypeSelector("p"))

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
    >>> Anchor > TypeSelector("p")

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

    For RelativeDescendant selector, with TypeSelector targeting 'p' tag,

    Example
    -------
    >>> RelativeDescendant(TypeSelector("p"))

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
    >>> Anchor >> TypeSelector("p")

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

    For RelativeNextSibling selector, with TypeSelector targeting 'p' tag,

    Example
    -------
    >>> RelativeNextSibling(TypeSelector("p"))

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
    >>> Anchor + TypeSelector("p")

    Which is equivalent to the first example and returns RelativeNextSibling selector.
    """

    _limit = 1
    _func = Tag.find_next_siblings


class RelativeSubsequentSibling(BaseRelativeSibling):
    """
    RelativeSubsequentSibling selector is used to find tags matching selector that are
    subsequent siblings of the tag that is being searched.

    For RelativeSubsequentSibling selector, with TypeSelector targeting 'p' tag,

    Example
    -------
    >>> RelativeSubsequentSibling(TypeSelector("p"))

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
    >>> Anchor * TypeSelector("p")

    Which is equivalent to the first example
    and returns RelativeSubsequentSibling selector.
    """

    _limit = None
    _func = Tag.find_next_siblings


class RelativeParent(BaseAncestorSelector):
    """
    `RelativeParent` selector is used to find tags matching selector that are
    parent of the tag that is being searched.

    For `RelativeParent` selector, with `TypeSelector` targeting 'div' tag,

    Example
    -------
    >>> RelativeParent(TypeSelector("div"))

    when 'p' element is passed into find methods:

    Example
    -------
    >>> <div><p></p></div> ✔️
    >>> <div><a><p></p></a></div> ❌
    >>> <span><p></p></span> ❌

    Returns element only if it is a parent of the anchor element
    and matches the selector.

    Although this combinator does not have its counterpart in CSS, it can be
    represented as has selector, where child combinator is explicitly stated:

    Example
    -------
    >>> div:has(> p)

    Where 'p' element is an anchor element passed to find methods and 'div' is
    the selector that matches its parent.

    It can be created with Anchor instance as well with use of '<' operator:

    Example
    -------
    >>> Anchor < TypeSelector("div")

    Which is equivalent to the first example and returns `RelativeParent` selector.

    Notes
    -------
    `RelativeParent` selector ignores `recursive` parameter,
    as it is always searches only for parent of the anchor element,
    `find_all` method can return at most one element (parent).
    """

    _limit = 1


class RelativeAncestor(BaseAncestorSelector):
    """
    `RelativeAncestor` selector is used to find tags matching selector that are
    ancestors of the tag that is being searched.

    For `RelativeAncestor` selector, with `TypeSelector` targeting 'div' tag,

    Example
    -------
    >>> RelativeAncestor(TypeSelector("div"))

    when 'p' element is passed into find methods:

    Example
    -------
    >>> <div><p></p></div> ✔️
    >>> <div><a><p></p></a></div> ✔️
    >>> <span><p></p></span> ❌
    >>> <p></p><div></div> ❌

    Returns element only if it is an ancestor of the anchor element
    and matches the selector.

    Although this combinator does not have its counterpart in CSS, it can be
    represented as has selector, where descendant combinator is implied:

    Example
    -------
    >>> div:has(p)

    Where 'p' element is an anchor element passed to find methods and 'div' is
    the selector that is being searched among its ancestors.

    It can be created with Anchor instance as well with use of '<<' operator:

    Example
    -------
    >>> Anchor << TypeSelector("div")

    Which is equivalent to the first example and returns `RelativeAncestor` selector.

    Notes
    -------
    `RelativeAncestor` selector ignores `recursive` parameter,
    as it is always searches among all ancestors of the anchor element.
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
    >>> Anchor > TypeSelector("div")

    Creates a RelativeChild selector, that selects any div tag that is a direct
    child of the tag that is being searched.

    * `>>`: RelativeDescendant

    Example
    -------
    >>> Anchor >> TypeSelector("div")

    Creates a RelativeDescendant selector, that selects any div tag that is a descendant
    of the tag that is being searched. This is default behavior of selectors,
    and is equivalent to using the TypeSelector directly, but is implemented
    for the sake of consistency.

    * `+`: RelativeNextSibling

    Example
    -------
    >>> Anchor + TypeSelector("div")

    Creates a RelativeNextSibling selector, that selects any div tag that is next
    sibling of the tag that is being searched, it can logically return at most one tag.

    * `*`: RelativeSubsequentSibling

    Example
    -------
    >>> Anchor * TypeSelector("div")

    Creates a RelativeSubsequentSibling selector, that selects any div tag
    that is a subsequent sibling of the tag that is being searched.

    * `<`: RelativeParent

    Example
    -------
    >>> Anchor < TypeSelector("div")

    Creates a RelativeParent selector, that selects any div tag
    that is a parent of the tag that is being searched.

    * `<<`: RelativeAncestor

    Example
    -------
    >>> Anchor << TypeSelector("div")

    Creates a RelativeAncestor selector, that selects any div tag
    that is an ancestor of the tag that is being searched.

    This imitates css selector relative selectors that are used for example in
    :has pseudo-class, that accepts relative selector list as an argument.

    Example
    -------
    >>> :has(> div, + a)

    This translated to soupsavvy would be:

    Example
    -------
    >>> HasSelector(Anchor > TypeSelector("div"), Anchor + TypeSelector("a"))

    Which would match any tag that has a direct child 'div' and a next sibling 'a' tag.
    Selected tag is the anchor tag that is being searched.

    Notes
    -------
    For more information on relative selectors, see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_selectors/Selector_structure#relative_selector
    """

    def __gt__(self, x: SoupSelector) -> RelativeChild:
        return RelativeChild(check_selector(x))

    def __rshift__(self, x: SoupSelector) -> RelativeDescendant:
        return RelativeDescendant(check_selector(x))

    def __lt__(self, x: SoupSelector) -> RelativeParent:
        return RelativeParent(check_selector(x))

    def __lshift__(self, x: SoupSelector) -> RelativeAncestor:
        return RelativeAncestor(check_selector(x))

    def __add__(self, x: SoupSelector) -> RelativeSelector:
        return RelativeNextSibling(check_selector(x))

    def __mul__(self, x: SoupSelector) -> RelativeSelector:
        return RelativeSubsequentSibling(check_selector(x))


# instance of Anchor class with purpose to be used as a singleton
Anchor = _Anchor()


class HasSelector(CompositeSoupSelector):
    """
    Class representing elements selected with respect to matching reference elements.
    Element is selected if any of the provided selectors matched reference element.

    Example
    -------
    >>> HasSelector(TypeSelector("div"))

    matches all elements that have any descendant with "div" tag name.
    It uses default combinator of relative selector, which is descendant.

    Example
    -------
    >>> <span><div>Hello World</div></span> ✔️
    >>> <span><a>Hello World</a></span> ❌

    Other relative selectors can be used with Anchor element.

    Example
    -------
    >>> from soupsavvy.selectors.relative import Anchor
    >>> HasSelector(Anchor > TypeSelector("div"))
    >>> HasSelector(Anchor + TypeSelector("div"))

    or by using RelativeSelector components directly:

    Example
    -------
    >>> from soupsavvy.selectors.relative import RelativeChild, RelativeNextSibling
    >>> HasSelector(RelativeChild(TypeSelector("div")))
    >>> HasSelector(RelativeNextSibling(TypeSelector("div"))

    Example
    -------
    >>> <span><div>Hello World</div></span> ✔️
    >>> <span><a><div>Hello World</div></a></span> ❌

    In this case, HasSelector is anchored against any element, and matches only elements
    that have "div" tag name as a child.

    Object can be initialized with multiple selectors as well, in which case
    at least one selector must match for element to be included in the result.

    This is an equivalent of CSS :has() pseudo-class,
    that represents elements if any of the relative selectors that are passed as an argument
    match at least one element when anchored against this element.

    Example
    -------
    >>> :has(div, a) { color: red; }
    >>> :has(+ div, > a) { color: red; }

    These examples translated to soupsavvy would be:

    Example
    -------
    >>> from soupsavvy.selectors.relative import Anchor
    >>> HasSelector(TypeSelector("div"), TypeSelector("a"))
    >>> HasSelector(Anchor + TypeSelector("div"), Anchor > TypeSelector("a"))

    Notes
    -----
    Passing RelativeDescendant selector into HasSelector is equivalent to using
    its selector directly, as descendant combinator is default option.

    Example
    -------
    >>> HasSelector(RelativeDescendant(TypeSelector("div")))
    >>> HasSelector(Anchor > TypeSelector("div"))
    >>> HasSelector(TypeSelector("div"))

    Three of the above examples are equivalent.

    For more information on :has() pseudo-class see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/:has
    """

    def __init__(
        self,
        selector: SoupSelector,
        /,
        *selectors: SoupSelector,
    ) -> None:
        """
        Initializes AndSelector object with provided
        positional arguments as selectors.

        Parameters
        ----------
        selectors: SoupSelector
            SoupSelector objects to match accepted as positional arguments.
            At least one selector is required to create HasSelector.

        Raises
        ------
        NotSoupSelectorException
            If any of provided parameters is not an instance of SoupSelector.
        """
        super().__init__([selector, *selectors])

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:

        elements = TagIterator(tag, recursive=recursive)
        matching: list[Tag] = []

        for element in elements:
            # we only care if anything matching was found
            if any(step.find(element) for step in self.selectors):
                matching.append(element)

                if len(matching) == limit:
                    break

        return matching
