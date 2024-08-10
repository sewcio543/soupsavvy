"""
Module for combinators defined in css.

They they combine other selectors in a way that gives them a useful relationship
to each other and the location of content in the document.

Soupsavvy provides combinators that are used to combine multiple SoupSelector
objects in a similar fashion to CSS combinators.

Classes
-------
ChildCombinator - equivalent of CSS child combinator (>)
NextSiblingCombinator - equivalent of CSS adjacent sibling combinator (+)
SubsequentSiblingCombinator - equivalent of CSS general sibling combinator (*)
DescentCombinator - equivalent of CSS descendant combinator (" ")
SelectorList - equivalent of CSS selector list (,) or :is() pseudo-class
OrSelector - alias for SelectorList

Notes
-----
For more information on CSS combinators see:
https://developer.mozilla.org/en-US/docs/Learn/CSS/Building_blocks/Selectors/Combinators
"""

from abc import abstractmethod
from functools import reduce
from typing import Optional, Type

from bs4 import Tag

from soupsavvy.selectors.base import CompositeSoupSelector, SoupSelector
from soupsavvy.selectors.relative import (
    RelativeChild,
    RelativeDescendant,
    RelativeNextSibling,
    RelativeSelector,
    RelativeSubsequentSibling,
)
from soupsavvy.selectors.tag_utils import TagIterator, TagResultSet


class BaseCombinator(CompositeSoupSelector):
    # order of selectors is relevant in context of results
    _ORDERED = True

    def __init__(
        self,
        selector1: SoupSelector,
        selector2: SoupSelector,
        /,
        *selectors: SoupSelector,
    ) -> None:
        """
        Initializes Combinator object with provided positional arguments.
        At least two SoupSelector object are required to create Combinator.

        Parameters
        ----------
        selectors: SoupSelector
            SoupSelector objects to match accepted as positional arguments.

        Notes
        -----
        Object can be initialized with more than two SoupSelector objects,
        which would be equal to chaining multiple combinators of the same type.

        For example, chaining child combinator in css:

        Example
        -------
        >>> div > a > span

        translated to soupsavvy would be:

        Example
        -------
        >>> ChildCombinator(TagSelector("div"), TagSelector("a"), TagSelector("span"))

        Raises
        ------
        NotSoupSelectorException
            If any of provided parameters is not an instance of SoupSelector.
        """
        super().__init__([selector1, selector2, *selectors])

    @property
    @abstractmethod
    def _selector(self) -> Type[RelativeSelector]:
        """
        Returns type of the relative selector that is used
        to perform a single step search in the combinator selector.

        Returns
        -------
        Type[RelativeSelector]
            Type of the relative selector that is used in the combinator.
            Selector instance of this type is initialized
            with each step in the combinator.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} is a base class "
            "and does not implement '_selector' property."
        )

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
        results = TagResultSet()

        for i, step in enumerate(self.selectors):
            if i == 0:
                # only first step follows recursive rule
                results |= TagResultSet(step.find_all(tag, recursive=recursive))
                continue

            if not results:
                break

            selector = self._selector(step)
            results = TagResultSet(
                reduce(
                    list.__add__,
                    # each relative selector has defined recursive behavior
                    (selector.find_all(element) for element in results.fetch()),
                )
            )

        # keep order of tags and limit
        results = TagResultSet(list(TagIterator(tag, recursive=True))) & results
        return results.fetch(limit)


class ChildCombinator(BaseCombinator):
    """
    Class representing a child combinator in CSS selectors.

    Example
    -------
    >>> ChildCombinator(TagSelector("div"), TagSelector("a"))

    matches all 'a' elements that are direct children of 'div' elements.

    Example
    -------
    >>> <div class="widget"><a>Hello World</a></div> ✔️
    >>> <div class="widget"><span></span><a>Hello World</a></div> ✔️
    >>> <span class="widget"><a>Hello World</a></span> ❌
    >>> <div class="menu"><span>Hello World</span></div> ❌

    Object can be created as well by using greater than operator '>'
    on two SoupSelector objects.

    Example
    -------
    >>> TagSelector("div") > TagSelector("a")

    Which is equivalent to the first example.

    This is an equivalent of CSS child combinator, that matches elements
    that are direct children of a specified element.

    Example
    -------
    >>> div.widget > a { color: red; }

    which translated to soupsavvy would be:

    Example
    -------
    >>> ChildCombinator(
    ...     TagSelector("div", attributes=[AttributeSelector("class", "widget")]),
    ...     TagSelector("a")
    ... )
    >>> TagSelector("div", attributes=[AttributeSelector("class", "widget")]) > TagSelector("a")

    Notes
    -----
    For more information on child combinator see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/Child_combinator
    """

    @property
    def _selector(self) -> Type[RelativeSelector]:
        return RelativeChild


class NextSiblingCombinator(BaseCombinator):
    """
    Class representing a next sibling combinator in CSS selectors.

    Example
    -------
    >>> NextSiblingCombinator(TagSelector("div"), TagSelector("a"))

    matches all 'a' elements that immediately follow 'div' elements,
    it means that both elements are children of the same parent element.

    Example
    -------
    >>> <div class="widget"></div><a>Hello World</a> ✔️
    >>> <div class="widget"><a>Hello World</a></div> ❌
    >>> <div class="widget"></div><span></span><a>Hello World</a> ❌

    Object can be created as well by using plus operator '+'
    on two SoupSelector objects.

    Example
    -------
    >>> div + a { color: red; }

    Which translated to soupsavvy would be:

    Example
    -------
    >>> NextSiblingCombinator(TagSelector("div"), TagSelector("a"))
    >>> TagSelector("div") + TagSelector("a")

    Notes
    -----
    For more information on next sibling combinator see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/Next-sibling_combinator

    This is also known as the adjacent sibling combinator.
    """

    @property
    def _selector(self) -> Type[RelativeSelector]:
        return RelativeNextSibling


class SubsequentSiblingCombinator(BaseCombinator):
    """
    Class representing a subsequent sibling combinator in CSS selectors.
    Subsequent sibling combinator separates two selectors
    and matches all instances of the second element that follow the first element
    (not necessarily immediately) and share the same parent element.

    Example
    -------
    >>> SubsequentSiblingCombinator(TagSelector("div"), TagSelector("a"))

    matches all 'a' elements that follow 'div' elements.

    Example
    -------
    >>> <div class="widget"></div><a>Hello World</a> ✔️
    >>> <div class="widget"><span></span><a>Hello World</a></div> ✔️
    >>> <span class="widget"><a>Hello World</a></span> ❌
    >>> <a>Hello World</a><div class="menu"></div> ❌

    Object can be created as well by using multiplication operator '*'
    on two SoupSelector objects, due to the lack of support for '~' operator
    between two operands.

    Example
    -------
    >>> div ~ a { color: red; }

    Which translated to soupsavvy would be:

    Example
    -------
    >>> TagSelector("div") * TagSelector("a")
    >>> SubsequentSiblingCombinator(TagSelector("div"), TagSelector("a"))

    Notes
    -----
    For more information on subsequent sibling combinator see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/Subsequent-sibling_combinator

    This is also known as the general sibling combinator.
    """

    @property
    def _selector(self) -> Type[RelativeSelector]:
        return RelativeSubsequentSibling


class DescendantCombinator(BaseCombinator):
    """
    Class representing a descent combinator in CSS selectors.
    Descent combinator separates two selectors and matches all instances
    of the second element that are descendants of the first element.

    Two SoupSelector objects are required to create DescentCombinator,
    but more can be provided as positional arguments, which binds them
    in a sequence of steps to match.

    Example
    -------
    >>> DescentCombinator(
    >>>     TagSelector("div", [AttributeSelector(name="class", value="menu")]),
    >>>     TagSelector("a", [AttributeSelector(name="href", value="google", re=True)])
    >>> )

    matches all descendants of 'div' element with 'menu' class attribute
    that are 'a' elements with href attribute containing 'google'.

    Example
    -------
    >>> <div class="menu"><a href="google.com"></a></div> ✔️
    >>> <div class="menu"><div><a href="google.com"></a></div></div> ✔️
    >>> <div class="menu"><a href="duckduckgo.com"></a></div> ❌
    >>> <div class="widget"><a href="google.com"></a></div> ❌
    >>> <a href="google.com"></a> ❌
    >>> <div class="widget"></div> ❌

    Object can be created as well by using right shift operator '>>'
    on two SoupSelector objects.

    Example
    -------
    >>> div a { color: red; }

    Which translated to soupsavvy would be:

    Example
    -------
    >>> TagSelector("div") >> TagSelector("a")
    >>> DescentCombinator(TagSelector("div"), TagSelector("a"))

    Notes
    -----
    For more information on subsequent sibling combinator see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/Descendant_combinator
    """

    @property
    def _selector(self) -> Type[RelativeSelector]:
        return RelativeDescendant


class SelectorList(CompositeSoupSelector):
    """
    Class representing a list of selectors in CSS,
    a selector list is a comma-separated list of selectors,
    that selects all the matching nodes.

    Class represents an Union of multiple soup selectors.
    Provides elements matching any of the selectors in an Union.

    At least two SoupSelector objects are required to create SelectorList,
    but more can be provided as positional arguments.

    Example
    -------
    >>> SelectorList(
    >>>     TagSelector("a"),
    >>>     TagSelector("div", [AttributeSelector(name="class", value="widget")])
    >>> )

    matches all elements that have "a" tag name OR 'class' attribute "widget".

    Example
    -------
    >>> <a>Hello World</a> ✔️
    >>> <div class="widget">Hello World</div> ✔️
    >>> <div>Hello Python</div> ❌

    This is an equivalent of CSS comma selector (selector list) or :is() selector.

    Example
    -------
    >>> h1, h1 { color: red;}
    >>> :is(h1, h2) { color: red; }

    This example translated to soupsavvy would be:

    Example
    -------
    >>> SoupUnionTag(TagSelector("h1"), TagSelector("h2"))
    >>> TagSelector("h1") | TagSelector("h2")

    Object can be created as well by using bitwise OR operator '|'
    on two SoupSelector objects.

    Example
    -------
    >>> TagSelector(tag="a") | TagSelector("div", [AttributeSelector(name="class", value="widget")])

    Which is equivalent to the first example.

    Notes
    -----
    This Combinator does not inherit from BaseCombinator,
    as its logic differs from other combinators.

    For more information on selector list see:
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
        Initializes SelectorList object with provided positional arguments.
        At least two SoupSelector objects are required to create SelectorList.

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
