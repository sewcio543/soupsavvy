"""
Module with relative selectors and utility components.
They are used for selecting elements based on their relation to the anchor element.

Classes
-------
- `RelativeChild` - matches direct children of the anchor element
- `RelativeDescendant` - matches descendants of the anchor element
- `RelativeNextSibling` - matches next sibling of the anchor element
- `RelativeSubsequentSibling` - matches subsequent siblings of the anchor element
- `RelativeParent` - matches parent of the anchor element
- `RelativeAncestor` - matches ancestors of the anchor element
- `HasSelector` - selects elements based on matching reference elements
- `Anchor` - Anchor object for easily creating relative selectors
"""

from abc import abstractmethod
from typing import Optional

from soupsavvy.base import CompositeSoupSelector, SoupSelector, check_selector
from soupsavvy.interfaces import IElement
from soupsavvy.utils.selector_utils import TagIterator, TagResultSet


class RelativeSelector(SoupSelector):
    """
    Base class for relative selectors, that are used to find elements relative
    to the element that is being searched, which is considered an anchor.

    CSS definition of relative selectors state, that it is a selector representing
    an element relative to one or more anchor elements preceded by a combinator.

    In this use case, the anchor element is the element that is being searched,
    and the combinator is the logic of specific relative selector that is used.

    Example
    -------
    >>> selector = Anchor > TypeSelector("div")
    ... selector.find_all(tag)

    Uses `RelativeChild` selector to find any `div` tag that is a direct child of the
    tag that is being searched (passed as an argument).

    In css such selectors can be used for example in `:has` pseudo-class, where selector
    is anchored to the element:

    Example
    -------
    >>> :has(> div)

    Selects any element that has a direct child `div` tag.

    Notes
    -------
    Recursive parameter is ignored in relative selectors,
    as they have their own logic of searching the document.
    """

    def __init__(self, selector: SoupSelector) -> None:
        """
        Initializes RelativeSelector instance with specified selector.

        Parameters
        ----------
        selector : SoupSelector
            Selector that is used to find tags relative to the anchor element.
        """
        self._selector = check_selector(selector)

    @property
    def selector(self) -> SoupSelector:
        """
        Returns selector used to find elements relative to the anchor element
        in this relative selector.

        Returns
        -------
        SoupSelector
            Selector used for searching elements relative to the anchor element.
        """
        return self._selector

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
    searches for next sibling(s) of the anchor element.
    Child class needs to define:
    - '_limit' - class attribute to specify how many next siblings to search for.
    - '_func' - class attribute to specify which method to use for finding siblings.
    """

    @abstractmethod
    def _func(self, tag: IElement) -> list[IElement]:
        raise NotImplementedError(
            "Method '_func' needs to be implemented in child class."
        )

    def find_all(
        self,
        tag: IElement,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[IElement]:
        search = tag.find_ancestors()[0]
        # find all sibling tags that match the selector
        matching = TagResultSet(self.selector.find_all(search, recursive=False))
        siblings = TagResultSet(self._func(tag))
        # find intersection between two sets
        matches = matching & siblings
        return matches.fetch(limit)


class BaseAncestorSelector(RelativeSelector):
    """
    Base class with implementation for ancestor selectors,
    searches for ancestor(s) of the anchor element.
    Child class needs to define:
    - '_limit' - class attribute to specify how many ancestors to search for.
    """

    _limit: Optional[int]

    def find_all(
        self,
        tag: IElement,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[IElement]:
        limit = limit or self._limit
        # get max number of ancestors that can possibly be returned
        ancestors = tag.find_ancestors(limit=self._limit)

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
    Selector for finding direct children of the anchor element.

    Example
    -------
    >>> RelativeChild(TypeSelector("p"))

    when 'div' element is passed into find methods:

    Example
    -------
    >>> <div><p></p></div> ✔️
    >>> <div><a><p></p></a></div> ❌
    >>> <div><a></a></div> ❌

    It can be created with `Anchor` instance as well with use of `gt` operator `>`:

    Example
    -------
    >>> Anchor > TypeSelector("p")

    Notes
    -------
    Behavior of `RelativeChild` selector is equivalent to using find methods of
    selector with `recursive=False` and is implemented to support 'HasSelector'
    and `ChildCombinator` selectors.
    """

    def find_all(
        self,
        tag: IElement,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[IElement]:
        return self.selector.find_all(tag, recursive=False, limit=limit)


class RelativeDescendant(RelativeSelector):
    """
    Selector for finding descendants of the anchor element.

    Example
    -------
    >>> RelativeDescendant(TypeSelector("p"))

    when 'div' element is passed into find methods:

    Example
    -------
    >>> <div><p></p></div> ✔️
    >>> <div><a><p></p></a></div> ✔️
    >>> <div><a></a></div> ❌
    >>> <div></div><p></p> ❌

    It can be created with `Anchor` instance as well with use of `right shift` operator `>>`:

    Example
    -------
    >>> Anchor >> TypeSelector("p")

    Notes
    -------
    Behavior of `RelativeDescendant` selector is equivalent to using find methods of
    selector with default `recursive=True` and is implemented to support
    'HasSelector' and `DescendantCombinator` selectors.
    """

    def find_all(
        self,
        tag: IElement,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[IElement]:
        return self.selector.find_all(tag, recursive=True, limit=limit)


class RelativeNextSibling(BaseRelativeSibling):
    """
    Selector for finding next sibling of the anchor element.

    Example
    -------
    >>> RelativeNextSibling(TypeSelector("p"))

    when 'div' element is passed into find methods:

    Example
    -------
    >>> <div></div><p></p> ✔️
    >>> <div></div><a></a><p></p>  ❌
    >>> <p></p><div></div> ❌

    It can be created with `Anchor` instance as well with use of `plus` operator `+`:

    Example
    -------
    >>> Anchor + TypeSelector("p")
    """

    def _func(self, tag: IElement) -> list[IElement]:
        return tag.find_subsequent_siblings(limit=1)


class RelativeSubsequentSibling(BaseRelativeSibling):
    """
    Selector for finding subsequent siblings of the anchor element.

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

    It can be created with `Anchor` instance as well
    with use of `multiplication` operator `*`:

    Example
    -------
    >>> Anchor * TypeSelector("p")
    """

    def _func(self, tag: IElement) -> list[IElement]:
        return tag.find_subsequent_siblings(limit=None)


class RelativeParent(BaseAncestorSelector):
    """
    Selector for finding parent of the anchor element.

    Example
    -------
    >>> RelativeParent(TypeSelector("div"))

    when 'p' element is passed into find methods:

    Example
    -------
    >>> <div><p></p></div> ✔️
    >>> <div><a><p></p></a></div> ❌
    >>> <span><p></p></span> ❌

    Although this combinator does not have its counterpart in CSS, it can be
    represented as has selector, where child combinator is explicitly stated:

    Example
    -------
    >>> div:has(> p)

    It can be created with `Anchor` instance as well with use of `lt` operator `<`:

    Example
    -------
    >>> Anchor < TypeSelector("div")

    Notes
    -------
    `RelativeParent` selector ignores `recursive` parameter,
    as it is always searches only for parent of the anchor element,
    `find_all` method can return at most one element (parent).
    """

    _limit = 1


class RelativeAncestor(BaseAncestorSelector):
    """
    Selector for finding ancestors of the anchor element.

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


    Although this combinator does not have its counterpart in CSS, it can be
    represented as has selector, where descendant combinator is implied:

    Example
    -------
    >>> div:has(p)

    It can be created with `Anchor` instance as well with use of `left shift` operator `<<`:

    Example
    -------
    >>> Anchor << TypeSelector("div")

    Notes
    -------
    `RelativeAncestor` selector ignores `recursive` parameter,
    as it is always searches among all ancestors of the anchor element.
    """

    _limit = None


class Anchor_:
    """
    Shortcut component used to create relative selectors
    in a more readable way with use of operators.

    `Anchor_` is an internal class and can be considered a singleton.
    It's advisable to use the `Anchor` instance instead of creating new objects.

    `Anchor` supports the following operators:
    - `>`: `RelativeChild`

    Example
    -------
    >>> Anchor > TypeSelector("div")

    Creates `RelativeChild` selector, that selects any div tag that is a direct
    child of the tag that is being searched.

    - `>>`: `RelativeDescendant`

    Example
    -------
    >>> Anchor >> TypeSelector("div")

    Creates `RelativeDescendant` selector, that selects any div tag that is a descendant
    of the tag that is being searched. This is default behavior of selectors,
    and is equivalent to using the `TypeSelector` directly, but is implemented
    for the sake of consistency.

    - `+`: `RelativeNextSibling`

    Example
    -------
    >>> Anchor + TypeSelector("div")

    Creates `RelativeNextSibling` selector, that selects any div tag that is next
    sibling of the tag that is being searched, it can logically return at most one tag.

    - `*`: `RelativeSubsequentSibling`

    Example
    -------
    >>> Anchor * TypeSelector("div")

    Creates `RelativeSubsequentSibling` selector, that selects any div tag
    that is a subsequent sibling of the tag that is being searched.

    - `<`: `RelativeParent`

    Example
    -------
    >>> Anchor < TypeSelector("div")

    Creates `RelativeParent` selector, that selects any div tag
    that is a parent of the tag that is being searched.

    - `<<`: `RelativeAncestor`

    Example
    -------
    >>> Anchor << TypeSelector("div")

    Creates `RelativeAncestor` selector, that selects any div tag
    that is an ancestor of the tag that is being searched.

    This imitates css selector relative selectors that are used for example in
    `:has` pseudo-class, that accepts relative selector list as an argument.

    Example
    -------
    >>> :has(> div, + a)

    This translated to `soupsavvy` would be:

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


# instance of Anchor class
Anchor = Anchor_()


class HasSelector(CompositeSoupSelector):
    """
    Selector for finding elements based on matching reference elements.

    Example
    -------
    >>> HasSelector(TypeSelector("div"))

    matches all elements that have any descendant with "div" tag name.
    It uses default combinator of relative selector, which is descendant combinator.

    Example
    -------
    >>> <span><div>Hello World</div></span> ✔️
    >>> <span><a>Hello World</a></span> ❌

    Other relative selectors can be used with `Anchor` element.

    Example
    -------
    ... HasSelector(Anchor > TypeSelector("div"))
    ... HasSelector(Anchor + TypeSelector("div"))

    or by using `RelativeSelector` components directly:

    Example
    -------
    ... HasSelector(RelativeChild(TypeSelector("div")))
    ... HasSelector(RelativeNextSibling(TypeSelector("div"))

    Example
    -------
    >>> <span><div>Hello World</div></span> ✔️
    >>> <span><a><div>Hello World</div></a></span> ❌

    In this case, HasSelector is anchored against any element, and matches only elements
    that have "div" tag name as a child.

    This is an equivalent of CSS :has() pseudo-class,
    that matches element if any of the relative selectors that are passed as an argument
    match element when anchored against it.

    Example
    -------
    >>> :has(div, a)
    >>> :has(+ div, > a)

    These examples translated to `soupsavvy` would be:

    Example
    -------
    ... HasSelector(TypeSelector("div"), TypeSelector("a"))
    ... HasSelector(Anchor + TypeSelector("div"), Anchor > TypeSelector("a"))

    Notes
    -----
    Passing `RelativeDescendant` selector into HasSelector is equivalent to using
    its selector directly, as descendant combinator is a default option.

    Example
    -------
    >>> HasSelector(RelativeDescendant(TypeSelector("div")))
    ... HasSelector(Anchor > TypeSelector("div"))
    ... HasSelector(TypeSelector("div"))

    Three of the above examples are equivalent.

    For more information on :has() pseudo-class, see:

    https://developer.mozilla.org/en-US/docs/Web/CSS/:has
    """

    def __init__(
        self,
        selector: SoupSelector,
        /,
        *selectors: SoupSelector,
    ) -> None:
        """
        Initializes `HasSelector` object with provided positional arguments as selectors.

        Parameters
        ----------
        selectors: SoupSelector
            `SoupSelector` objects to match accepted as positional arguments.
            At least one selector is required to create `HasSelector`.

        Raises
        ------
        NotSoupSelectorException
            If any of provided parameters is not an instance of `SoupSelector`.
        """
        super().__init__([selector, *selectors])

    def find_all(
        self,
        tag: IElement,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[IElement]:

        elements = TagIterator(tag, recursive=recursive)
        matching: list[IElement] = []

        for element in elements:
            # we only care if anything matching was found
            if any(step.find(element) for step in self.selectors):
                matching.append(element)

                if len(matching) == limit:
                    break

        return matching
