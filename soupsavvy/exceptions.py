"""Module for custom `soupsavvy` exceptions."""


class SoupsavvyException(Exception):
    """Custom Base Exception for `soupsavvy` specific Exceptions."""


class SoupSelectorException(SoupsavvyException):
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


class InvalidCSSSelector(SoupsavvyException):
    """
    Raised when the provided CSS selector is invalid.
    Usually raised when invalid formula was passed into 'nth' selector.

    Example
    -------
    >>> NthChild("2x + 1")
    InvalidCSSSelector
    """


class HTMLGeneratorException(SoupsavvyException):
    """Base exception for the HTML generator module."""


class NotUniqueAttributesException(HTMLGeneratorException):
    """
    Exception raised by TagGenerator when input attributes have non-unique names.
    HTML tags cannot have multiple attributes with the same name.

    Example
    ------
    >>> TagGenerator(name="a", attrs=["href", ("href", "/endpoint")]
    NotUniqueAttributesException
    """


class VoidTagWithChildrenException(HTMLGeneratorException):
    """
    Exception raised by TagGenerator when input name of the tag is a void html tag
    like <img> or <br> and children are specified, which is not an allowed operation.

    Example
    ------
    >>> TagGenerator(name="img", children=["div", "span"])
    VoidTagWithChildrenException
    """


class EmptyNameException(HTMLGeneratorException):
    """
    Exception raised by TagGenerator when input name of the tag is empty.
    Exception raised by AttributeGenerator when input name of the attribute is empty.

    Empty string is not acceptable in these contexts.

    Example
    ------
    >>> TagGenerator(name="")
    EmptyNamException

    Example
    ------
    >>> AttributeGenerator(name="")
    EmptyNamException
    """


class InvalidTemplateException(HTMLGeneratorException):
    """
    Exception raised by AttributeGenerator when invalid template is passed as value
    or by TagGenerator when invalid template is passed as text.
    Allowed types are str, BaseTemplate and None. Passing other types is not acceptable.

    Example
    ------
    >>> AttributeGenerator(name="class", value=123)
    InvalidTemplateException

    Example
    ------
    >>> TagGenerator(name="div", text=["hello", "world"])
    InvalidTemplateException
    """


class AttributeParsingError(HTMLGeneratorException):
    """
    Exception raised by TagGenerator when data passed into attributes iterable
    contains element that couldn't be parsed into AttributeGenerator object.
    Relevant only to elements in attributes iterable that
    are not already AttributeGenerator objects.

    Example
    ------
    >>> TagGenerator(name="div", attrs=[123]) # not a string
    AttributeParsingError

    Example
    ------
    >>> TagGenerator(name="div", attrs=[("", "test")]) # empty name string
    AttributeParsingError

    Example
    ------
    >>> TagGenerator(name="div", attrs=[("class", ["hello", "soupsavvy"]]) # invalid value template
    AttributeParsingError
    """
