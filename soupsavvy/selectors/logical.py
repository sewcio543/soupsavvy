"""
Module for selectors that represent logical operations on multiple selectors.
These selectors are used to create more complex selectors by combining
multiple selectors in a single object.

Classes
-------
AndSelector - intersection of multiple selectors
NotSelector - negation of a selector (~)
XORSelector - exclusive OR of multiple selectors
OrSelector - union of multiple selectors (|)
"""

from collections import Counter
from functools import reduce
from typing import Optional

from bs4 import Tag

from soupsavvy.selectors.base import CompositeSoupSelector, SoupSelector
from soupsavvy.selectors.combinators import SelectorList
from soupsavvy.selectors.tag_utils import TagIterator, TagResultSet, UniqueTag

# alias for SelectorList
OrSelector = SelectorList


class NotSelector(CompositeSoupSelector):
    """
    Class representing selector of elements that do not match provided selectors.

    Example
    -------
    >>> NotSelector(TagSelector(tag="div"))

    matches all elements that do not have "div" tag name.

    Example
    -------
    >>> <span> class="widget">Hello World</span> ✔️
    >>> <div class="menu">Hello World</div> ❌

    Object can be initialized with multiple selectors as well, in which case
    at least one selector must match for element to be excluded from the result.

    Object can be created as well by using bitwise NOT operator '~'
    on a SoupSelector object.

    Example
    -------
    >>> ~TagSelector(tag="div")

    Which is equivalent to the first example.

    This is an equivalent of CSS :not() negation pseudo-class,
    that represents elements that do not match a list of selectors

    Example
    -------
    >>> div:not(.widget) { color: red; }
    >>> :not(strong, .important) { color: red; }

    The second example translated to soupsavvy would be:

    Example
    -------
    >>> NotSelector(TagSelector("strong"), AttributeSelector("class", "important"))
    >>> ~(TagSelector("strong") | AttributeSelector("class", "important"))

    Notes
    -----
    For more information on :not() pseudo-class see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/:not
    """

    def __init__(
        self,
        selector: SoupSelector,
        /,
        *selectors: SoupSelector,
    ) -> None:
        """
        Initializes NotSelectors object with provided positional arguments as selectors.

        Parameters
        ----------
        selectors: SoupSelector
            SoupSelector objects to negate match accepted as positional arguments.
            At least one SoupSelector object is required to create NotSelector.

        Raises
        ------
        NotSoupSelectorException
            If any of provided parameters is not an instance of SoupSelector.
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
        the tag in case of single selector, or SoupUnionTag in case of multiple.
        """
        from soupsavvy.selectors.combinators import SelectorList

        if not self._multiple:
            return self.selectors[0]

        return SelectorList(*self.selectors)


class AndSelector(CompositeSoupSelector):
    """
    Class representing an intersection of multiple soup selectors.
    Provides elements matching all of the listed selectors.

    Example
    -------
    >>> AndTagSelector(
    ...    TagSelector(tag="div"),
    ...    AttributeSelector(name="class", value="widget")
    ... )

    matches all elements that have "div" tag name AND 'class' attribute "widget".

    Example
    -------
    >>> <div class="widget">Hello World</div> ✔️
    >>> <span class="widget">Hello World</span> ❌
    >>> <div class="menu">Hello World</div> ❌

    Object can be initialized with multiple selectors as well, in which case
    all selectors must match for element to be included in the result.

    Object can be created as well by using bitwise AND operator '&'
    on two SoupSelector objects.

    Example
    -------
    >>> TagSelector(tag="div") & AttributeSelector(name="class", value="widget")

    Which is equivalent to the first example.

    This is an equivalent of CSS selectors concatenation.

    Example
    -------
    >>> div.class1#id1 { color: red; }

    which translated to soupsavvy would be:

    Example
    -------
    >>> TagSelector("div") & AttributeSelector("class", "class1") & AttributeSelector("id", "id1")
    >>> TagSelector("div", attributes=[AttributeSelector("class", "class1"), AttributeSelector("id", "id1")])
    """

    def __init__(
        self,
        selector1: SoupSelector,
        selector2: SoupSelector,
        /,
        *selectors: SoupSelector,
    ) -> None:
        """
        Initializes AndTagSelector object with provided
        positional arguments as selectors.

        Parameters
        ----------
        selectors: SoupSelector
            SoupSelector objects to match accepted as positional arguments.
            At least two SoupSelector objects are required to create AndSelector.

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
    Class representing an exclusive OR of multiple soup selectors.
    Element is selected if it matches exactly one of the provided selectors.

    Example
    -------
    >>> XORSelector(TagSelector(tag="div"), AttributeSelector(class="widget"))

    Matches all elements that have either "div" tag name or 'class' attribute "widget".
    Elements with "div" tag name and 'class' attribute "widget" do not match selector.

    This is a shortcut for defining XOR operation between two selectors like this:

    Example
    -------
    >>> selector1 = TagSelector("div")
    ... selector2 = AttributeSelector("class", value="widget")
    ... xor = (selector1 & (~selector2)) | ((~selector1) & selector2)

    Object can be initialized with more then two selectors as well, in which case
    exactly one selector must match for element to be included in the result.
    """

    def __init__(
        self,
        selector1: SoupSelector,
        selector2: SoupSelector,
        /,
        *selectors: SoupSelector,
    ) -> None:
        """
        Initializes XORSelector object with provided positional arguments as selectors.

        Parameters
        ----------
        selectors: SoupSelector
            SoupSelector objects to match accepted as positional arguments.
            At least two selector are required to create XORSelector.

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
