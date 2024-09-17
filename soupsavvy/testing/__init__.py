"""
Subpackage with functionalities for generating customizable html,
that can be used to test selectors and workflows.
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
