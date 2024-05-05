"""Module for components utilized to navigate html markup or BeautifulSoup Tags."""

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


@dataclass
class AttributeTag(SingleSelectableSoup, SelectableCSS):
    """
    Class representing attribute of the HTML element.
    If used directly, provides elements based only on a single attribute value.
    For example 'AttributeTag(name="class", value="widget")' matches all html elements
    that have class attribute with value "widget".

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
    >>> attribute = AttributeTag(name="class", value="widget")
    >>> attribute.selector
    [class=widget]

    >>> attribute = AttributeTag(name="class", value="widget", re=True)
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
class ElementTag(SingleSelectableSoup, SelectableCSS):
    """
    Class representing HTML element.
    Provides elements based on element tag and all defined attributes.

    Example
    -------
    >>> ElementTag(
    >>>     tag="div",
    >>>     attributes=[
    >>>         AttributeTag(name="class", value="widget"),
    >>>         AttributeTag(name="role", value="button")
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

    attributes : Iterable[AttributeTag], optional
        Iterable of AttributeTag objects that specify element attributes.
        By default empty list.

    Example
    -------
    >>> element = ElementTag(
    >>>    tag="div",
    >>>    attributes=[AttributeTag(name="class", value="widget")]
    >>> )
    >>> element.selector
    div[class=widget]

    Notes
    -----
    Initializing object without passing any parameters is a legal move.
    It results in matching all elements in markup and wildcard selector "*".
    """

    tag: Optional[str] = None
    attributes: Iterable[AttributeTag] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Raises exception if empty ElementTag was provided."""
        if self.tag is None and not self.attributes:
            raise WildcardTagException(
                "Empty ElementTag is not a valid input, provide tag or attributes. "
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
class PatternElementTag(SingleSelectableSoup):
    """
    Class representing HTML element with specific string pattern for text.
    Provides elements matching ElementTag with their text matching a pattern.

    Example
    -------
    >>> PatternElementTag(
    >>>     pattern="Hello World",
    >>>     tag=ElementTag("div")
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
        Empty Tag is not a valid parameter and raises an exception.
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
    EmptyElementTagException
        When empty ElementTag was passed as a tag parameter.
    """

    tag: SingleSelectableSoup
    pattern: str | Pattern[str]
    re: bool = False

    def __post_init__(self) -> None:
        #! if only string is specified in case of wildcard tag - returns NavigableString
        #! which causes problems downstream
        if isinstance(self.tag, AnyTag):
            raise WildcardTagException(
                "AnyTag which is a wildcard tag matching all elements, "
                + "is not acceptable as a tag parameter for PatternElementTag."
            )

    @property
    def _find_params(self) -> dict[str, Any]:
        pattern = re.compile(self.pattern) if self.re else self.pattern
        return {ns.STRING: pattern} | self.tag._find_params


@dataclass(init=False)
class StepsElementTag(SelectableSoup, IterableSoup):
    """
    Class representing an list of steps of multiple soup selectors.
    Finds nested elements that match all steps in order.

    Example
    -------
    >>> StepsElementTag(
    >>>     ElementTag("div", [AttributeTag(name="class", value="menu")]),
    >>>     ElementTag("a", [AttributeTag(name="href", value="google", re=True)])
    >>> )

    matches all elements inside 'div' element with 'menu' class attribute
    that are 'a' elements with href attribute containing 'google'.

    Example
    -------
    >>> <div class="menu"><a href="google.com"></a></div> ✔️
    >>> <div class="menu"><a href="duckduckgo.com"></a></div> ❌
    >>> <div class="widget"><a href="google.com"></a></div> ❌
    >>> <a href="google.com"></a> ❌
    >>> <div class="widget"></div> ❌

    Parameters
    ----------
    tags : SelectableSoup
        SelectableSoup objects to match accepted as positional arguments.

    Notes
    -----
    StepsElementTag does not implement SelectableSoup interface
    as it allows SelectableSoup as positional init arguments.
    """

    def __init__(
        self,
        tag1: SelectableSoup,
        tag2: SelectableSoup,
        /,
        *tags: SelectableSoup,
    ) -> None:
        """
        Initializes StepsElementTag object with provided positional arguments as tags.
        At least two SelectableSoup object required to create StepsElementTag.

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
        elements = [tag]

        for step in self.steps:
            elements = reduce(
                list.__add__,
                (step.find_all(element, recursive=recursive) for element in elements),
            )

            # break if no elements were found in the step
            if not elements:
                break

        return elements[:limit]


class AnyTag(SingleSelectableSoup, SelectableCSS):
    """
    Class representing a wildcard tag that matches any tag in the markup.
    Matches always the first tag in the markup.

    AnyTag implements SelectableCSS interface with wildcard css selector "*".

    Example
    -------
    >>> any_element = AnyTag()
    >>> any_element.selector
    "*"
    """

    @property
    def _find_params(self) -> dict[str, Any]:
        return {}

    @property
    def selector(self) -> str:
        """Returns wildcard css selector matching all elements in the markup."""
        return ns.CSS_SELECTOR_WILDCARD
