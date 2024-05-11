"""Module with custom exceptions for the css tag selectors."""


class InvalidCSSSelector(Exception):
    """
    Raised when the provided CSS selector is invalid.
    Usually raised when invalid formula was passed into 'nth' selector.

    Example
    -------
    >>> NthChild("2x + 1")
    InvalidCSSSelector
    """
