"""Module with custom exception for generators."""


class HTMLGeneratorException(Exception):
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
