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
ParentCombinator - matches parent of preceding selector
AncestorCombinator - matches ancestor of preceding selector

Notes
-----
For more information on CSS combinators see:
https://developer.mozilla.org/en-US/docs/Learn/CSS/Building_blocks/Selectors/Combinators
"""

from abc import abstractmethod
from functools import reduce
from typing import Optional, Type

from bs4 import Tag

from soupsavvy.base import CompositeSoupSelector, SoupSelector
from soupsavvy.selectors.relative import (
    RelativeAncestor,
    RelativeChild,
    RelativeDescendant,
    RelativeNextSibling,
    RelativeParent,
    RelativeSelector,
    RelativeSubsequentSibling,
)
from soupsavvy.utils.selector_utils import TagIterator, TagResultSet


class BaseCombinator(CompositeSoupSelector):
    # order of selectors is relevant in context of results
    COMMUTATIVE = False

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
        >>> ChildCombinator(TypeSelector("div"), TypeSelector("a"), TypeSelector("span"))

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

    def _find_first_step(
        self, step: SoupSelector, tag: Tag, recursive: bool
    ) -> TagResultSet:
        """
        Returns results of the first step in the combinator selector,
        given Tag object that is being searched and recursive behavior
        passed to find method by user.

        Parameters
        ----------
        tag: Tag
            Tag object that's being searched by first step in the combinator.
        recursive: bool
            Recursive behavior passed to find method by user.

        Returns
        -------
        TagResultSet
            Results of the first step in the combinator selector.
        """
        return TagResultSet(step.find_all(tag, recursive=recursive))

    def _order_results(
        self, results: TagResultSet, tag: Tag, recursive: bool
    ) -> TagResultSet:
        """
        Orders results of find_all method of the combinator selector, given
        initial Tag object that was passed to find_all method and recursive behavior.

        Parameters
        ----------
        results: TagResultSet
            Results of the combinator selector.
        tag: Tag
            Initial Tag object that was passed to find_all method.
        recursive: bool
            Recursive behavior passed to find method by user.

        Returns
        -------
        TagResultSet
            Ordered results of the combinator selector.
        """
        return TagResultSet(list(TagIterator(tag, recursive=True))) & results

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
        results = TagResultSet()

        for i, step in enumerate(self.selectors):
            if i == 0:
                results |= self._find_first_step(
                    step=step, tag=tag, recursive=recursive
                )
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

        results = self._order_results(results=results, tag=tag, recursive=recursive)
        return results.fetch(limit)


class BaseAncestorCombinator(BaseCombinator):
    """
    Base class for ancestor combinators, that are specific type of combinators,
    unlike other combinators, they move up the tree of elements, rather than down
    after finding first step.

    * Elements that match first step can be found
    anywhere in the tree, regardless of `recursive` parameter.
    * Final results should contain only children if `recursive` is False.
    """

    def _find_first_step(
        self, step: SoupSelector, tag: Tag, recursive: bool
    ) -> TagResultSet:
        # always look for all descendants in first step
        return TagResultSet(step.find_all(tag, recursive=True))

    def _order_results(
        self, results: TagResultSet, tag: Tag, recursive: bool
    ) -> TagResultSet:
        # respect recursive parameter while ordering results
        return TagResultSet(list(TagIterator(tag, recursive=recursive))) & results


class ChildCombinator(BaseCombinator):
    """
    Class representing a child combinator in CSS selectors.

    Example
    -------
    >>> ChildCombinator(TypeSelector("div"), TypeSelector("a"))

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
    >>> TypeSelector("div") > TypeSelector("a")

    Which is equivalent to the first example.

    This is an equivalent of CSS child combinator, that matches elements
    that are direct children of a specified element.

    Example
    -------
    >>> .widget > a { color: red; }

    which translated to soupsavvy would be:

    Example
    -------
    >>> ChildCombinator(
    ...     AttributeSelector("class", "widget"),
    ...     TypeSelector("a")
    ... )

    or with use of `>` operator:

    Example
    -------
    >>> AttributeSelector("class", "widget") > TypeSelector("a")

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
    >>> NextSiblingCombinator(TypeSelector("div"), TypeSelector("a"))

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
    >>> NextSiblingCombinator(TypeSelector("div"), TypeSelector("a"))
    >>> TypeSelector("div") + TypeSelector("a")

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
    >>> SubsequentSiblingCombinator(TypeSelector("div"), TypeSelector("a"))

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
    >>> TypeSelector("div") * TypeSelector("a")
    >>> SubsequentSiblingCombinator(TypeSelector("div"), TypeSelector("a"))

    Notes
    -----
    For more information on subsequent sibling combinator see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/Subsequent-sibling_combinator

    This combinator is also known as `general sibling combinator`
    or `adjacent sibling combinator`.
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
    >>>     TypeSelector("div"),
    >>>     AttributeSelector(name="href", value="google.com")
    >>> )

    matches all descendants of 'div' element
    that have href attribute equal to 'google.com'.

    Example
    -------
    >>> <div><a href="google.com"></a></div> ✔️
    >>> <div><div><a href="google.com"></a></div></div> ✔️
    >>> <div><a href="duckduckgo.com"></a></div> ❌
    >>> <span><a href="google.com"></a></span> ❌
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
    >>> TypeSelector("div") >> TypeSelector("a")
    >>> DescentCombinator(TypeSelector("div"), TypeSelector("a"))

    Notes
    -----
    For more information on subsequent sibling combinator see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/Descendant_combinator
    """

    @property
    def _selector(self) -> Type[RelativeSelector]:
        return RelativeDescendant


class ParentCombinator(BaseAncestorCombinator):
    """
    Parent combinator separates two selectors and matches all instances
    of the second element that are parents of the first element.

    Two `SoupSelector` objects are required to create ParentCombinator,
    but more can be provided as positional arguments, which binds them
    in a sequence of steps to match.

    Example
    -------
    >>> ParentCombinator(
    ...     TypeSelector("a"),
    ...     AttributeSelector("class", "menu"),
    ...     TypeSelector("div"),
    ... )

    The given selector would first look for 'a' elements, then find elements with
    'menu' class that are parents of 'a' elements, and finally find 'div' elements
    that are parents of 'menu' elements.

    Example
    -------
    >>> <div><span class="menu"><a href="/shop"></a></span></div> ✔️
    >>> <div><span class="menu"><div><a href="/shop"></a></div></span></div> ❌
    >>> <div><a href="/shop"></a><span class="menu"></span></div> ❌
    >>> <div><a href="/shop"></a></span></div> ❌

    It is equivalent to using `HasSelector` with child combinator and narrowing
    down results to `div` types with `TypeSelector`.

    Example
    -------
    >>> HasSelector(
    ...     Anchor > AttributeSelector("class", "menu") > TypeSelector("a")
    ... ) & TypeSelector("div")

    Although this combinator does not have its counterpart in CSS, it can be
    represented as:

    Example
    -------
    >>> div:has(> .menu > a)

    Object can be created as well by using lt operator '<'
    on two SoupSelector objects.

    Example
    -------
    >>> div:has(> a) { color: red; }

    Which translated to soupsavvy would be:

    Example
    -------
    >>> TypeSelector("a") < TypeSelector("div")
    >>> ParentCombinator(TypeSelector("a"), TypeSelector("div"))
    """

    @property
    def _selector(self) -> Type[RelativeSelector]:
        return RelativeParent


class AncestorCombinator(BaseAncestorCombinator):
    """
    Ancestor combinator separates two selectors and matches all instances
    of the second element that are ancestors of the first element.

    Two `SoupSelector` objects are required to create AncestorCombinator,
    but more can be provided as positional arguments, which binds them
    in a sequence of steps to match.

    Example
    -------
    >>> AncestorCombinator(
    ...     TypeSelector("a"),
    ...     AttributeSelector("class", "menu"),
    ...     TypeSelector("div"),
    ... )

    The given selector would first look for 'a' elements, then find elements with
    'menu' class that are ancestors of 'a' elements, and finally find 'div' elements
    that are ancestors of 'menu' elements.

    Example
    -------
    >>> <div><span class="menu"><a href="/shop"></a></span></div> ✔️
    >>> <div><span class="menu"><div><a href="/shop"></a></div></span></div> ✔️
    >>> <div><a href="/shop"></a><span class="menu"></span></div> ❌
    >>> <div><a href="/shop"></a></span></div> ❌

    It is equivalent to using `HasSelector` with (default) descendant combinator
    and narrowing down results to `div` types with `TypeSelector`.

    Example
    -------
    >>> HasSelector(
    ...     AttributeSelector("class", "menu") > TypeSelector("a")
    ... ) & TypeSelector("div")

    Although this combinator does not have its counterpart in CSS, it can be
    represented as has selector, where descendant combinator is implied:

    Example
    -------
    >>> div:has(.menu a)

    Object can be created as well by using left shift operator '<<'
    on two SoupSelector objects.

    Example
    -------
    >>> div:has(a) { color: red; }

    Which translated to soupsavvy would be:

    Example
    -------
    >>> TypeSelector("a") << TypeSelector("div")
    >>> AncestorCombinator(TypeSelector("a"), TypeSelector("div"))
    """

    @property
    def _selector(self) -> Type[RelativeSelector]:
        return RelativeAncestor


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
    >>>     TypeSelector("a"),
    >>>     TypeSelector("div", [AttributeSelector(name="class", value="widget")])
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
    >>> SoupUnionTag(TypeSelector("h1"), TypeSelector("h2"))
    >>> TypeSelector("h1") | TypeSelector("h2")

    Object can be created as well by using bitwise OR operator '|'
    on two SoupSelector objects.

    Example
    -------
    >>> TypeSelector("a") | TypeSelector("div", [AttributeSelector(name="class", value="widget")])

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
