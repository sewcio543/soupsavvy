"""
Module with nth-of-type selector implementations for SoupSelectors.
Searches for nth-of-type element in similar fashion to CSS nth-of-type selector,
but 'type' is any SoupSelector instance.
"""

from typing import Optional

from bs4 import Tag

from soupsavvy.selectors.base import SoupSelector
from soupsavvy.selectors.nth.nth_utils import parse_nth
from soupsavvy.selectors.tag_utils import TagIterator, TagResultSet


class _BaseNthOfSelector(SoupSelector):
    """
    Base class for nth-of-selector and nth-last-of-selector
    that implements general logic for finding matching elements.
    """

    # slice for modification of list of elements matching selector
    _slice: slice

    def __init__(self, selector: SoupSelector, nth: str) -> None:
        """
        Initializes NthOfSelector instance

        Parameters
        ----------
        selector : SoupSelector
            Any SoupSelector instance to match tags.
        nth : str
            CSS nth selector string. Accepts all valid css nth selectors.

        Raises
        ------
        NotSoupSelectorException
            If selector is not an instance of SoupSelector.
        """
        self.selector = self._check_selector_type(selector)
        self.nth_selector = parse_nth(nth)

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
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


class NthOfSelector(_BaseNthOfSelector):
    """
    Component that matches nth-of-type elements in the soup, with use of standard
    css nth selectors. Element is of type if it matches provided SoupSelector instance.

    Example
    -------
    >>> selector = NthOfSelector(AttributeSelector("class", "item"), "2n+1")

    matches all odd elements with class "item".

    Example
    -------
    >>> <div class="item">1</div> ✔️
    >>> <div id="item"></div> ❌
    >>> <div class="item">2</div> ❌
    >>> <div class="item">3</div> ✔️
    >>> <div class="widget"></div> ❌
    >>> <div class="item">4</div> ❌

    For more information about standard :nth-of-type selector, visit:
    https://developer.mozilla.org/en-US/docs/Web/CSS/:nth-of-type

    and check out soupsavvy implementation of :nth-of-type selector:
    `soupsavvy.tags.css.tag_selectors.NthOfType`
    """

    # keep initial order of matching elements
    _slice = slice(None)


class NthLastOfSelector(_BaseNthOfSelector):
    """
    Component that matches nth-last-of-type elements in the soup, with use of standard
    css nth selectors. Element is of type if it matches provided SoupSelector instance.

    Example
    -------
    >>> selector = NthLastOfSelector(AttributeSelector("class", "item"), "2n+1")

    matches all odd elements with class "item" starting from the last element.

    Example
    -------
    >>> <div class="item">1</div> ❌
    >>> <div id="item"></div> ❌
    >>> <div class="item">2</div> ✔️
    >>> <div class="item">3</div> ❌
    >>> <div class="widget"></div> ❌
    >>> <div class="item">4</div> ✔️

    For more information about standard :nth-of-type selector, visit:
    https://developer.mozilla.org/en-US/docs/Web/CSS/:nth-last-of-type

    and check out soupsavvy implementation of :nth-of-type selector:
    `soupsavvy.tags.css.tag_selectors.NthLastOfType`
    """

    # reverse order of matching elements
    _slice = slice(None, None, -1)


class OnlyOfSelector(SoupSelector):
    """
    Component that matches only-of-type elements in the soup. Element is of type
    if it matches provided SoupSelector instance.

    Example
    -------
    >>> selector = NthLastOnlyOfSelectorOfSelector(AttributeSelector("class", "item"))

    matches all elements with class "item" that are the only child of their parent
    that matches the selector.

    Example
    -------
    >>> <div><div class="item"></div><a class="item"></a></div> ❌
    >>> <div><div class="item"></div><a class="widget"></a></div> ✔️
    >>> <div><div class="item"></div></div> ✔️
    >>> <div><div class="widget"></div></div> ❌

    For all positive examples above, `<div class="item">` is matched.

    For more information about standard :only-of-type selector, visit:
    https://developer.mozilla.org/en-US/docs/Web/CSS/:only-of-type

    and check out soupsavvy implementation of :only-of-type selector:
    `soupsavvy.tags.css.tag_selectors.OnlyOfType`
    """

    def __init__(self, selector: SoupSelector) -> None:
        """
        Initializes OnlyOfSelector instance.

        Parameters
        ----------
        selector : SoupSelector
            Any SoupSelector instance to match tags.

        Raises
        ------
        NotSoupSelectorException
            If selector is not an instance of SoupSelector.
        """
        self.selector = self._check_selector_type(selector)

    def find_all(self, tag: Tag, recursive: bool = True, limit=None) -> list[Tag]:
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
