"""
Subpackage with operations used to postprocessing the results of selectors.
"""

from .conditional import Break, Continue, IfElse
from .general import Operation
from .soup import Href, Parent, Text
from .wrappers import SkipNone, Suppress

__all__ = [
    "Operation",
    "Text",
    "Href",
    "Parent",
    "Break",
    "IfElse",
    "Continue",
    "SkipNone",
    "Suppress",
]
