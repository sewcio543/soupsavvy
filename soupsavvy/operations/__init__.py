"""
Package with operations used to post-process the results of selections.

Classes
-------
- `Operation` - User defined operation with any function.
- `Text` - Operation to extract text from the tag.
- `Href` - Operation to extract href attribute from the tag.
- `Parent` - Operation to extract parent tag of the tag.
- `Break` - Operation to break the pipeline execution.
- `IfElse` - Operation to control flow in the pipeline.
- `Continue` - Operation to skip the operation and continue with the next one.
- `SkipNone` - Operation to skip operation if input is None.
- `Suppress` - Operation to suppress exceptions and return None instead.
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
