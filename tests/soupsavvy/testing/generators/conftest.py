"""Module for generators tests configuration."""

from soupsavvy.testing.generators.templates.templates import BaseTemplate

TEMPLATE_VALUE = "test"


class MockTemplate(BaseTemplate):
    """
    Mock template class for testing purposes
    that always returns a constant value.
    """

    def generate(self) -> str:
        return TEMPLATE_VALUE
