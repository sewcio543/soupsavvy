"""
Module for general purpose operations.

* Operation - Custom operation with any function.
* OperationPipeline - Chain multiple operations together.
* Text - Extract text from a BeautifulSoup Tag - most common operation.

These components are design to be used for processing html tags and extracting
desired information. They can be used in combination with selectors.
"""

from __future__ import annotations

import inspect
from typing import Any, Callable

from bs4 import Tag

import soupsavvy.exceptions as exc
from soupsavvy.operations.base import BaseOperation, check_operator


class OperationPipeline(BaseOperation):
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
    """

    def __init__(
        self,
        operation1: BaseOperation,
        operation2: BaseOperation,
        /,
        *operations: BaseOperation,
    ) -> None:
        """
        Initializes OperationPipeline with multiple operations.

        Parameters
        ----------
        operations : BaseOperation
            BaseOperation instances to be chained together.

        Raises
        ------
        NotOperationException
            If any of the input operations is not a valid operation.
        """
        self.operations = [
            check_operator(operation)
            for operation in (operation1, operation2, *operations)
        ]

    def _execute(self, arg: Any) -> Any:
        """
        Executes each operation in sequence, passing the result to the next one.
        """
        for operation in self.operations:
            arg = operation.execute(arg)
        return arg

    def __or__(self, x: Any) -> OperationPipeline:
        """
        Overrides __or__ method called also by pipe operator '|'.
        Creates new `OperationPipeline` with additional provided operation.

        Parameters
        ----------
        x : BaseOperation
            BaseOperation object used to extend the pipeline.

        Returns
        -------
        OperationPipeline
            New `OperationPipeline` with extended operations.

        Raises
        ------
        NotOperationException
            If provided object is not of type BaseOperation.
        """
        x = check_operator(x)
        return OperationPipeline(*self.operations, x)

    def __eq__(self, x: Any) -> bool:
        # equal only if operations are the same
        if not isinstance(x, OperationPipeline):
            return False

        return self.operations == x.operations


class Operation(BaseOperation):
    """
    Custom operation that wraps any function
    to be used with other `soupsavvy` components.

    Example
    -------
    >>> from soupsavvy.operations import Operation
    ... operation = Operation(str.lower)
    ... operation.execute("TEXT")
    "text"
    """

    def __init__(self, func: Callable) -> None:
        """
        Initializes Operation with a custom function.

        Parameters
        ----------
        func : Callable
            Any callable object that takes not more than one mandatory argument
            and at least one argument in total.

        Raises
        ------
        InvalidOperationFunction
            If the input is not a valid operation callable
        """
        self.operation = self._check_callable(func)

    def _check_callable(self, obj: Any) -> Callable:
        """
        Check if the input is a valid callable that can be used as an operation.
        Input must be callable that takes not more than one mandatory argument
        and at least one argument in total.
        Type is allowed as well, in such case __init__ method is checked.

        Parameters
        ----------
        obj : Any
            Input passed to Operation initialization.

        Returns
        -------
        Callable
            The input callable if it is a valid operation.

        Raises
        ------
        InvalidOperationFunction
            If the input is not valid operation callable.
        """
        if not isinstance(obj, Callable):
            raise exc.InvalidOperationFunction(
                f"Expected Callable as input, got {type(obj)}"
            )

        # if type is passed, check __init__ method
        check = obj.__init__ if isinstance(obj, type) else obj

        signature = inspect.signature(check)
        params = signature.parameters.values()

        if not params:
            raise exc.InvalidOperationFunction(
                "Expected callable with at least one parameter, got none."
            )

        mandatory_keyword_only = [
            p
            for p in params
            if p.default == inspect.Parameter.empty
            and p.kind == inspect.Parameter.KEYWORD_ONLY
        ]

        if mandatory_keyword_only:
            raise exc.InvalidOperationFunction(
                f"Callable with keyword-only without default is not valid."
            )

        mandatory_params = [
            p
            for p in params
            if p.default == inspect.Parameter.empty
            and p.kind
            in {
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.POSITIONAL_ONLY,
            }
        ]

        if len(mandatory_params) > 1:
            # it can be 0 with signature def foo(arg1=1)
            raise exc.InvalidOperationFunction(
                f"Expected callable with one mandatory argument, got {len(mandatory_params)}"
            )

        return obj

    def _execute(self, arg: Any) -> Any:
        """Executes the custom operation."""
        return self.operation(arg)

    def __eq__(self, x: Any) -> bool:
        # functions used as operations need to be the same object
        if not isinstance(x, Operation):
            return False

        return self.operation is x.operation


class Text(BaseOperation):
    """
    Operation to extract text from a BeautifulSoup Tag.
    Wrapper of most common operation used in web scraping.

    Example
    -------
    >>> from soupsavvy.operations import Text
    ... operation = Text()
    ... operation.execute(tag)
    "Extracted text from the tag"

    Wrapper for BeautifulSoup `get_text` method, that exposes all its options,
    and imitates its default behavior.
    """

    def __init__(self, separator: str = "", strip: bool = False) -> None:
        """
        Initializes Text operation with optional separator and strip option.

        Parameters
        ----------
        separator : str, optional
            Separator used to join strings from multiple text nodes, by default "".
        strip : bool, optional
            Flag to strip the text nodes from whitespaces and newline characters,
            by default False.
        """
        self.separator = separator
        self.strip = strip

    def _execute(self, arg: Tag) -> str:
        """Extracts text from a BeautifulSoup Tag."""
        return arg.get_text(separator=self.separator, strip=self.strip)

    def __eq__(self, x: Any) -> bool:
        # equal only if separator and strip are the same
        if not isinstance(x, Text):
            return False

        return self.separator == x.separator and self.strip == x.strip
