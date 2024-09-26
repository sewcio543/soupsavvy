"""
Module with selectors that represent logical operations on multiple selectors.

Classes
-------
- `AndSelector` - intersection of multiple selectors (&)
- `NotSelector` - negation of a selector (~)
- `XORSelector` - exclusive OR of multiple selectors
- `SelectorList` - counterpart of CSS selector list or :is() pseudo-class (|)
- `OrSelector` - union of multiple selectors - alias of `SelectorList` (|)
"""

from collections import Counter
from functools import reduce
from typing import Optional

from bs4 import Tag

from soupsavvy.base import CompositeSoupSelector, SoupSelector
from soupsavvy.utils.selector_utils import TagIterator, TagResultSet, UniqueTag


class SelectorList(CompositeSoupSelector):
    """
    Counterpart of CSS selector list.
    At least one selector from list must match the element to be included.

    Example
    -------
    >>> SelectorList(TypeSelector("a"), AttributeSelector(name="class", value="widget"))

    matches all elements that have "a" tag name OR 'class' attribute "widget".

    Example
    -------
    >>> <a>Hello World</a> ✔️
    >>> <div class="widget">Hello World</div> ✔️
    >>> <div>Hello Python</div> ❌

    Object can be created as well by using `pipe` operator '|' on `SoupSelector` objects.

    Example
    -------
    >>> TypeSelector("a") | ClassSelector("widget")

    CSS counterpart can be represented as:

    Example
    -------
    >>> a, .widget
    >>> :is(a, .widget)

    Notes
    -----
    For more information on selector list, see:

    https://developer.mozilla.org/en-US/docs/Web/CSS/Selector_list
    """

    def __init__(
        self,
        selector1: SoupSelector,
        selector2: SoupSelector,
        /,
        *selectors: SoupSelector,
    ) -> None:
        """
        Initializes `SelectorList` object with provided positional arguments.
        At least two `SoupSelector` objects are required to create `SelectorList`.

        Parameters
        ----------
        selectors: SoupSelector
            SoupSelector objects to match accepted as positional arguments.

        Raises
        ------
        NotSoupSelectorException
            If any of provided parameters is not an instance of SoupSelector.
        """
        super().__init__([selector1, selector2, *selectors])

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
        results = TagResultSet()

        for selector in self.selectors:
            results |= TagResultSet(
                selector.find_all(tag, recursive=recursive),
            )

        # keep order of tags and limit
        results = TagResultSet(list(TagIterator(tag, recursive=recursive))) & results
        return results.fetch(limit)


# alias of `SelectorList`
OrSelector = SelectorList


class NotSelector(CompositeSoupSelector):
    """
    Selector for finding elements that do not match provided selector(s).
    Counterpart of CSS :not() pseudo-class.

    Example
    -------
    >>> NotSelector(TypeSelector("div"))

    matches all elements that do not have "div" tag name.

    Example
    -------
    >>> <span> class="widget">Hello World</span> ✔️
    >>> <div class="menu">Hello World</div> ❌

    Object can be created as well by using `bitwise NOT` operator '~'
    on `SoupSelector` object.

    Example
    -------
    >>> ~TypeSelector("div")

    Which is equivalent to the first example.

    This is CSS counterpart of :not() pseudo-class.

    Example
    -------
    >>> :not(div)

    Notes
    -----
    For more information on :not() pseudo-class, see:

    https://developer.mozilla.org/en-US/docs/Web/CSS/:not
    """

    def __init__(
        self,
        selector: SoupSelector,
        /,
        *selectors: SoupSelector,
    ) -> None:
        """
        Initializes `NotSelectors` object with provided positional arguments as selectors.

        Parameters
        ----------
        selectors: SoupSelector
            `SoupSelector` objects to negate match accepted as positional arguments.
            At least one `SoupSelector` object is required to create `NotSelector`.

        Raises
        ------
        NotSoupSelectorException
            If any of provided parameters is not an instance of `SoupSelector`.
        """
        self._multiple = bool(selectors)
        super().__init__([selector, *selectors])

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
        matching = reduce(
            TagResultSet.__or__,
            (
                TagResultSet(step.find_all(tag, recursive=recursive))
                for step in self.selectors
            ),
        )
        all_tags = list(TagIterator(tag, recursive=recursive))
        result = TagResultSet(all_tags) - matching
        return result.fetch(limit)

    def __invert__(self) -> SoupSelector:
        """
        Overrides __invert__ method to cancel out negation by returning
        the tag in case of single selector, or `SelectorList` in case of multiple.
        """
        if not self._multiple:
            return self.selectors[0]

        return SelectorList(*self.selectors)


class AndSelector(CompositeSoupSelector):
    """
    Selector representing an intersection of multiple selectors,
    where element must be matched by all provided selectors.
    Counterpart of CSS compound selector.

    Example
    -------
    >>> AndSelector(TypeSelector("div"), ClassSelector("widget"))

    matches all elements that have "div" tag name AND 'class' attribute "widget".

    Example
    -------
    >>> <div class="widget">Hello World</div> ✔️
    >>> <span class="widget">Hello World</span> ❌
    >>> <div class="menu">Hello World</div> ❌

    Object can be created as well by using `bitwise AND` operator '&'
    on `SoupSelector` objects.

    Example
    -------
    >>> TypeSelector("div") & ClassSelector("widget")

    CSS counterpart can be represented as:

    Example
    -------
    >>> div.widget

    Notes
    -----
    For more information on compound selectors ,see:

    https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_selectors/Selector_structure#compound_selector
    """

    def __init__(
        self,
        selector1: SoupSelector,
        selector2: SoupSelector,
        /,
        *selectors: SoupSelector,
    ) -> None:
        """
        Initializes `AndSelector` object with provided
        positional arguments as selectors.

        Parameters
        ----------
        selectors: SoupSelector
            `SoupSelector` objects to match accepted as positional arguments.
            At least two `SoupSelector` objects are required to create `AndSelector`.

        Raises
        ------
        NotSoupSelectorException
            If any of provided parameters is not an instance of `SoupSelector`.
        """
        super().__init__([selector1, selector2, *selectors])

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
        matching = reduce(
            TagResultSet.__and__,
            (
                TagResultSet(step.find_all(tag, recursive=recursive))
                for step in self.selectors
            ),
        )
        return matching.fetch(limit)


class XORSelector(CompositeSoupSelector):
    """
    Selector representing an exclusive OR of multiple selectors,
    where element must be matched by exactly one of them.

    Example
    -------
    >>> XORSelector(TypeSelector("div"), ClassSelector("widget"))

    Matches all elements that have either "div" tag name or 'class' attribute "widget".
    Elements with both "div" tag name and 'class' attribute "widget" do not match selector.

    This is a shortcut for defining XOR operation between two selectors like this:

    Example
    -------
    >>> selector1 = TypeSelector("div")
    ... selector2 = AttributeSelector("class", value="widget")
    ... xor = (selector1 & (~selector2)) | ((~selector1) & selector2)
    """

    def __init__(
        self,
        selector1: SoupSelector,
        selector2: SoupSelector,
        /,
        *selectors: SoupSelector,
    ) -> None:
        """
        Initializes `XORSelector` object with provided positional arguments as selectors.

        Parameters
        ----------
        selectors: SoupSelector
            `SoupSelector` objects to match accepted as positional arguments.
            At least two selector are required to create `XORSelector`.

        Raises
        ------
        NotSoupSelectorException
            If any of provided parameters is not an instance of `SoupSelector`.
        """
        super().__init__([selector1, selector2, *selectors])

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
        unique = (
            UniqueTag(element)
            for step in self.selectors
            for element in step.find_all(tag, recursive=recursive)
        )
        results = TagResultSet(
            [element.tag for element, count in Counter(unique).items() if count == 1]
        )
        # keep order of tags and limit
        results = TagResultSet(list(TagIterator(tag, recursive=recursive))) & results
        return results.fetch(limit)
