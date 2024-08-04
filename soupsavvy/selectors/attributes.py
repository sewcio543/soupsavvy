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

import soupsavvy.selectors.namespace as ns
from soupsavvy.selectors.base import SingleSoupSelector
from soupsavvy.selectors.namespace import PatternType


@dataclass
class AttributeSelector(SingleSoupSelector):
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
    """

    name: str
    value: Optional[PatternType] = None

    def __post_init__(self) -> None:
        """Sets pattern attribute used in SoupSelector find operations."""
        self._pattern = self._parse_pattern()

    def _parse_pattern(self) -> PatternType:
        """Parses pattern used in find methods based on provided init parameters."""
        # if value was not provided, fall back to default pattern
        if self.value is None:
            return re.compile(ns.DEFAULT_PATTERN)
        # cast value to string if not a regex pattern
        if not isinstance(self.value, Pattern):
            return str(self.value)
        # value is already a compiled regex pattern
        return self.value

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

    def __init__(self, value: Optional[PatternType] = None) -> None:
        """
        Initializes specific attribute selector with default attribute name.

        Parameters
        ----------
        value : str | Pattern, optional
            Value of the attribute, like a class name. Can be regex pattern,
            which results in using re.search to match the attribute value.
            By default None, if not provided, default pattern matching any sequence
            of characters is used.
        """
        super().__init__(name=self._NAME, value=value)


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
    """

    _NAME = "id"


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
    """

    _NAME = "class"
