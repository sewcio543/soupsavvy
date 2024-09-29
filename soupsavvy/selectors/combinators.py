"""
Module with combinators, which are composite selectors, that define a relationship
between multiple selectors related to their position in the document.

Most of them are counterpart of CSS combinators, but others extend their functionality.

Classes
-------
- `ChildCombinator` - counterpart of CSS child combinator (>)
- `NextSiblingCombinator` - counterpart of CSS adjacent sibling combinator (+)
- `SubsequentSiblingCombinator` - counterpart of CSS subsequent sibling combinator (*)
- `DescentCombinator` - counterpart of CSS descendant combinator (" ")
- `ParentCombinator` - matches parent of preceding selector
- `AncestorCombinator` - matches ancestor of preceding selector

Notes
-----
For more information on CSS combinators, see:

https://developer.mozilla.org/en-US/docs/Learn/CSS/Building_blocks/Selectors/Combinators
"""

from abc import abstractmethod
from functools import reduce
from typing import Optional, Type

from bs4 import Tag
from typing_extensions import deprecated

from soupsavvy.base import CompositeSoupSelector, SoupSelector
from soupsavvy.selectors.logical import SelectorList as _SelectorList
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


@deprecated("`SelectorList` was moved to `soupsavvy.selectors.logical` module.")
class SelectorList(_SelectorList): ...


class BaseCombinator(CompositeSoupSelector):
    """
    Base class for all combinators, which are composite selectors,
    that defined a relationship between multiple selectors and apply it to search
    for elements in the document.
    """

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
        At least two `SoupSelector` object are required to create Combinator.

        Parameters
        ----------
        selectors: SoupSelector
            `SoupSelector` objects to match accepted as positional arguments.

        Notes
        -----
        Object can be initialized with more than two `SoupSelector` objects,
        which would be equal to chaining multiple combinators of the same type.

        For example, chaining child combinator in css:

        Example
        -------
        >>> div > a > span

        translated to `soupsavvy` would be:

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

    - Elements that match first step can be found
    anywhere in the tree, regardless of `recursive` parameter.
    - Final results should contain only children of element if `recursive` is False.
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
    Counterpart of CSS child combinator.
    Represents the relationship between selectors, where every next matching element
    is a direct child of the previous one.

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

    Object can be created as well by using `greater than` operator '>'
    on `SoupSelector` objects.

    Example
    -------
    >>> TypeSelector("div") > TypeSelector("a")

    Which is equivalent to the first example.

    CSS counterpart can be represented as:

    Example
    -------
    >>> div > a { color: red; }

    Notes
    -----
    For more information on child combinator, see:

    https://developer.mozilla.org/en-US/docs/Web/CSS/Child_combinator
    """

    @property
    def _selector(self) -> Type[RelativeSelector]:
        return RelativeChild


class NextSiblingCombinator(BaseCombinator):
    """
    Counterpart of CSS next sibling combinator.
    Represents the relationship between selectors, where every next matching element
    is a sibling immediately following the previous one.

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

    Object can be created as well by using `plus` operator '+` on `SoupSelector` objects.

    Example
    -------
    >>> TypeSelector("div") + TypeSelector("a")

    Which is equivalent to the first example.

    CSS counterpart can be represented as:

    Example
    -------
    >>> div + a

    Notes
    -----
    This is also known as the `adjacent sibling combinator` in CSS.
    For more information on next sibling combinator, see:

    https://developer.mozilla.org/en-US/docs/Web/CSS/Next-sibling_combinator
    """

    @property
    def _selector(self) -> Type[RelativeSelector]:
        return RelativeNextSibling


class SubsequentSiblingCombinator(BaseCombinator):
    """
    Counterpart of CSS subsequent sibling combinator.
    Represents the relationship between selectors, where every next matching element
    is a sibling following the previous one, but not necessarily immediately.

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

    Object can be created as well by using `multiplication` operator '*'
    on `SoupSelector` objects.

    Example
    -------
    >>> TypeSelector("div") * TypeSelector("a")

    CSS counterpart can be represented as:

    Example
    -------
    >>> div ~ a

    Notes
    -----
    This combinator is also known as `general sibling combinator` in CSS.
    For more information on subsequent sibling combinator, see:

    https://developer.mozilla.org/en-US/docs/Web/CSS/Subsequent-sibling_combinator
    """

    @property
    def _selector(self) -> Type[RelativeSelector]:
        return RelativeSubsequentSibling


class DescendantCombinator(BaseCombinator):
    """
    Counterpart of CSS descendant combinator.
    Represents the relationship between selectors, where every next matching element
    is a descendant of the previous one.

    Example
    -------
    >>> DescentCombinator(TypeSelector("div"), ClassSelector("widget"))

    matches all descendants of 'div' element with 'widget' class.

    Example
    -------
    >>> <div><a class="widget"></a></div> ✔️
    >>> <div><div><a class="widget"></a></div></div> ✔️
    >>> <div><a id="widget"></a></div> ❌
    >>> <span><a class="widget"></a></span> ❌
    >>> <a class="widget"></a> ❌

    Object can be created as well by using `right shift` operator '>>'
    on `SoupSelector` objects.

    Example
    -------
    >>> TypeSelector("div") >> ClassSelector("widget")

    CSS counterpart can be represented as:

    Example
    -------
    >>> div .widget

    Notes
    -----
    For more information on subsequent sibling combinator, see:

    https://developer.mozilla.org/en-US/docs/Web/CSS/Descendant_combinator
    """

    @property
    def _selector(self) -> Type[RelativeSelector]:
        return RelativeDescendant


class ParentCombinator(BaseAncestorCombinator):
    """
    Defines a relationship between selectors, where every next matching element
    is a parent of the previous one.

    Example
    -------
    >>> ParentCombinator(TypeSelector("a"), TypeSelector("div"))

    The given selector matches all 'div' elements that are parents of 'a' elements.

    Example
    -------
    >>> <div><a href="/shop"></a></div> ✔️
    >>> <div><span><div><a href="/shop"></a></span></div> ❌
    >>> <span><a href="/shop"></a></span> ❌

    Object can be created as well by using `lt` operator '<' on `SoupSelector` objects.

    Example
    -------
    >>> TypeSelector("a") < TypeSelector("div")

    Although this combinator does not have its counterpart in CSS, it can be represented as:

    Example
    -------
    >>> div:has(> a)
    """

    @property
    def _selector(self) -> Type[RelativeSelector]:
        return RelativeParent


class AncestorCombinator(BaseAncestorCombinator):
    """
    Defines a relationship between selectors, where every next matching element
    is an ancestor of the previous one.

    Example
    -------
    >>> AncestorCombinator(TypeSelector("a"), TypeSelector("div"))

    The given selector matches all 'div' elements that are ancestors of 'a' elements.

    Example
    -------
    >>> <div><span><a href="/shop"></a></span></div> ✔️
    >>> <div><a href="/shop"></a></div> ✔️
    >>> <div><span class="menu"></span>/div> ❌
    >>> <span><a class="menu"></span>/div> ❌

    Object can be created as well by using `left shift` operator '<<'
    on `SoupSelector` objects.

    Example
    -------
    >>> TypeSelector("a") << TypeSelector("div")

    Although this combinator does not have its counterpart in CSS, it can be represented as:

    Example
    -------
    >>> div:has(a)
    """

    @property
    def _selector(self) -> Type[RelativeSelector]:
        return RelativeAncestor
