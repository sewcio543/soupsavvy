"""
Module for components utilized to navigate html markup or BeautifulSoup Tags.

They are used for selection of various elements in the markup,
based on their tag name, attributes or text content.

They can be considered soupsavvy equivalent of CSS selectors,
but with more flexibility and power to navigate the markup.

Classes
-------
AttributeSelector - Attribute Selector
TagSelector - combines type and attribute selectors
PatternSelector - matches elements based on text content and selector
AnyTagSelector - universal selector (*)
AndSelector - intersection of multiple selectors
NotSelector - negation of a selector (~)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import reduce
from typing import Any, Iterable, Optional, Pattern

from bs4 import Tag

import soupsavvy.tags.namespace as ns
from soupsavvy.tags.base import (
    IterableSoup,
    SelectableCSS,
    SelectableSoup,
    SingleSelectableSoup,
)
from soupsavvy.tags.exceptions import WildcardTagException
from soupsavvy.tags.tag_utils import TagIterator, UniqueTag


@dataclass
class AttributeSelector(SingleSelectableSoup, SelectableCSS):
    """
    Class representing attribute of the HTML element.
    If used directly, provides elements based only on a single attribute value.

    Example
    -------
    >>> AttributeSelector(name="class", value="widget")

    matches all elements that have 'class' attribute with value "widget".

    Example
    -------
    >>> <div class="widget">Hello World</div> ✔️
    >>> <div class="menu">Hello World</div> ❌

    Parameters
    ----------
    name : str
        HTML element attribute name ex. "class", "href"
    value : str, optional
        Value of the attribute, like a class name.
        By default None, if not provided pattern will be used.
        If both pattern and value are None, pattern falls back to default,
        that matches any sequence of characters.
    re : bool, optional
        Whether to use a pattern to match the attribute value, by default False.
        If True, attribute value needs to be contained in the name to be matched.
    pattern : Pattern | str, optional
        Regular Expression pattern to match the attribute value.
        Applicable only for SelectableSoup find operations, skipped in selector.

    Example
    -------
    >>> attribute = AttributeSelector(name="class", value="widget")
    >>> attribute.selector
    [class=widget]

    >>> attribute = AttributeSelector(name="class", value="widget", re=True)
    >>> attribute.selector
    [class*=widget]
    """

    name: str
    value: str | None = None
    re: bool = False
    pattern: Pattern[str] | str | None = None

    def __post_init__(self) -> None:
        """Sets pattern attribute used in SelectableSoup find operations."""
        self._pattern = self._parse_pattern()

    def _parse_pattern(self) -> Pattern[str] | str:
        """Parses pattern used in find methods based on provided init parameters."""
        # if any pattern was provided, it takes precedence before value and re
        if self.pattern is not None:
            return re.compile(self.pattern)
        # if pattern and value was not provided, fall back to default pattern
        if self.value is None:
            return re.compile(ns.DEFAULT_PATTERN)
        # if only value was provided and re = True, create pattern from value
        if self.re:
            return re.compile(self.value)
        # if only value was provided and re = False, use str value as pattern
        return self.value

    @property
    def selector(self) -> str:
        # undefined value - bs Tag matches all elements with attribute if css is
        # provided without a value in ex. format '[href]'
        if self.value is None:
            return f"[{self.name}]"

        operator = "*=" if self.re else "="
        return f"[{self.name}{operator}'{self.value}']"

    @property
    def _find_params(self) -> dict[str, Any]:
        # passing filters in attrs parameter as dict instead of kwargs
        # to avoid overriding other find method parameters like ex. 'name'
        return {ns.ATTRS: {self.name: self._pattern}}


@dataclass
class TagSelector(SingleSelectableSoup, SelectableCSS):
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
        HTML tag name ex. "a", "div". By default None.

    attributes : Iterable[AttributeSelector], optional
        Iterable of AttributeSelector objects that specify element attributes.
        By default empty list.

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
    Initializing object without passing any parameters is a legal move.
    It results in matching all elements in markup and wildcard selector "*".
    """

    tag: Optional[str] = None
    attributes: Iterable[AttributeSelector] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Raises exception if empty TagSelector was provided."""
        if self.tag is None and not self.attributes:
            raise WildcardTagException(
                "Empty TagSelector is not a valid input, provide tag or attributes. "
                + "If you want to match all elements, use AnyTag component instead."
            )

    @property
    def selector(self) -> str:
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


@dataclass
class PatternSelector(SingleSelectableSoup):
    """
    Class representing HTML element with specific string pattern for text.
    Provides elements matching TagSelector with their text matching a pattern.

    Example
    -------
    >>> PatternSelector(
    >>>     pattern="Hello World",
    >>>     tag=TagSelector("div")
    >>> )

    matches all elements that have "div" tag name
    AND their text is equal to "Hello World".

    Example
    -------
    >>> <div>Hello World</div> ✔️
    >>> <div>Hello Python</div> ❌

    Parameters
    ----------
    tag: SingleSelectableSoup
        An SingleSelectableSoup instance representing desired HTML element.
        AnyTagSelector is not a valid parameter and raises an exception.
    pattern: str | Pattern
        A pattern to match text of the element. Can be a string for exact match
        or Pattern for any more complex regular expressions.
    re: bool, optional
        Whether to use a pattern to match the text, by default False.
        If True, text of element needs to be contained in the pattern to be matched.

    Notes
    -----
    Pattern can be a regex pattern.
    Providing 're.compile(r"[0-9]")' as pattern will much any digit in text:

    Example
    -------
    >>> <div>Hello World 123</div> ✔️
    >>> <div>Hello World</div> ❌

    Raises
    ------
    EmptyTagSelectorException
        When empty TagSelector was passed as a tag parameter.
    """

    tag: SingleSelectableSoup
    pattern: str | Pattern[str]
    re: bool = False

    def __post_init__(self) -> None:
        #! if only string is specified in case of wildcard tag - returns NavigableString
        #! which causes problems downstream
        if isinstance(self.tag, AnyTagSelector):
            raise WildcardTagException(
                "AnyTag which is a wildcard tag matching all elements, "
                + "is not acceptable as a tag parameter for PatternTagSelector."
            )

    @property
    def _find_params(self) -> dict[str, Any]:
        pattern = re.compile(self.pattern) if self.re else self.pattern
        return {ns.STRING: pattern} | self.tag._find_params


class AnyTagSelector(SingleSelectableSoup, SelectableCSS):
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


@dataclass(init=False)
class NotSelector(SelectableSoup, IterableSoup):
    """
    Class representing selector of elements that do not match provided selectors.

    Example
    -------
    >>> NotSelector(TagSelector(tag="div")

    matches all elements that do not have "div" tag name.

    Example
    -------
    >>> <span> class="widget">Hello World</span> ✔️
    >>> <div class="menu">Hello World</div> ❌

    Object can be initialized with multiple selectors as well, in which case
    all selectors must match for element to be excluded from the result.

    Object can be created as well by using bitwise NOT operator '~'
    on a SelectableSoup object.

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
        tag: SelectableSoup,
        /,
        *tags: SelectableSoup,
    ) -> None:
        """
        Initializes NotSelectors object with provided positional arguments as tags.
        At least one SelectableSoup object is required to create NotSelectors.

        Parameters
        ----------
        tags: SelectableSoup
            SelectableSoup objects to negate match accepted as positional arguments.

        Raises
        ------
        NotSelectableSoupException
            If any of provided parameters is not an instance of SelectableSoup.
        """
        self._multiple = bool(tags)
        super().__init__([tag, *tags])

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
        matching = set()

        for step in self.steps:
            matching |= {
                UniqueTag(element)
                for element in step.find_all(tag, recursive=recursive)
            }

        return [
            element
            for element in TagIterator(tag, recursive=recursive)
            if UniqueTag(element) not in matching
        ][:limit]

    def __invert__(self) -> SelectableSoup:
        """
        Overrides __invert__ method to cancel out negation by returning
        the tag in case of single selector, or SoupUnionTag in case of multiple.
        """
        from soupsavvy.tags.combinators import SelectorList

        if not self._multiple:
            return self.steps[0]

        return SelectorList(*self.steps)


@dataclass(init=False)
class AndSelector(SelectableSoup, IterableSoup):
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
    on two SelectableSoup objects.

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
        tag1: SelectableSoup,
        tag2: SelectableSoup,
        /,
        *tags: SelectableSoup,
    ) -> None:
        """
        Initializes AndTagSelector object with provided positional arguments as tags.
        At least two SelectableSoup objects are required to create AndTagSelector.

        Parameters
        ----------
        tags: SelectableSoup
            SelectableSoup objects to match accepted as positional arguments.

        Raises
        ------
        NotSelectableSoupException
            If any of provided parameters is not an instance of SelectableSoup.
        """
        super().__init__([tag1, tag2, *tags])

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
        steps = iter(self.steps)
        matching = [
            UniqueTag(element)
            for element in next(steps).find_all(tag, recursive=recursive)
        ]

        for step in steps:
            # not using set on purpose to keep order of elements
            step_elements = [
                UniqueTag(element)
                for element in step.find_all(tag, recursive=recursive)
            ]
            matching = [element for element in matching if element in step_elements]

        return [element.tag for element in matching][:limit]
