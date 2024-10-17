"""
Subpackage with soup selectors, which define declarative procedure
of searching for elements in the document.
"""

from .attributes import AttributeSelector, ClassSelector, IdSelector
from .combinators import (
    AncestorCombinator,
    ChildCombinator,
    DescendantCombinator,
    NextSiblingCombinator,
    ParentCombinator,
    SubsequentSiblingCombinator,
)
from .general import (
    AnyTagSelector,
    ExpressionSelector,
    PatternSelector,
    SelfSelector,
    TypeSelector,
    UniversalSelector,
)
from .logical import AndSelector, NotSelector, OrSelector, SelectorList, XORSelector
from .nth import NthLastOfSelector, NthOfSelector, OnlyOfSelector
from .relative import Anchor, HasSelector

__all__ = [
    "TypeSelector",
    "AttributeSelector",
    "ClassSelector",
    "IdSelector",
    "PatternSelector",
    "UniversalSelector",
    "ExpressionSelector",
    "SelfSelector",
    "DescendantCombinator",
    "ChildCombinator",
    "NextSiblingCombinator",
    "SubsequentSiblingCombinator",
    "SelectorList",
    "ParentCombinator",
    "AncestorCombinator",
    "AndSelector",
    "NotSelector",
    "OrSelector",
    "HasSelector",
    "Anchor",
    "XORSelector",
    "AnyTagSelector",
    "NthOfSelector",
    "NthLastOfSelector",
    "OnlyOfSelector",
]
