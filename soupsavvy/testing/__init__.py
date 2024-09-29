"""
Package with functionalities for generating customizable html,
that can be used to test selectors and workflows.

Classes
-------
- `AttributeGenerator` - Generator for creating html attributes.
- `TagGenerator` - Generator for creating html tags.
- `ChoiceTemplate` - Template for randomly selecting from a list of choices.
- `RandomTemplate` - Template for generating a random string of ASCII letters and digits.
- `BaseTemplate` - Base for user-defined templates.
"""

from .generators import AttributeGenerator, TagGenerator
from .generators.templates import ChoiceTemplate, RandomTemplate
from .generators.templates.base import BaseTemplate

__all__ = [
    "AttributeGenerator",
    "TagGenerator",
    "ChoiceTemplate",
    "RandomTemplate",
    "BaseTemplate",
]
