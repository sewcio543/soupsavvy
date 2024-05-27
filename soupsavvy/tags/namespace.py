"""Namespace with constants and types for tag components."""

from typing import Union

from bs4 import NavigableString, Tag

# bs4 parameter name for tag name
NAME = "name"
# attribute filter parameter name in bs4.Tag find methods
ATTRS = "attrs"
# bs4 parameter name for tag text
STRING = "string"
# possible return types of bs4.Tag find method
FindResult = Union[NavigableString, Tag, None]
# default pattern if no value was provided
# wild card - matches any sequence of characters in a non-greedy
DEFAULT_PATTERN = "(.*?)"
# css selector wildcard
CSS_SELECTOR_WILDCARD = "*"
