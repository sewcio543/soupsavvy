"""
Module for selectors that are based on HTML element attributes.

They are used for selection of various elements in the markup,
based on attributes values.

Classes
-------
AttributeSelector - Selects element for any attribute value.
IdSelector - Selects element based on 'id' attribute value.
ClassSelector - Selects element based on 'class' attribute value.
"""

import re
from dataclasses import dataclass
from typing import Any, Optional, Pattern

import soupsavvy.tags.namespace as ns
from soupsavvy.tags.base import SelectableCSS, SingleSoupSelector
from soupsavvy.tags.namespace import PatternType


@dataclass
class AttributeSelector(SingleSoupSelector, SelectableCSS):
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
    value : str | Pattern, optional
        Value of the attribute, like a class name. Can be regex pattern,
        which results in using re.search to match the attribute value.
        By default None, if not provided, default pattern matching any sequence
        of characters is used.
    re : bool, optional
        Whether to use a regex pattern to match the attribute value, by default False.
        If True, re.search is used to match the attribute value.

    Implements SelectableCSS interface for CSS selector generation.

    Example
    -------
    >>> selector = AttributeSelector(name="class", value="widget")
    ... selector.selector
    [class=widget]

    >>> selector = AttributeSelector(name="class", value="widget", re=True)
    ... selector.selector
    [class*=widget]

    >>> selector = AttributeSelector("class")
    ... selector.selector
    [class]

    It is a simplified version and it will not be equivalent in results
    in case of using regex patterns, which are not supported in CSS,
    it defaults to *= containment operator.

    Example
    -------
    >>> selector = AttributeSelector(name="class", value=re.compile("^main[0-9]"))
    ... selector.selector
    [class*='^main[0-9]']
    """

    name: str
    value: Optional[PatternType] = None
    re: bool = False

    def __post_init__(self) -> None:
        """Sets pattern attribute used in SoupSelector find operations."""
        self._pattern = self._parse_pattern()

    def _parse_pattern(self) -> PatternType:
        """Parses pattern used in find methods based on provided init parameters."""
        # if value was not provided, fall back to default pattern
        if self.value is None:
            return re.compile(ns.DEFAULT_PATTERN)
        # if value was provided and re = True, create pattern from value
        if self.re:
            return re.compile(self.value)
        # if value was provided and re = False, use str value as pattern
        return self.value

    @property
    def selector(self) -> str:
        # undefined value - bs Tag matches all elements with attribute if css is
        # provided without a value in ex. format '[href]'
        if self.value is None:
            return f"[{self.name}]"

        value = self._pattern
        re = self.re

        if isinstance(self._pattern, Pattern):
            # extract regex pattern string from compiled regex
            value = self._pattern.pattern
            # always reduce to containment operator for regex patterns
            re = True

        operator = "*=" if re else "="
        return f"[{self.name}{operator}'{value}']"

    @property
    def _find_params(self) -> dict[str, Any]:
        # passing filters in attrs parameter as dict instead of kwargs
        # to avoid overriding other find method parameters like ex. 'name'
        return {ns.ATTRS: {self.name: self._pattern}}

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AttributeSelector):
            return False

        # pattern is what is used in find methods
        return self._pattern == other._pattern and self.name == other.name


class _SpecificAttributeSelector(AttributeSelector):
    """
    Base class for specific attribute selectors,
    that wraps AttributeSelector with default attribute name for user convenience.

    Child classes should define _NAME attribute with default attribute name,
    that will be used in the AttributeSelector.
    """

    _NAME: str

    def __init__(
        self,
        value: Optional[PatternType] = None,
        re: bool = False,
    ) -> None:
        """
        Initializes specific attribute selector with default attribute name.

        Parameters
        ----------
        value : str | Pattern, optional
            Value of the attribute, like a class name. Can be regex pattern,
            which results in using re.search to match the attribute value.
            By default None, if not provided, default pattern matching any sequence
            of characters is used.
        re : bool, optional
            Whether to use a regex pattern to match the attribute value,
            by default False. If True, re.search is used to match the attribute value.
        """
        super().__init__(name=self._NAME, value=value, re=re)


class IdSelector(_SpecificAttributeSelector):
    """
    Component for selecting HTML elements based on 'id' attribute value.
    Convenience wrapper for AttributeSelector with default attribute name 'id',
    as its use is very common in CSS selectors.

    Example
    -------
    >>> IdSelector("main")

    matches all elements that have 'id' attribute with value "main".

    Example
    -------
    >>> <div id="main">Hello World</div> ✔️
    >>> <div id="content">Hello World</div> ❌

    Implements SelectableCSS interface for CSS selector generation,
    provides simplified, more css native selector for id attribute,
    when value is provided, and no pattern is used.

    Example
    -------
    >>> selector = IdSelector("main")
    ... selector.selector
    #main

    It is a simplified version and it will not be equivalent in results
    in case of using regex patterns, which are not supported in CSS,
    it defaults to *= containment operator.

    Example
    -------
    >>> selector = IdSelector(re.compile("^main[0-9]"))
    ... selector.selector
    [id*='^main[0-9]']
    """

    _NAME = "id"

    @property
    def selector(self) -> str:
        # returns '#' css syntax if selecting string value
        if isinstance(self._pattern, str):
            return f"#{self._pattern}"

        return super().selector


class ClassSelector(_SpecificAttributeSelector):
    """
    Component for selecting HTML elements based on 'class' attribute value.
    Convenience wrapper for AttributeSelector with default attribute name 'class',
    as its use is very common in CSS selectors.

    Example
    -------
    >>> ClassSelector("main")

    matches all elements that have 'class' attribute with value "main".

    Example
    -------
    >>> <div class="main">Hello World</div> ✔️
    >>> <div class="content">Hello World</div> ❌

    Implements SelectableCSS interface for CSS selector generation,
    provides simplified, more css native selector for class attribute,
    when value is provided, and no pattern is used.

    Example
    -------
    >>> selector = ClassSelector("main")
    ... selector.selector
    .main

    It is a simplified version and it will not be equivalent in results
    in case of using regex patterns, which are not supported in CSS,
    it defaults to *= containment operator.

    Example
    -------
    >>> selector = ClassSelector(re.compile("^main[0-9]"))
    ... selector.selector
    [class*='^main[0-9]']
    """

    _NAME = "class"

    @property
    def selector(self) -> str:
        # returns '.' css syntax if selecting string value
        if isinstance(self._pattern, str):
            return f".{self._pattern}"

        return super().selector
