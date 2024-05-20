"""
Module for css selectors API and not only.
Imitate css some pseudo-classes behavior done on soupsavvy selectors.

Contains:

* is_: function to create SelectorList from list of selectors
* where: alias for is_, no difference in behavior in scraping context
* not_: function to create NotSelector from list of selectors
* and_: function to create AndSelector from list of selectors
* has: ...

There is not similar functionality in css for AndSelector expect for selector concatenation,
and_ is more to have and alternative way to create AndSelector for soupsavvy selectors.

These utils do not brings extra functionality into the package, but they can be
used for convenience and readability in some cases.
"""

from soupsavvy.tags.base import SelectableSoup
from soupsavvy.tags.combinators import DescendantCombinator, SelectorList
from soupsavvy.tags.components import AndSelector, NotSelector


def is_(
    selector1: SelectableSoup,
    selector2: SelectableSoup,
    /,
    *selectors: SelectableSoup,
) -> SelectorList:
    """
    Returns an union of multiple soup selectors.
    Provides elements matching any of the selectors in the union.

    Parameters
    ----------
    selectors: SelectableSoup
        SelectableSoup objects to match accepted as positional arguments.
        At least two objects are required per SelectorList class requirements.

    Example
    -------
    >>> is_(ElementTag("h1"), ElementTag("h2"))
    >>> where(ElementTag("h1"), ElementTag("h2"))

    This is an equivalent of CSS comma selector (selector list) or :is() selector.
    Function is also aliased by 'where' function that imitate css :where pseudo-class.
    In css the main difference is their specificity, but in this context they are the same.

    Example
    -------
    >>> h1, h1 { color: red;}
    >>> :is(h1, h2) { color: red; }
    >>> :where(h1, h2) { color: red; }

    Notes
    -----
    For more information on selector list see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/:is
    https://developer.mozilla.org/en-US/docs/Web/CSS/:where
    https://developer.mozilla.org/en-US/docs/Web/CSS/Selector_list
    """
    return SelectorList(selector1, selector2, *selectors)


where = is_


def not_(selector: SelectableSoup, /, *selectors: SelectableSoup) -> NotSelector:
    """
    Returns an negation of multiple soup selectors.
    NotSelector represents elements that do not match a list of selectors.

    Parameters
    ----------
    selectors: SelectableSoup
        SelectableSoup objects to negate match accepted as positional arguments.

    Example
    -------
    >>> not_(TagSelector(tag="div"), TagSelector(tag="a"))

    This is an equivalent of CSS :not() negation pseudo-class,
    that represents elements that do not match a list of selectors

    Example
    -------
    >>> :not(div, a) { color: red; }

    Notes
    -----
    For more information on selector list see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/:not
    """
    return NotSelector(selector, *selectors)


def and_(
    selector1: SelectableSoup,
    selector2: SelectableSoup,
    /,
    *selectors: SelectableSoup,
) -> AndSelector:
    """
    Returns an intersection of multiple soup selectors.
    Element must match all of them to be selected.

    Parameters
    ----------
    selectors: SelectableSoup
        SelectableSoup objects to match accepted as positional arguments.
        At least two objects are required per AndSelector class requirements.

    Example
    -------
    >>> and_(TagSelector(tag="div"), AttributeSelector(name="class", value="widget"))

    This is an equivalent of CSS selectors concatenation.

    Example
    -------
    >>> div.class1#id1 { color: red; }
    """
    return AndSelector(selector1, selector2, *selectors)


#! TODO has selector
# described in https://developer.mozilla.org/en-US/docs/Web/CSS/:has
def has(
    selector1: SelectableSoup,
    selector2: SelectableSoup,
    /,
    *selectors: SelectableSoup,
): ...
