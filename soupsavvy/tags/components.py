"""
Module for components utilized to navigate html markup or BeautifulSoup Tags.

They are used for selection of various elements in the markup,
based on their tag name, attributes or text content.

They can be considered soupsavvy equivalent of CSS selectors,
but with more flexibility and power to navigate the markup.

Classes
-------
TagSelector - combines type and attribute selectors
PatternSelector - matches elements based on text content and selector
AnyTagSelector - universal selector (*)
AndSelector - intersection of multiple selectors
NotSelector - negation of a selector (~)
"""

from __future__ import annotations

import itertools
import re
from dataclasses import dataclass, field
from functools import reduce
from typing import Any, Iterable, Optional, Pattern

from bs4 import SoupStrainer, Tag

import soupsavvy.tags.namespace as ns
from soupsavvy.tags.attributes import AttributeSelector
from soupsavvy.tags.base import (
    MultipleSoupSelector,
    SelectableCSS,
    SingleSoupSelector,
    SoupSelector,
)
from soupsavvy.tags.tag_utils import TagIterator, TagResultSet


@dataclass
class TagSelector(SingleSoupSelector, SelectableCSS):
    """
    Class representing HTML element.
    Provides elements based on element tag and all defined attributes.

    Example
    -------
    >>> TagSelector(
    >>>     tag="div",
    >>>     attributes=[
    >>>         AttributeSelector(name="class", value="widget"),
    >>>         AttributeSelector(name="role", value="button")
    >>>     ]
    >>> )

    matches all elements that have "div" tag name, 'class' attribute "widget"
    and 'role' attribute "button".

    Example
    -------
    >>> <div class="widget" role="button">Hello World</div> ✔️
    >>> <div class="menu" role="button">Hello World</div> ❌

    Parameters
    ----------
    name : str, optional
        HTML tag name ex. "a", "div". By default None, all tag names will be matched.

    attributes : Iterable[AttributeSelector], optional
        Iterable of AttributeSelector objects that specify element attributes.
        By default empty list, no attribute will be checked.

    Example
    -------
    >>> element = TagSelector(
    >>>    tag="div",
    >>>    attributes=[AttributeSelector(name="class", value="widget")]
    >>> )
    >>> element.selector
    div[class=widget]

    Notes
    -----
    Initializing object without passing any parameters is equal to selector for all elements,
    which is equivalent to using AnyTagSelector object.
    """

    tag: Optional[str] = None
    attributes: Iterable[AttributeSelector] = field(default_factory=list)

    @property
    def selector(self) -> str:
        if not self.tag and not self.attributes:
            return ns.CSS_SELECTOR_WILDCARD

        # drop duplicated css attribute selectors and preserve order
        selectors = list(map(lambda attr: attr.selector, self.attributes))
        attrs = sorted(set(selectors), key=selectors.index)
        # at least one of tag or attributes must be provided
        return (self.tag or "") + "".join(attrs)

    @property
    def _find_params(self) -> dict[str, Any]:
        params = [attr._find_params[ns.ATTRS] for attr in self.attributes]
        # reduce raises error when given an empty iterable
        attrs = dict(reduce(lambda x, y: {**x, **y}, params)) if params else {}
        return {ns.NAME: self.tag} | {ns.ATTRS: attrs}

    def __eq__(self, other: object) -> bool:
        if isinstance(other, AnyTagSelector):
            return other == self
        if not isinstance(other, TagSelector):
            return False

        # TagSelector produces the same results only if attributes are in the same order
        return self.tag == other.tag and self.attributes == other.attributes


@dataclass
class PatternSelector(SoupSelector):
    """
    Class representing HTML element with specific string pattern for text.
    Provides elements matching with text matching the pattern.

    Example
    -------
    >>> PatternSelector(pattern="Hello World")

    matches all element with exact text content "Hello World".

    Example
    -------
    >>> <div>Hello World</div> ✔️
    >>> <div>Hello Python</div> ❌
    >>> <div>Hello World 3</div> ❌

    Parameters
    ----------
    pattern: str | Pattern
        A pattern to match text of the element. Can be a string for exact match
        or Pattern for any more complex regular expressions.

    Notes
    -----
    Selector uses re.search function to match text content
    if compiled regex is passed as pattern.
    Providing 're.compile(r"[0-9]")' as pattern will much any element with a digit in text.

    Example
    -------
    >>> import re
    >>> PatternSelector(pattern=re.compile(r"[0-9]"))

    Example
    -------
    >>> <div>Hello World 123</div> ✔️
    >>> <div>Hello World</div> ❌

    Due to bs4 implementation, element does not match the pattern if it has any children.
    Only leaf nodes can be returned by PatternSelector find methods.

    Example
    -------
    >>> <div>Hello World<span></span></div> ❌
    """

    pattern: str | Pattern[str]

    def __post_init__(self) -> None:
        """Sets up compiled regex pattern used for SoupStrainer in find methods."""
        from typing import Union

        self._pattern = (
            str(self.pattern) if not isinstance(self.pattern, Pattern) else self.pattern
        )

    def find_all(
        self, tag: Tag, recursive: bool = True, limit: Optional[int] = None
    ) -> list[Tag]:
        iterator = TagIterator(tag, recursive=recursive)
        strainer = SoupStrainer(string=self._pattern)  # type: ignore
        filter_ = filter(strainer.search_tag, iterator)
        return list(itertools.islice(filter_, limit))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PatternSelector):
            return False

        return self._pattern == other._pattern


@dataclass
class AnyTagSelector(SingleSoupSelector, SelectableCSS):
    """
    Class representing a wildcard tag that matches any tag in the markup.
    Matches always the first tag in the markup.

    AnyTagSelector implements SelectableCSS interface with wildcard css selector "*",
    aka. universal selector, that matches all elements in the markup.

    Example
    -------
    >>> any_element = AnyTagSelector()
    >>> any_element.selector
    "*"

    Notes
    -----
    For more information on universal selector see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/Universal_selectors
    """

    @property
    def _find_params(self) -> dict[str, Any]:
        return {}

    @property
    def selector(self) -> str:
        """Returns wildcard css selector matching all elements in the markup."""
        return ns.CSS_SELECTOR_WILDCARD

    def __eq__(self, other: object) -> bool:
        # TagSelector produces the same results only if it does not have
        # any parameters specified
        if isinstance(other, TagSelector):
            return other.tag is None and not other.attributes

        return isinstance(other, AnyTagSelector)


class NotSelector(MultipleSoupSelector):
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
        tag: SoupSelector,
        /,
        *tags: SoupSelector,
    ) -> None:
        """
        Initializes NotSelectors object with provided positional arguments as tags.
        At least one SoupSelector object is required to create NotSelector.

        Parameters
        ----------
        tags: SoupSelector
            SoupSelector objects to negate match accepted as positional arguments.

        Raises
        ------
        NotSoupSelectorException
            If any of provided parameters is not an instance of SoupSelector.
        """
        self._multiple = bool(tags)
        super().__init__([tag, *tags])

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
        from soupsavvy.tags.combinators import SelectorList

        if not self._multiple:
            return self.selectors[0]

        return SelectorList(*self.selectors)


class AndSelector(MultipleSoupSelector):
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
        tag1: SoupSelector,
        tag2: SoupSelector,
        /,
        *tags: SoupSelector,
    ) -> None:
        """
        Initializes AndTagSelector object with provided positional arguments as tags.
        At least two SoupSelector objects are required to create AndSelector.

        Parameters
        ----------
        tags: SoupSelector
            SoupSelector objects to match accepted as positional arguments.

        Raises
        ------
        NotSoupSelectorException
            If any of provided parameters is not an instance of SoupSelector.
        """
        super().__init__([tag1, tag2, *tags])

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


class HasSelector(MultipleSoupSelector):
    """
    Class representing elements selected with respect to matching reference elements.
    Element is selected if any of the provided selectors matched reference element.

    Example
    -------
    >>> HasSelector(TagSelector(tag="div"))

    matches all elements that have any descendant with "div" tag name.
    It uses default combinator of relative selector, which is descendant.

    Example
    -------
    >>> <span><div>Hello World</div></span> ✔️
    >>> <span><a>Hello World</a></span> ❌

    Other relative selectors can be used with Anchor element.

    Example
    -------
    >>> from soupsavvy.tags.relative import Anchor
    >>> HasSelector(Anchor > TagSelector("div"))
    >>> HasSelector(Anchor + TagSelector("div"))

    or by using RelativeSelector components directly:

    Example
    -------
    >>> from soupsavvy.tags.relative import RelativeChild, RelativeNextSibling
    >>> HasSelector(RelativeChild(TagSelector("div")))
    >>> HasSelector(RelativeNextSibling(TagSelector("div"))

    Example
    -------
    >>> <span><div>Hello World</div></span> ✔️
    >>> <span><a><div>Hello World</div></a></span> ❌

    In this case, HasSelector is anchored against any element, and matches only elements
    that have "div" tag name as a child.

    Object can be initialized with multiple selectors as well, in which case
    at least one selector must match for element to be included in the result.

    This is an equivalent of CSS :has() pseudo-class,
    that represents elements if any of the relative selectors that are passed as an argument
    match at least one element when anchored against this element.

    Example
    -------
    >>> :has(div, a) { color: red; }
    >>> :has(+ div, > a) { color: red; }

    These examples translated to soupsavvy would be:

    Example
    -------
    >>> from soupsavvy.tags.relative import Anchor
    >>> HasSelector(TagSelector("div"), TagSelector("a"))
    >>> HasSelector(Anchor + TagSelector("div"), Anchor > TagSelector("a"))

    Notes
    -----
    Passing RelativeDescendant selector into HasSelector is equivalent to using
    its selector directly, as descendant combinator is default option.

    Example
    -------
    >>> HasSelector(RelativeDescendant(TagSelector("div")))
    >>> HasSelector(Anchor > TagSelector("div"))
    >>> HasSelector(TagSelector("div"))

    Three of the above examples are equivalent.

    For more information on :has() pseudo-class see:
    https://developer.mozilla.org/en-US/docs/Web/CSS/:has
    """

    def __init__(
        self,
        selector: SoupSelector,
        /,
        *selectors: SoupSelector,
    ) -> None:
        """
        Initializes AndTagSelector object with provided positional arguments as tags.
        At least two SoupSelector objects are required to create HasSelector.

        Parameters
        ----------
        tags: SoupSelector
            SoupSelector objects to match accepted as positional arguments.
            At least one selector is required to create HasSelector.

        Raises
        ------
        NotSoupSelectorException
            If any of provided parameters is not an instance of SoupSelector.
        """
        super().__init__([selector, *selectors])

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:

        elements = TagIterator(tag, recursive=recursive)
        matching: list[Tag] = []

        for element in elements:
            # we only care if anything matching was found
            if any(step.find(element) for step in self.selectors):
                matching.append(element)

                if len(matching) == limit:
                    break

        return matching
