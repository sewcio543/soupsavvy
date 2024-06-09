"""Module for custom Tag exceptions."""


class SoupSelectorException(Exception):
    """Custom Base Exception for SoupSelector specific Exceptions."""


class TagNotFoundException(SoupSelectorException):
    """
    Exception to be raised when SoupSelector element was not found in the markup.
    Raised by SoupSelector find method when strict parameter is set to True
    and target element was not found in provided bs4.Tag object.
    """


class NavigableStringException(SoupSelectorException):
    """
    Exception to be raised when NavigableString was found in find method.
    It does not return expected bs4 markup after conversion to bs4.Tag.
    When bs4.Tag find method was used with only 'string' parameter if any tag
    matches NavigableString is returned which does not have information about the tag.

    Example
    -------
    >>> nav_string = NavigableString("Hello World")
    >>> BeautifulSoup(nav_string)
    <html><body><p>Hello World</p></body></html>

    BeautifulSoup constructor always wraps NavigableString in <p> element.
    It is rather an unexpected behavior and should rather be avoided in SoupSelector
    find method, thus this exception is raised.
    """


class NotSoupSelectorException(SoupSelectorException, TypeError):
    """
    Exception to be raised when function excepted SoupSelector as input
    and got argument of the different, invalid type.
    """
