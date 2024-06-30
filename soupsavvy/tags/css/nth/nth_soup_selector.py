"""
Module with nth-of-type selector implementations for SoupSelectors.
Searches for nth-of-type element in similar fashion to CSS nth-of-type selector,
but type is any SoupSelector instance. It also supports nth-last-of-type selector.
"""

from typing import Optional

from bs4 import Tag

from soupsavvy.tags.base import SoupSelector
from soupsavvy.tags.css.nth.nth_utils import parse_nth
from soupsavvy.tags.tag_utils import TagIterator, TagResultSet


class BaseNthOfSelector(SoupSelector):
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
        """
        self._check_selector_type(selector)
        self.selector = selector
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
            else [tag]
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


class NthOfSelector(BaseNthOfSelector):
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

    For more information about standard nth-of-type selector, visit:
    https://developer.mozilla.org/en-US/docs/Web/CSS/:nth-of-type

    and check out soupsavvy implementation of nth-of-type selector:
    `soupsavvy.tags.css.tag_selectors.NthOfType`
    """

    # keep initial order of matching elements
    _slice = slice(None)


class NthLastOfSelector(BaseNthOfSelector):
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

    For more information about standard nth-of-type selector, visit:
    https://developer.mozilla.org/en-US/docs/Web/CSS/:nth-last-of-type

    and check out soupsavvy implementation of nth-of-type selector:
    `soupsavvy.tags.css.tag_selectors.NthLastOfType`
    """

    # reverse order of matching elements
    _slice = slice(None, None, -1)


# class NthOnlyOfSelector(SoupSelector):
#     def __init__(self, selector: SoupSelector) -> None:
#         self.selector = selector

#     def find_all(self, tag: Tag, recursive: bool = True, limit=None) -> list[Tag]:
#         iter_ = TagIterator(tag, recursive=recursive)
#         matches = []

#         for i in iter_:
#             matching = self.selector.find_all(tag=i, recursive=False)

#             if len(matching) == 1:
#                 matches.append(matching[0])

#                 if len(matches) == limit:
#                     break

#         return matches

#     def __eq__(self, other):
#         if not isinstance(other, NthOnlyOfSelector):
#             return False

#         return self.selector == other.selector
