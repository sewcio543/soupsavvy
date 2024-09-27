"""
Module for operators, which are alternative way to create composite selectors
by combining multiple of them in particular way.

Contains
--------
- `is_` - function to create `SelectorList` from multiple selectors
- `where` - alias for `is_`, no difference in behavior in scraping context
- `or_` - alias for `is_`, no difference in behavior in scraping context
- `not_` - function to create `NotSelector` from multiple selectors
- `and_` - function to create `AndSelector` from multiple selectors
- `has` - function to create `HasSelector` from multiple selectors
- `xor` - function to create `XORSelector` from multiple selectors

These utils do not brings extra functionality into the package, but they can be
used for convenience and readability in some cases.
"""

from soupsavvy.base import SoupSelector
from soupsavvy.selectors.logical import (
    AndSelector,
    NotSelector,
    SelectorList,
    XORSelector,
)
from soupsavvy.selectors.relative import HasSelector


def is_(
    selector1: SoupSelector,
    selector2: SoupSelector,
    /,
    *selectors: SoupSelector,
) -> SelectorList:
    """
    Returns an union of multiple soup selectors.

    Parameters
    ----------
    selectors: SoupSelector
         At least two `SoupSelector` objects to match accepted as positional arguments.

    Returns
    -------
    SelectorList
        `SelectorList` object that represents union of provided selectors.

    Example
    -------
    >>> is_(TypeSelector("h1"), TypeSelector("h2"))
    ... where(TypeSelector("h1"), TypeSelector("h2"))

    This is CSS counterpart of `selector list`, `:is()` or `:where` pseudo-classes.

    Example
    -------
    >>> h1, h1
    >>> :is(h1, h2)
    >>> :where(h1, h2)

    Aliases
    -------
    - `where` - to imitate css `:where` pseudo-class
    - `or_` - to imitate logical operator `or`

    Notes
    -----
    For more information on css counterparts, see:

    - https://developer.mozilla.org/en-US/docs/Web/CSS/:is
    - https://developer.mozilla.org/en-US/docs/Web/CSS/:where
    - https://developer.mozilla.org/en-US/docs/Web/CSS/Selector_list
    """
    return SelectorList(selector1, selector2, *selectors)


where = is_
or_ = is_


def not_(selector: SoupSelector, /, *selectors: SoupSelector) -> NotSelector:
    """
    Returns the negation of multiple soup selectors.

    Parameters
    ----------
    selectors: SoupSelector
        `SoupSelector` object(s) to negate match accepted as positional arguments.

    Returns
    -------
    NotSelector
        `NotSelector` object that represents negation of provided selector(s).

    Example
    -------
    >>> not_(TypeSelector("div"), TypeSelector("a"))


    This is the counterpart of CSS `:not()` negation pseudo-class,
    that represents elements that do not match a list of selectors.

    Example
    -------
    >>> :not(div, a)

    Notes
    -----
    For more information on `:not()` pseudo-class, see:

    - https://developer.mozilla.org/en-US/docs/Web/CSS/:not
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
        At least two `SoupSelector` objects to match accepted as positional arguments.

    Returns
    -------
    AndSelector
        `AndSelector` object that represents intersection of provided selectors.

    Example
    -------
    >>> and_(TypeSelector("div"), ClassSelector("widget"))

    This is the counterpart of CSS compound selector (selector concatenation):

    Example
    -------
    >>> div.widget

    Notes
    -----
    For more information on compound selectors, see:

    - https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_selectors/Selector_structure#compound_selector
    """
    return AndSelector(selector1, selector2, *selectors)


def has(
    selector: SoupSelector,
    /,
    *selectors: SoupSelector,
) -> HasSelector:
    """
    Returns `HasSelector`, whose behavior imitate css `:has()` pseudo-class,
    that represents elements if any of the relative selectors that are passed as an argument
    match at least one element when anchored against this element.

    Parameters
    ----------
    selectors: SoupSelector
        `SoupSelector` object(s) to match accepted as positional arguments.

    Returns
    -------
    HasSelector
        `HasSelector` object that represents `:has()` pseudo-class behavior.

    Example
    -------
    >>> has_(TypeSelector("div"), TypeSelector("a"))

    This is the counterpart of CSS `:has()` pseudo-class:

    Example
    -------
    >>> :has(div, a)

    Notes
    -----
    For more information on `:has()` pseudo-class, see:

    - https://developer.mozilla.org/en-US/docs/Web/CSS/:has
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
        At least two `SoupSelector` objects to match accepted as positional arguments.

    Returns
    -------
    XORSelector
       `XORSelector` object that represents symmetric difference of provided selectors.

    Example
    -------
    >>> xor(TypeSelector("div"), ClassSelector("widget"))

    This is a shortcut for defining `XOR` operation between two selectors like this:

    Example
    -------
    >>> selector1 = TypeSelector("div")
    ... selector2 = ClassSelector("widget")
    ... xor = (selector1 & (~selector2)) | ((~selector1) & selector2)
    """
    return XORSelector(selector1, selector2, *selectors)
