"""Module for custom `soupsavvy` exceptions."""


class SoupsavvyException(Exception):
    """Custom Base Exception for `soupsavvy` specific Exceptions."""


class NotTagSearcherException(SoupsavvyException, TypeError):
    """
    Exception to be raised when function excepted `TagSearcher` as input
    and got argument of the different, invalid type.
    """


#! SELECTORS


class SoupSelectorException(SoupsavvyException):
    """Custom Base Exception for `SoupSelector` specific Exceptions."""


class TagNotFoundException(SoupSelectorException):
    """
    Exception to be raised when `SoupSelector` element was not found in the markup.
    Raised by `SoupSelector` find method when strict parameter is set to True
    and target element was not found in provided element object.
    """


class NotSoupSelectorException(SoupSelectorException, TypeError):
    """
    Exception to be raised when function excepted `SoupSelector` as input
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


class InvalidXPathSelector(SoupsavvyException):
    """
    Raised when the parsing provided XPath selector in `XPathSelector`
    failed due to invalid syntax.

    Example
    -------
    >>> XPathSelector("2x + 1")
    InvalidXPathSelector
    """


#! GENERATORS


class HTMLGeneratorException(SoupsavvyException):
    """Base exception for the HTML generator module."""


class NotUniqueAttributesException(HTMLGeneratorException):
    """
    Exception raised by `TagGenerator` when input attributes have non-unique names.
    HTML tags cannot have multiple attributes with the same name.

    Example
    ------
    >>> TagGenerator(name="a", attrs=["href", ("href", "/endpoint")]
    NotUniqueAttributesException
    """


class VoidTagWithChildrenException(HTMLGeneratorException):
    """
    Exception raised by `TagGenerator` when input name of the tag is a void html tag
    like <img> or <br> and children are specified, which is not an allowed operation.

    Example
    ------
    >>> TagGenerator(name="img", children=["div", "span"])
    VoidTagWithChildrenException
    """


class EmptyNameException(HTMLGeneratorException):
    """
    Exception raised by `TagGenerator` when input name of the tag is empty.
    Exception raised by `AttributeGenerator` when input name of the attribute is empty.

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
    Exception raised by `AttributeGenerator` when invalid template is passed as value
    or by `TagGenerator` when invalid template is passed as text.
    Allowed types are str, `BaseTemplate` and None. Passing other types is not acceptable.

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
    Exception raised by `TagGenerator` when data passed into attributes iterable
    contains element that couldn't be parsed into `AttributeGenerator` object.
    Relevant only to elements in attributes iterable that
    are not already `AttributeGenerator` objects.

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


#! OPERATIONS


class OperationException(SoupsavvyException):
    """Base exception for the `BaseOperation` related errors"""


class FailedOperationExecution(SoupsavvyException):
    """
    Exception raised by `BaseOperation` when operation execution failed and raised
    any exception.
    """


class NotOperationException(OperationException, TypeError):
    """
    Exception to be raised when function excepted `BaseOperation` as input
    and got argument of the different, invalid type.
    """


class BreakOperationException(OperationException):
    """
    Exception raised by breaking operations such `Break`, to stop the execution
    of the pipeline. Special exception that accepts result as first argument.
    """

    def __init__(self, result) -> None:
        self.result = result


#! BROWSER OPERATIONS


class NotBrowserException(OperationException, TypeError):
    """
    Exception to be raised when function excepted `IBrowser` as input
    and got argument of the different, invalid type.
    """


#! MODELS


class BaseModelException(SoupsavvyException):
    """Base exception related to models package and `BaseModel` class."""


class UnknownModelFieldException(BaseModelException):
    """
    Exception raised by `BaseModel` when model passing unknown field name
    to model constructor.
    """


class ModelNotFoundException(BaseModelException):
    """
    Exception raised by `BaseModel` when model scope was not found in provided element
    and strict parameter was set to True.
    """


class FieldExtractionException(BaseModelException):
    """
    Exception raised by `BaseModel` when field extraction failed and related exception
    was raised by any selector step.
    """


class ScopeNotDefinedException(BaseModelException):
    """
    Exception raised by `BaseModel` when scope was not found in defined model class.
    `__scope__` class attribute is mandatory in `BaseModel` derived classes.
    """


class RequiredConstraintException(BaseModelException):
    """
    Exception raised by `Required` field wrapper when required field was not found
    in provided tag.
    """


class FieldsNotDefinedException(BaseModelException):
    """
    Exception raised by `BaseModel` when fields were not found in defined model class.
    At least one field should be defined in class to be a valid model.
    """


class MissingFieldsException(BaseModelException):
    """
    Exception raised by `BaseModel` when parameters passed into the constructor
    do not contain all required fields defined in the model class.
    """


class FrozenModelException(BaseModelException):
    """
    Exception raised by `BaseModel` when trying to modify frozen model instance.
    Frozen model instances are read-only and cannot be modified.
    """


class InvalidDecorationException(BaseModelException):
    """
    Exception raised by `BaseModel` when a method is decorated with an invalid
    decorator.
    """
