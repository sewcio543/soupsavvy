"""
Module with implementation of templates that complement generator components
providing more customization options.

Classes
-------
- `EmptyTemplate` - Template for generating an empty string.
- `ConstantTemplate` - Template for generating a constant string.
- `ChoiceTemplate` - Template for randomly selecting from a list of choices.
- `RandomTemplate` - Template for generating a random string of ASCII letters and digits.
"""

from .templates import ChoiceTemplate, ConstantTemplate, EmptyTemplate, RandomTemplate

__all__ = [
    "ChoiceTemplate",
    "ConstantTemplate",
    "EmptyTemplate",
    "RandomTemplate",
]
