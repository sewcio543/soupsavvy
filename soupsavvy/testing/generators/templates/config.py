"""Module with configuration for the templates."""

from soupsavvy.testing.generators.templates.base import BaseTemplate
from soupsavvy.testing.generators.templates.templates import EmptyTemplate

# Default template used in AttributeGenerator when no value is specified
DEFAULT_VALUE_TEMPLATE: BaseTemplate = EmptyTemplate()

# Default template used in TagGenerator when no text is specified
DEFAULT_TEXT_TEMPLATE: BaseTemplate = EmptyTemplate()
