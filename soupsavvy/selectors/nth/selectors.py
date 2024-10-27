"""
Module provides `nth-of-type` selector implementations for `SoupSelector`.
It allows you to search for the nth occurrence of an element,
similar to how the CSS `nth-of-type` pseudo-class works.
However, instead of being limited to css selectors, it works with any `SoupSelector` instance.

Classes
-------
- `NthOfSelector` - Selects nth element matching given selector
- `NthLastOfSelector` - Selects nth last element matching given selector
- `OnlyOfSelector` - Selects only element matching given selector
"""

from typing import Optional

from soupsavvy.base import SoupSelector, check_selector
from soupsavvy.interfaces import IElement
from soupsavvy.selectors.nth.nth_utils import parse_nth
from soupsavvy.utils.selector_utils import TagIterator, TagResultSet


class BaseNthOfSelector(SoupSelector):
    """
    Base class for nth-of-selector and nth-last-of-selector
    that implements general logic for finding matching elements.
    """

    # slice for modification of list of elements matching selector
    _slice: slice

    def __init__(self, selector: SoupSelector, nth: str) -> None:
        """
        Initializes nth selector instance.

        Parameters
        ----------
        selector : SoupSelector
            Any `SoupSelector` instance used to match elements.
        nth : str
            CSS nth selector string. Accepts all valid css nth formulas.

        Raises
        ------
        NotSoupSelectorException
            If selector is not an instance of `SoupSelector`.
        """
        self._selector = check_selector(selector)
        self.nth_selector = parse_nth(nth)

    @property
    def selector(self) -> SoupSelector:
        """
        Returns selector instance used for matching elements in this nth selector.

        Returns
        -------
        SoupSelector
            Selector used in this nth selector.
        """
        return self._selector

    def find_all(
        self,
        tag: IElement,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[IElement]:
        # if recursive is False, check only children of tag itself
        tag_iterator = (
            TagIterator(tag, recursive=recursive, include_self=True)
            if recursive
            else iter([tag])
        )

        matches = []

        for tag_ in tag_iterator:
            matching = self.selector.find_all(tag=tag_, recursive=False)[self._slice]
            matches += [
                matching[index - 1]
                for index in self.nth_selector.generate(len(matching))
            ]

        # keep order of tags and limit
        results = TagResultSet(
            list(TagIterator(tag, recursive=recursive))
        ) & TagResultSet(matches)

        return results.fetch(limit)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return (
            self.selector == other.selector and self.nth_selector == other.nth_selector
        )

    def __repr__(self):
        cls = self.__class__.__name__
        return f"{cls}(selector={self.selector}, nth={self.nth_selector})"

    def __str__(self):
        return repr(self)


class NthOfSelector(BaseNthOfSelector):
    """
    Selector for finding nth-of elements in the soup among elements that match
    provided `SoupSelector` instance.

    Example
    -------
    >>> selector = NthOfSelector(ClassSelector("item"), "2n+1")

    matches all odd elements with class "item".

    Example
    -------
    >>> <div class="item">1</div> ✔️
    ... <div id="item"></div> ❌
    ... <div class="item">2</div> ❌
    ... <div class="item">3</div> ✔️
    ... <div class="widget"></div> ❌
    ... <div class="item">4</div> ❌

    Notes
    -----
    For more information about standard :nth-of-type pseudo-class, visit:

    https://developer.mozilla.org/en-US/docs/Web/CSS/:nth-of-type
    """

    # keep initial order of matching elements
    _slice = slice(None)


class NthLastOfSelector(BaseNthOfSelector):
    """
    Selector for finding nth-last-of elements in the soup among elements that match
    provided `SoupSelector` instance.

    Example
    -------
    >>> selector = NthLastOfSelector(ClassSelector("item"), "2n+1")

    matches all odd elements with class "item" starting from the last element.

    Example
    -------
    >>> <div class="item">1</div> ❌
    ... <div id="item"></div> ❌
    ... <div class="item">2</div> ✔️
    ... <div class="item">3</div> ❌
    ... <div class="widget"></div> ❌
    ... <div class="item">4</div> ✔️

    Notes
    -----
    For more information about standard :nth-of-type pseudo-class, visit:

    https://developer.mozilla.org/en-US/docs/Web/CSS/:nth-last-of-type
    """

    # reverse order of matching elements
    _slice = slice(None, None, -1)


class OnlyOfSelector(SoupSelector):
    """
    Selector for finding the only element,
    that matches provided `SoupSelector` instance among its siblings.

    Example
    -------
    >>> selector = OnlyOfSelector(ClassSelector("item"))

    matches all elements with class "item" that are the only child of their parent
    that matches the selector.

    Example
    -------
    >>> <div><div class="item"></div><a class="item"></a></div> ❌
    >>> <div><div class="item"></div><a class="widget"></a></div> ✔️
    >>> <div><div class="item"></div></div> ✔️
    >>> <div><div class="widget"></div></div> ❌

    Notes
    -----
    For more information about standard :only-of-type pseudo-class, visit:

    https://developer.mozilla.org/en-US/docs/Web/CSS/:only-of-type
    """

    def __init__(self, selector: SoupSelector) -> None:
        """
        Initializes `OnlyOfSelector` instance.

        Parameters
        ----------
        selector : SoupSelector
            Any `SoupSelector` instance used to match elements.

        Raises
        ------
        NotSoupSelectorException
            If selector is not an instance of `SoupSelector`.
        """
        self.selector = check_selector(selector)

    def find_all(
        self,
        tag: IElement,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[IElement]:
        tag_iterator = (
            TagIterator(tag, recursive=recursive, include_self=True)
            if recursive
            else iter([tag])
        )

        matching = [
            self.selector.find_all(tag=tag_, recursive=False) for tag_ in tag_iterator
        ]
        matches = [elements[0] for elements in matching if len(elements) == 1]

        # keep order of tags and limit
        results = TagResultSet(
            list(TagIterator(tag, recursive=recursive))
        ) & TagResultSet(matches)

        return results.fetch(limit)

    def __eq__(self, other):
        if not isinstance(other, OnlyOfSelector):
            return False

        return self.selector == other.selector

    def __repr__(self):
        cls = self.__class__.__name__
        return f"{cls}(selector={self.selector})"
