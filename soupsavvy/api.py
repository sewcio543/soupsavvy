"""
This module is deprecated and will be removed in the future.
Use soupsavvy.operators module instead.
"""

import warnings

from soupsavvy.base import SoupSelector
from soupsavvy.selectors.logical import (
    AndSelector,
    NotSelector,
    SelectorList,
    XORSelector,
)
from soupsavvy.selectors.relative import HasSelector

warnings.warn(
    "soupsavvy.api module is deprecated, use soupsavvy.operators",
    DeprecationWarning,
)


def is_(
    selector1: SoupSelector,
    selector2: SoupSelector,
    /,
    *selectors: SoupSelector,
) -> SelectorList:
    """
    Returns an union of multiple soup selectors.
    Provides elements matching any of the selectors in the union.

    Parameters
    ----------
    selectors: SoupSelector
        SoupSelector objects to match accepted as positional arguments.
        At least two objects are required per SelectorList class requirements.

    Returns
    -------
    SelectorList
        SelectorList object that represents union of provided selectors.

    Example
    -------
    >>> is_(TypeSelector("h1"), TypeSelector("h2"))
    >>> where(TypeSelector("h1"), TypeSelector("h2"))

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
    For more information on selector list, see:

    https://developer.mozilla.org/en-US/docs/Web/CSS/:is

    https://developer.mozilla.org/en-US/docs/Web/CSS/:where

    https://developer.mozilla.org/en-US/docs/Web/CSS/Selector_list
    """
    return SelectorList(selector1, selector2, *selectors)


where = is_
or_ = is_


def not_(selector: SoupSelector, /, *selectors: SoupSelector) -> NotSelector:
    """
    Returns an negation of multiple soup selectors.
    NotSelector represents elements that do not match a list of selectors.

    Parameters
    ----------
    selectors: SoupSelector
        SoupSelector objects to negate match accepted as positional arguments.

    Returns
    -------
    NotSelector
        NotSelector object that represents negation of provided selectors.

    Example
    -------
    >>> not_(TypeSelector("div"), TypeSelector("a"))

    This is an equivalent of CSS :not() negation pseudo-class,
    that represents elements that do not match a list of selectors

    Example
    -------
    >>> :not(div, a) { color: red; }

    Notes
    -----
    For more information on selector list, see:

    https://developer.mozilla.org/en-US/docs/Web/CSS/:not
    """
    return NotSelector(selector, *selectors)


def and_(
    selector1: SoupSelector,
    selector2: SoupSelector,
    /,
    *selectors: SoupSelector,
) -> AndSelector:
    """
    Returns an intersection of multiple soup selectors.
    Element must match all of them to be selected.

    Parameters
    ----------
    selectors: SoupSelector
        SoupSelector objects to match accepted as positional arguments.
        At least two objects are required per AndSelector class requirements.

    Returns
    -------
    AndSelector
        AndSelector object that represents intersection of provided selectors.

    Example
    -------
    >>> and_(TypeSelector("div"), AttributeSelector(name="class", value="widget"))

    This is an equivalent of CSS selectors concatenation.

    Example
    -------
    >>> div.class1#id1 { color: red; }
    """
    return AndSelector(selector1, selector2, *selectors)


def has(
    selector: SoupSelector,
    /,
    *selectors: SoupSelector,
) -> HasSelector:
    """
    Returns HasSelector whose behavior imitate css :has() pseudo-class,
    that represents elements if any of the relative selectors that are passed as an argument
    match at least one element when anchored against this element.

    Parameters
    ----------
    selectors: SoupSelector
        SoupSelector objects to match accepted as positional arguments.
        At least two objects are required per AndSelector class requirements.

    Returns
    -------
    HasSelector
        HasSelector object that represents :has() pseudo-class behavior.

    Example
    -------
    >>> has_(TypeSelector("div"), TypeSelector("div"))

    This is an equivalent of CSS :has() pseudo-class:

    Example
    -------
    >>> :has(div, a) { color: red; }

    For now only default combinator (descendant) for 'relative' selectors is supported,
    so imitating css behavior of this kind is not possible yet.

    Example
    -------
    >>> :has(+ div, > a) { color: red; }

    Notes
    -----
    For more information on :has() pseudo-class, see:

    https://developer.mozilla.org/en-US/docs/Web/CSS/:has
    """
    return HasSelector(selector, *selectors)


def xor(
    selector1: SoupSelector,
    selector2: SoupSelector,
    /,
    *selectors: SoupSelector,
) -> XORSelector:
    """
    Returns an symmetric difference of multiple soup selectors.
    Element must match exactly one of them to be selected.

    Parameters
    ----------
    selectors: SoupSelector
        SoupSelector objects to match accepted as positional arguments.
        At least two objects are required per XORSelector class requirements.

    Returns
    -------
    XORSelector
        XORSelector object that represents symmetric difference of provided selectors.

    Example
    -------
    >>> xor(TypeSelector("div"), AttributeSelector(name="class", value="widget"))
    """
    return XORSelector(selector1, selector2, *selectors)
