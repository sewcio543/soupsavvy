"""
Module with selectors that search for elements based on their attributes.

Classes
-------
- `AttributeSelector` - Selects element based on any attribute value.
- `IdSelector` - Selects element based on 'id' attribute value.
- `ClassSelector` - Selects element based on 'class' attribute value.
"""

import re
from dataclasses import dataclass
from typing import Optional, Pattern

import soupsavvy.selectors.namespace as ns
from soupsavvy.base import SoupSelector
from soupsavvy.interfaces import T
from soupsavvy.selectors.namespace import PatternType


@dataclass
class AttributeSelector(SoupSelector):
    """
    Selector for searching element based on its attribute value.
    Counterpart of css attribute selectors, that extends its capability
    with regex pattern matching.

    Example
    -------
    >>> AttributeSelector(name="role", value="widget")

    matches all elements that have 'role' attribute with value "widget".

    Example
    -------
    >>> <div role="widget">Hello World</div> ✔️
    >>> <div class="menu">Hello World</div> ❌
    >>> <div role="menu">Hello World</div> ❌

    CSS counterpart can be represented as:

    Example
    -------
    >>> [role="widget"]

    In case of using regex pattern, `re.search` is used to match the attribute value.

    Example
    -------
    >>> AttributeSelector(name="href", value=re.compile(r"wikipedia"))

    Parameters
    ----------
    name : str
        HTML element attribute name ex. "class", "href"
    value : str | Pattern, optional
        Value of the attribute to match.
        By default None, if not provided, default pattern matching any sequence
        of characters is used.

    Notes
    -----
    For more information about attribute selectors, see:

    https://developer.mozilla.org/en-US/docs/Web/CSS/Attribute_selectors
    """

    name: str
    value: Optional[PatternType] = None

    def __post_init__(self) -> None:
        """Sets pattern attribute used in `SoupSelector` find operations."""
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

    def find_all(
        self,
        tag: T,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[T]:
        params = {self.name: self._pattern}
        return tag.find_all(attrs=params, recursive=recursive, limit=limit)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AttributeSelector):
            return False

        # pattern is what is used in find methods
        return self._pattern == other._pattern and self.name == other.name


class SpecificAttributeSelector(AttributeSelector):
    """
    Base class for specific attribute selectors,
    that wraps `AttributeSelector` with default attribute name for user convenience.

    Child classes should define _NAME attribute with default attribute name,
    that will be used in the `AttributeSelector`.
    """

    _NAME: str

    def __init__(self, value: Optional[PatternType] = None) -> None:
        """
        Initializes specific attribute selector with default attribute name.

        Parameters
        ----------
        value : str | Pattern, optional
            Value of the attribute to match.
            By default None, if not provided, default pattern matching any sequence
            of characters is used.
        """
        super().__init__(name=self._NAME, value=value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value!r})"


class IdSelector(SpecificAttributeSelector):
    """
    Specific `AttributeSelector` for matching elements based on 'id' attribute value.

    Example
    -------
    >>> IdSelector("main")

    matches all elements that have 'id' attribute with value "main".

    Example
    -------
    >>> <div id="main">Hello World</div> ✔️
    >>> <div id="content">Hello World</div> ❌

    `IdSelector` is a convenience wrapper for `AttributeSelector`,
    thus example above is equivalent to using:

    >>> AttributeSelector(name="id", value="main")

    CSS counterpart can be represented as:

    Example
    -------
    >>> #main

    In case of using regex pattern, `re.search` is used to match the attribute value.

    Example
    -------
    >>> IdSelector(re.compile(r"content[0-9]+"))

    Notes
    -----
    For more information about id attribute, see:

    https://developer.mozilla.org/en-US/docs/Web/CSS/ID_selectors
    """

    _NAME = "id"


class ClassSelector(SpecificAttributeSelector):
    """
    Specific `AttributeSelector` for matching elements based on 'class' attribute value.

    Example
    -------
    >>> ClassSelector("widget")

    matches all elements that have 'class' attribute with value "widget".

    Example
    -------
    >>> <div class="widget">Hello World</div> ✔️
    >>> <div class="content">Hello World</div> ❌

    `ClassSelector` is a convenience wrapper for `AttributeSelector`,
    thus example above is equivalent to using:

    >>> AttributeSelector(name="class", value="widget")

    CSS counterpart can be represented as:

    Example
    -------
    >>> .widget

    In case of using regex pattern, `re.search` is used to match the attribute value.

    Example
    -------
    >>> ClassSelector(re.compile(r"nav"))

    Notes
    -----
    For more information about class attribute, see:

    https://developer.mozilla.org/en-US/docs/Web/CSS/Class_selectors
    """

    _NAME = "class"
