"""
Module for general purpose operations.

* Operation - Custom operation with any function.
* OperationPipeline - Chain multiple operations together.
* Text - Extract text from a BeautifulSoup Tag - most common operation.

These components are design to be used for processing html tags and extracting
desired information. They can be used in combination with selectors.
"""

from __future__ import annotations

from typing import Any, Callable, Optional

from bs4 import Tag

from soupsavvy.interfaces import TagSearcher
from soupsavvy.operations.base import BaseOperation, check_operation


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
            check_operation(operation)
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
        x = check_operation(x)
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
            Any callable object that can be called with one positional argument.
        """
        self.operation = func

    def _execute(self, arg: Any) -> Any:
        """Executes the custom operation."""
        return self.operation(arg)

    def __eq__(self, x: Any) -> bool:
        # functions used as operations need to be the same object
        if not isinstance(x, Operation):
            return False

        return self.operation is x.operation


class Text(BaseOperation, TagSearcher):
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

    Implements `TagSearcher` interface for convenience. It has find methods
    that can be used to extract text from a tag.

    Example
    -------
    >>> from soupsavvy.operations import Text
    ... operation = Text()
    ... operation.find(tag)
    "Text"
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

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[str]:
        """
        Extracts text from provided element. Always returns a single
        element list with the extracted text.

        Parameters
        ----------
        tag : Tag
            Any BeautifulSoup Tag object to extract text from.
        recursive : bool, optional
            Ignored, for consistency with interface.
        limit : int, optional
            Ignored, for consistency with interface, always returns a single string.

        Returns
        -------
        list[str]
            Extracted text from the tag, wrapped in a single element list.
        """
        return [self.execute(tag)]

    def find(
        self,
        tag: Tag,
        strict: bool = False,
        recursive: bool = True,
    ) -> Any:
        """
        Extracts text from provided element. Always returns a single string.

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
        str
            Extracted text from the tag.
        """
        return self.execute(tag)

    def _execute(self, arg: Tag) -> str:
        """Extracts text from a BeautifulSoup Tag."""
        return arg.get_text(separator=self.separator, strip=self.strip)

    def __eq__(self, x: Any) -> bool:
        # equal only if separator and strip are the same
        if not isinstance(x, Text):
            return False

        return self.separator == x.separator and self.strip == x.strip
