"""
Package with classes for searching based on CSS selectors.

Contains implementation of basic CSS pseudo-classes like
:only-child, :empty, :nth-child().

They can be used in combination with other `SoupSelector` objects
to create more complex search procedures.

Classes
-------
- OnlyChild
- Empty
- FirstChild
- LastChild
- NthChild
- NthLastChild
- FirstOfType
- LastOfType
- NthOfType
- NthLastOfType
- OnlyOfType
- CSS - wrapper for simple search with CSS selectors
"""

from .selectors import (
    CSS,
    Empty,
    FirstChild,
    FirstOfType,
    LastChild,
    LastOfType,
    NthChild,
    NthLastChild,
    NthLastOfType,
    NthOfType,
    OnlyChild,
    OnlyOfType,
)

__all__ = [
    "CSS",
    "Empty",
    "FirstChild",
    "FirstOfType",
    "LastChild",
    "LastOfType",
    "NthChild",
    "NthLastChild",
    "NthLastOfType",
    "NthOfType",
    "OnlyChild",
    "OnlyOfType",
]
