"""
`soupsavvy` is flexible search engine for `BeautifulSoup`,
designed to provide more powerful capabilities, making more complex searches simple
and web scraping tasks more efficient and manageable.

`soupsavvy` introduces the concept of a `Selector`,
a declarative search procedure designed with simple and readable syntax.
It encapsulates search logic, making it reusable across different scenarios.

The package offers various types of selectors that can be easily combined
to perform more complex searches.
"""

from .selectors import (
    AncestorCombinator,
    Anchor,
    AndSelector,
    AnyTagSelector,
    AttributeSelector,
    ChildCombinator,
    ClassSelector,
    DescendantCombinator,
    HasSelector,
    IdSelector,
    NextSiblingCombinator,
    NotSelector,
    OrSelector,
    ParentCombinator,
    PatternSelector,
    SelectorList,
    SelfSelector,
    SubsequentSiblingCombinator,
    TypeSelector,
    UniversalSelector,
    XORSelector,
)

__version__ = "0.3.0-dev3"
__author__ = "sewcio543"

__all__ = [
    "UniversalSelector",
    "AttributeSelector",
    "TypeSelector",
    "PatternSelector",
    "SelectorList",
    "DescendantCombinator",
    "AndSelector",
    "NotSelector",
    "SelfSelector",
    "ChildCombinator",
    "NextSiblingCombinator",
    "SubsequentSiblingCombinator",
    "AncestorCombinator",
    "ParentCombinator",
    "HasSelector",
    "Anchor",
    "OrSelector",
    "ClassSelector",
    "IdSelector",
    "XORSelector",
    "AnyTagSelector",
]
