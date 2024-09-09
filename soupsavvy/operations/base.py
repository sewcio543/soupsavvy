"""Module for base classes and interfaces for operations."""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Optional

from bs4 import Tag

import soupsavvy.exceptions as exc
from soupsavvy.interfaces import Comparable, Executable, TagSearcher

if TYPE_CHECKING:
    from soupsavvy.operations.general import OperationPipeline


def check_operation(x: Any, message: Optional[str] = None) -> BaseOperation:
    """
    Checks if provided object is a valid `soupsavvy` operation.
    Checks for instance of BaseOperation and raises an exception if not.
    Returns provided object if fulfills the condition for convenience.

    Parameters
    ----------
    x : Any
        Any object to be validated as correct operation.
    message : str, optional
        Custom message to be displayed in case of raising an exception.
        By default None, which results in default message.

    Raises
    ------
    NotOperationException
        If provided object is not an instance of BaseOperation.
    """
    message = message or f"Object {x} is not an instance of {BaseOperation.__name__}."

    if not isinstance(x, BaseOperation):
        raise exc.NotOperationException(message)

    return x


class BaseOperation(Executable, Comparable):
    """
    Base class for all `soupsavvy` operations.
    Operations are used to process the selection results from the soup,
    extract and transform the data.

    Operations can be chained together using the pipe operator '|'.

    Example
    -------
    >>> from soupsavvy.operations.general import Operation
    ... operation = Operation(str.lower) | Operation(str.strip)
    ... operation.execute("  TEXT  ")
    'text'

    Operations can be combined with selectors to extract and transform
    target information.

    Example
    -------
    >>> from soupsavvy import TypeSelector
    ... from soupsavvy.operations import Operation, Text
    ... selector = TypeSelector("div") | Text() | Operation(int)
    ... selector.find(soup)
    42

    BaseOperation inherits from `Comparable` interface, `__eq__` method needs to be
    implemented in derived classes.
    """

    def execute(self, arg: Any) -> Any:
        """
        Execute the operation on the given argument and return the result.

        Parameters
        ----------
        arg : Any
            Argument to be processed by the operation.

        Returns
        -------
        Any
            Result of the operation.
        """
        try:
            return self._execute(arg)
        except Exception as e:
            raise exc.FailedOperationExecution(
                f"Failed to execute operation: {e}"
            ) from e

    @abstractmethod
    def _execute(self, arg: Any) -> Any:
        """Internal method for executing the operation."""

        raise NotImplementedError(
            f"{self.__class__.__name__} is an interface, "
            "and does not implement this method."
        )

    def __or__(self, x: Any) -> OperationPipeline:
        """
        Overrides __or__ method called also by pipe operator '|'.
        Syntactical Sugar for logical disjunction, that creates OperationPipeline,
        which chains two operations together.

        Parameters
        ----------
        x : BaseOperation
            BaseOperation object to be combined into new OperationPipeline.

        Returns
        -------
        OperationPipeline
            New `OperationPipeline` with extended operations.

        Raises
        ------
        NotOperationException
            If provided object is not of type BaseOperation.
        """
        from soupsavvy.operations.general import OperationPipeline

        message = (
            f"Bitwise OR not supported for types {type(self)} and {type(x)}, "
            f"expected an instance of {BaseOperation.__name__}."
        )
        other = check_operation(x, message=message)
        return OperationPipeline(self, other)


class OperationSearcherMixin(BaseOperation, TagSearcher):
    """
    Mixin of `BaseOperation` and `TagSearcher` interfaces.
    Allows operations to be used as field searchers in model
    to perform operation directly on scope element.
    """

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Any]:
        """
        Extracts information from provided element.

        Parameters
        ----------
        tag : Tag
            Any BeautifulSoup Tag object to extract text from.
        recursive : bool, optional
            Ignored, for consistency with interface.
        limit : int, optional
            Ignored, for consistency with interface.

        Returns
        -------
        list[Any]
            Extracted information from the tag.
        """
        return [self.execute(tag)]

    def find(
        self,
        tag: Tag,
        strict: bool = False,
        recursive: bool = True,
    ) -> Any:
        """
        Extracts information from provided element.

        Parameters
        ----------
        tag : Tag
            Any BeautifulSoup Tag object to extract text from.
        strict : bool, optional
            Ignored, for consistency with interface.
        recursive : int, optional
            Ignored, for consistency with interface.

        Returns
        -------
        Any
            Extracted information from the tag.
        """
        return self.execute(tag)
