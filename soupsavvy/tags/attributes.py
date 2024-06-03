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
from typing import Any, Optional

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
        Applicable only for SoupSelector find operations, skipped in selector.
        Value always takes precedence over pattern, if both are provided.

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
    it defaults to selector matching all elements with the attribute
    if value is not provided.

    Example
    -------
    >>> selector = AttributeSelector(name="class", pattern="^main[0-9]+$")
    ... selector.selector
    [class]
    """

    name: str
    value: Optional[str] = None
    re: bool = False
    pattern: Optional[PatternType] = None

    def __post_init__(self) -> None:
        """Sets pattern attribute used in SoupSelector find operations."""
        self._pattern = self._parse_pattern()

    def _parse_pattern(self) -> PatternType:
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


class _SpecificAttributeSelector(AttributeSelector):
    """
    Base class for specific attribute selectors,
    that wrap AttributeSelector with default attribute name for user convenience.

    Child classes should define _NAME attribute with default attribute name,
    that will be used in the AttributeSelector.
    """

    _NAME: str

    def __init__(
        self,
        value: Optional[str] = None,
        re: bool = False,
        pattern: Optional[PatternType] = None,
    ) -> None:
        """
        Initializes specific attribute selector with default attribute name.

        Parameters
        ----------
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
            Applicable only for SoupSelector find operations, skipped in selector.
        """
        super().__init__(name=self._NAME, value=value, re=re, pattern=pattern)


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

    In case of using patterns or not specifying value, it falls back to
    the default AttributeSelector implementation.
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

    In case of using patterns or not specifying value, it falls back to
    the default AttributeSelector implementation.
    """

    _NAME = "class"

    @property
    def selector(self) -> str:
        # returns '.' css syntax if selecting string value
        if isinstance(self._pattern, str):
            return f".{self._pattern}"

        return super().selector
