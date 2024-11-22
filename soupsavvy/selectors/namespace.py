"""Namespace with constants and types used by selectors"""

from typing import Pattern, Union

# default pattern if no value was provided
# wild card - matches any sequence of characters in a non-greedy
DEFAULT_PATTERN = "(.*?)"
# css selector wildcard
CSS_SELECTOR_WILDCARD = "*"
# allowed pattern types for attribute selectors
PatternType = Union[Pattern[str], str]
