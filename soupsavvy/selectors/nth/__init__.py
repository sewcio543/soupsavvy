"""
Module provides `nth-of-type` selector implementations for `SoupSelector`.
It allows you to search for the nth occurrence of an element,
similar to how the CSS `nth-of-type` pseudo-class works.
However, instead of being limited to css selectors, it works with any `SoupSelector` instance.

Classes
-------
`NthOfSelector` - Selects nth element matching given selector
`NthLastOfSelector` - Selects nth last element matching given selector
`OnlyOfSelector` - Selects only element matching given selector
"""

from .selectors import NthLastOfSelector, NthOfSelector, OnlyOfSelector

__all__ = ["NthLastOfSelector", "NthOfSelector", "OnlyOfSelector"]
