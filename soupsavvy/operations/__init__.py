"""
Package with operations used to post-process the results of selections.

Classes
-------
- `Operation` - User defined operation with any function.
- `Text` - Operation to extract text from the element.
- `Href` - Operation to extract href attribute from the element.
- `Parent` - Operation to extract parent element of the element.
- `Break` - Operation to break the pipeline execution.
- `IfElse` - Operation to control flow in the pipeline.
- `Continue` - Operation to skip the operation and continue with the next one.
- `SkipNone` - Operation to skip operation if input is None.
- `Suppress` - Operation to suppress exceptions and return None instead.
"""

from .conditional import Break, Continue, IfElse
from .element import Href, Parent, Text
from .general import Operation
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
