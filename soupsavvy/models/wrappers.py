"""
Module with wrappers for operations and selectors used mostly in models.
Wrappers are used to control behavior and define how fields of the models are defined.

Classes
-------
- SkipNone : OperationWrapper
- Suppress : OperationWrapper
- All : FieldWrapper
- Required : FieldWrapper
- Nullable : FieldWrapper
- Default : FieldWrapper
"""

from typing import Any, Optional

from bs4 import Tag

import soupsavvy.exceptions as exc
from soupsavvy.interfaces import Comparable, TagSearcher
from soupsavvy.operations.base import BaseOperation, check_operation
from soupsavvy.operations.selection_pipeline import SelectionPipeline


class OperationWrapper(BaseOperation):
    """
    A wrapper class for operations that extends the base operation functionality.
    Acts as a higher order operation, which controls behavior of the wrapped operation.
    """

    def __init__(self, operation: BaseOperation) -> None:
        """
        Initialize Higher Order Operation.

        Parameters
        ----------
        operation : BaseOperation
            The operation to be wrapped.
        """
        self.operation = operation

    def __eq__(self, x: Any) -> bool:
        """
        Check if two OperationWrapper instances are equal.
        They need to be of the same class and wrap the same operation.

        Parameters
        ----------
        x : Any
            The object to compare with.

        Returns
        -------
        bool
            True if the instances are equal, False otherwise.
        """
        return isinstance(x, self.__class__) and self.operation == x.operation

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.operation})"

    def __repr__(self) -> str:
        return str(self)


class SkipNone(OperationWrapper):
    """
    A wrapper that skips the operation if the input is None.
    Used to prevent exceptions where it's safe and expected to skip the operation.

    Example
    -------
    >>> from soupsavvy.operations import Text
    ... from soupsavvy.models import SkipNone
    ... operation = SkipNone(Text())
    ... operation.execute(None)
    None

    When element was not found, which can be expected, skips operation
    and returns None.
    """

    def _execute(self, arg: Any) -> Any:
        if arg is None:
            return None

        return self.operation.execute(arg)


class Suppress(OperationWrapper):
    """
    A wrapper that executes the operation
    and suppresses FailedOperationExecution exception, returning None instead.
    Used to catch exceptions where it's expected this might happen.

    Example
    -------
    >>> from soupsavvy.operations import Operation
    ... from soupsavvy.models import Suppress
    ... operation = Suppress(Operation(int))
    ... operation.execute("")
    None

    This can be used with `Default` operation to provide a default value
    when the operation fails.

    Example
    -------
    >>> from soupsavvy.operations import Operation
    ... from soupsavvy.models import Suppress
    ... operation = Default(Suppress(Operation(int)), 0)
    ... operation.execute("")
    None

    Operations in example can be used to try to convert string to integer
    from text of tag, that can potentially be empty. In such case, if it's not required,
    default can be set to None or known value.
    """

    def _execute(self, arg: Any) -> Any:
        try:
            return self.operation.execute(arg)
        except exc.FailedOperationExecution:
            return None


class FieldWrapper(TagSearcher, Comparable):
    """
    A wrapper for TagSearcher objects, that acts as a higher order searcher,
    which controls behavior of the wrapped searcher.
    Used as field to defined model.
    """

    def __init__(self, selector: TagSearcher) -> None:
        """
        Initialize FieldWrapper.

        Parameters
        ----------
        selector : TagSearcher
            The TagSearcher instance to be wrapped.
        """

        if not isinstance(selector, TagSearcher):
            raise exc.NotTagSearcherException(
                f"Expected {TagSearcher.__name__}, got {type(selector)}."
            )

        self.selector = selector

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Any]:
        """
        Find all matching tags using the wrapped selector.
        Used for compatibility with TagSearcher interface,
        delegates to wrapped selector.

        Parameters
        ----------
        tag : Tag
            Any BeautifulSoup tag to search within.
        recursive : bool, optional
            Whether to search recursively, by default True.
        limit : int, optional
            Limit the number of results, by default None.

        Returns
        -------
        list[Any]
            A list of found results.
        """
        return self.selector.find_all(tag, recursive=recursive, limit=limit)

    def __eq__(self, x: Any) -> bool:
        """
        Check if two FieldWrapper instances are equal.
        They need to be of the same class and wrap the same selector.

        Parameters
        ----------
        x : Any
            The object to compare with.

        Returns
        -------
        bool
            True if the instances are equal, False otherwise.
        """
        return isinstance(x, self.__class__) and self.selector == x.selector

    def __or__(self, x: Any) -> SelectionPipeline:
        """
        Overrides __or__ method called also by pipe operator '|'.
        Combines the current FieldWrapper with an operation.

        Parameters
        ----------
        x : BaseOperation
            The operation to be combined with the FieldWrapper.

        Returns
        -------
        SelectionPipeline
            New SelectionPipeline object created from combining selector and operation.

        Raises
        ------
        NotOperationException
            If provided object is not of BaseOperation type.
        """
        x = check_operation(x)
        return SelectionPipeline(selector=self, operation=x)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.selector})"

    def __repr__(self) -> str:
        return str(self)


class All(FieldWrapper):
    """
    Field wrapper for selecting multiple elements matching the selector.
    Forces find method to fall back to find_all method and return all matches.

    Example
    -------
    >>> from soupsavvy.models import All
    ... from soupsavvy import TypeSelector
    ... selector = All(TypeSelector("div"))
    ... selector.find(tag)
    [element1, element2, element3]
    """

    def find(self, tag: Tag, strict: bool = False, recursive: bool = True) -> list[Any]:
        """
        Find all matching tags using the wrapped selector,
        enforcing the use of find_all method.

        Parameters
        ----------
        tag : Tag
            Any BeautifulSoup tag to search within.
        strict : bool, optional
            Ignored, as this method always falls back to find_all.
        recursive : bool, optional
            Whether to search recursively, by default True.

        Returns
        -------
        list[Any]
            A list of matching results.
        """
        return self.selector.find_all(tag, recursive=recursive)


class Required(FieldWrapper):
    """
    Field wrapper for enforcing matched element not to be None.
    Raises an exception if searcher does not find any matches.

    Example
    -------
    >>> from soupsavvy.models import Required
    ... from soupsavvy import TypeSelector
    ... selector = Required(TypeSelector("div"))
    ... selector.find(tag)
    RequiredConstraintException
    """

    def find(self, tag: Tag, strict: bool = False, recursive: bool = True) -> Any:
        """
        Finds a required element using the wrapped selector,
        enforcing matched element not to be None.
        If any exception is raised during the search, it's propagated to the caller.

        Parameters
        ----------
        tag : Tag
            Any BeautifulSoup tag to search within.
        strict : bool, optional
            If True, raises an exception if no matches are found, by default False.
        recursive : bool, optional
            Whether to search recursively, by default True.

        Returns
        -------
        Any
            The found element.

        Raises
        ------
        RequiredConstraintException
            If selector returns None, indicating that required element was not found.
        """
        result = self.selector.find(tag=tag, strict=strict, recursive=recursive)

        if result is None:
            raise exc.RequiredConstraintException("Required element was not found")

        return result


class Nullable(FieldWrapper):
    """
    Field wrapper for allowing matched element to be None,
    irrespective of `strict` setting. Used to allow optional fields.

    Example
    -------
    >>> from soupsavvy.models import Nullable
    ... from soupsavvy import TypeSelector
    ... selector = Nullable(TypeSelector("div"))
    ... selector.find(tag, strict=True)
    None
    """

    def find(self, tag: Tag, strict: bool = False, recursive: bool = True) -> Any:
        """
        Finds an element, allowing for a null result if not found,
        irrespective of the `strict` setting. When `strict` is set to True
        and selector does not find any matches, it catches the exception
        and returns None instead.

        Parameters
        ----------
        tag : Tag
            Any BeautifulSoup tag to search within.
        strict : bool, optional
            Ignored, as this method always returns None if no matches are found.
        recursive : bool, optional
            Whether to search recursively, by default True.

        Returns
        -------
        Any
            The found element or None if not found.
        """
        try:
            return self.selector.find(tag=tag, strict=strict, recursive=recursive)
        except exc.TagNotFoundException:
            return None


class Default(FieldWrapper):
    """
    Field wrapper for returning a default value if no match is found.

    Example
    -------
    >>> from soupsavvy.models import Default
    ... from soupsavvy import TypeSelector
    ... selector = Default(TypeSelector("div"), default="1234")
    ... selector.find(tag)
    "1234"
    """

    def __init__(self, selector: TagSearcher, default: Any) -> None:
        """
        Initializes Default FieldWrapper.

        Parameters
        ----------
        selector : TagSearcher
            The TagSearcher instance to be wrapped.
        default : Any
            The default value to return if no match is found.
        """
        super().__init__(selector)
        self.default = default

    def find(self, tag: Tag, strict, recursive: bool = True):
        """
        Finds an element, returning a default value if None was returned
        by wrapped selector. Any exception raised during the search is propagated.

        Parameters
        ----------
        tag : Tag
            Any BeautifulSoup tag to search within.
        strict : bool, optional
            If True, raises an exception if no matches are found, by default False.
        recursive : bool, optional
            Whether to search recursively, by default True.

        Returns
        -------
        Any
            The found element or the default value if not found.
        """
        result = self.selector.find(tag=tag, strict=strict, recursive=recursive)
        return self.default if result is None else result

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.selector}, default={self.default})"
