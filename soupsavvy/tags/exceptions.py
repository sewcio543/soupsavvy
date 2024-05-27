"""Module for custom Tag exceptions."""


class SelectableSoupException(Exception):
    """Custom Base Exception for SelectableSoup specific Exceptions."""


class TagNotFoundException(SelectableSoupException):
    """
    Exception to be raised when SelectableSoup element was not found in the markup.
    Raised by SelectableSoup find method when strict parameter is set to True
    and target element was not found in provided bs4.Tag object.
    """


class WildcardTagException(SelectableSoupException):
    """
    Exception to be raised when wildcard SelectableSoup is provided in place where
    it's not expected. AnyTag is a wildcard tag that matches any html elements.
    This could be useful in some cases, but can render code unpredictable.

    Example
    -------
    >>> PatternElementTag(AnyTag(), pattern="Hello World")
    WildcardElementTagException

    In this example wildcard AnyTag is not accepted as input tag and this exception
    is raised. PatternElementTag without any tag search parameters except for 'string'
    returns NavigableString in find method,
    which causes unexpected behavior downstream that would rather be avoided in line
    with 'asking for permission' programming style.
    """


class NavigableStringException(SelectableSoupException):
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
    It is rather an unexpected behavior and should rather be avoided in SelectableSoup
    find method, thus this exception is raised.
    """


class NotSelectableSoupException(SelectableSoupException, TypeError):
    """
    Exception to be raised when function excepted SelectableSoup as input
    and got argument of the different, invalid type.
    """
