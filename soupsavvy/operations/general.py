"""
Module for general purpose operations.

Classes
-------
- `Operation` - Executes custom operation with any function.
- `OperationPipeline` - Chains multiple operations together.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import soupsavvy.exceptions as exc
from soupsavvy.base import BaseOperation, OperationSearcherMixin, check_operation


class OperationPipeline(OperationSearcherMixin):
    """
    Pipeline for chaining multiple operations together.
    Applies each operation in sequence, passing the result to the next.

    Example
    -------
    >>> from soupsavvy.operations import Operation
    ... pipeline = Operation(int) | Operation(lambda x: x + 1)
    ... pipeline.execute("1")
    2

    Most common way of creating a pipeline is using the `|` operator
    on two operations.

    `OperationPipeline` is operation-searcher mixin, which means it can be used
    to find information in `IElement` object directly with find methods.
    This way, it can be used as field in model or `execute` method can be replaced
    with `find` method, which would produce the same result.
    """

    def __init__(
        self,
        operation1: BaseOperation,
        operation2: BaseOperation,
        /,
        *operations: BaseOperation,
    ) -> None:
        """
        Initializes `OperationPipeline` with multiple operations.

        Parameters
        ----------
        operations : BaseOperation
            `BaseOperation` instances to be chained together.

        Raises
        ------
        NotOperationException
            If any of the input operations is not an instance of `BaseOperation`.
        """
        self.operations = [
            check_operation(operation)
            for operation in (operation1, operation2, *operations)
        ]

    def _execute(self, arg: Any) -> Any:
        """
        Executes each operation in sequence, passing the result to the next one.
        If operation is breaking, returns the result immediately.
        """
        for operation in self.operations:

            try:
                arg = operation.execute(arg)
            except exc.BreakOperationException as e:
                return e.result

        return arg

    def __or__(self, x: Any) -> OperationPipeline:
        """
        Overrides `__or__` method called also by pipe operator '|'.
        Creates new `OperationPipeline` object extended by provided operation.

        Parameters
        ----------
        x : BaseOperation
            `BaseOperation` object used to extend the pipeline.

        Returns
        -------
        OperationPipeline
            New `OperationPipeline` with extended operations.

        Raises
        ------
        NotOperationException
            If provided object is not an instance of `BaseOperation`.
        """
        x = check_operation(x)
        return OperationPipeline(*self.operations, x)

    def __eq__(self, x: Any) -> bool:
        # equal only if operations are the same
        if not isinstance(x, self.__class__):
            return NotImplemented

        return self.operations == x.operations

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.operations})"


class Operation(OperationSearcherMixin):
    """
    Custom operation that wraps any function
    to be used with other `soupsavvy` components.

    Example
    -------
    >>> from soupsavvy.operations import Operation
    ... operation = Operation(str.lower)
    ... operation.execute("TEXT")
    "text"

    `Operation` is operation-searcher mixin, which means it can be used
    to find information in `IElement` directly with find methods.
    This way, it can be used as field in model or `execute` method can be replaced
    with `find` method, which would produce the same result.
    """

    def __init__(self, func: Callable, *args, **kwargs) -> None:
        """
        Initializes `Operation` with provided function and optional arguments.

        Parameters
        ----------
        func : Callable
            Any callable object that can be called with one positional argument.
        *args : Any
            Additional positional arguments passed to the operation function.
        **kwargs : Any
            Additional keyword arguments passed to the operation function.
        """
        self.operation = func
        self.args = args
        self.kwargs = kwargs

    def _execute(self, arg: Any) -> Any:
        """Executes the custom operation."""
        return self.operation(arg, *self.args, **self.kwargs)

    def __eq__(self, x: Any) -> bool:
        # functions used as operations need to be the same object
        # and have the same function arguments if provided
        if not isinstance(x, self.__class__):
            return NotImplemented

        return (
            self.operation is x.operation
            and self.args == x.args
            and self.kwargs == x.kwargs
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.operation})"
