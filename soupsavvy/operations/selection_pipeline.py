"""
Module with selection pipeline class.
Pipeline for chaining selector and operation together, used as a bridge between
selecting html elements and processing the data.
"""

from __future__ import annotations

from typing import Any, Optional

from soupsavvy.base import BaseOperation, check_operation, check_tag_searcher
from soupsavvy.interfaces import Comparable, IElement, TagSearcher, TagSearcherType


class SelectionPipeline(TagSearcher, Comparable):
    """
    Class for chaining searcher and operation together.
    Uses searcher to find information in element and operation to process the data.

    Example
    -------
    >>> from soupsavvy import TypeSelector
    ... from soupsavvy.operations import Operation, Text
    ... pipeline = TypeSelector("span") | Text()
    ... pipeline.find(soup)
    'information'

    Most common way of creating a pipeline is using the `|` operator
    on selector and operation.
    """

    def __init__(self, selector: TagSearcherType, operation: BaseOperation) -> None:
        """
        Initializes `SelectionPipeline` with selector and operation.

        Parameters
        ----------
        selector : TagSearcher
            Selector used for finding target information in the element.
        operation : BaseOperation
            Operation used for processing the data.

        Raises
        ------
        NotTagSearcherException
            If provided selector is not a valid `TagSearcher` instance.
        NotOperationException
            If provided operation is not a valid `BaseOperation` instance.
        """
        self._selector = check_tag_searcher(selector)
        self._operation = check_operation(operation)

    @property
    def selector(self) -> TagSearcher:
        """
        Returns `TagSearcher` object of this pipeline used for finding target
        information in the element.

        Returns
        -------
        TagSearcher
            TagSearcher object used in this pipeline.
        """
        return self._selector

    @property
    def operation(self) -> BaseOperation:
        """
        Returns `BaseOperation` object of this pipeline used for processing the data.

        Returns
        -------
        BaseOperation
            BaseOperation object used in this pipeline.
        """
        return self._operation

    def find(
        self,
        tag: IElement,
        strict: bool = False,
        recursive: bool = True,
    ) -> Any:
        """
        Finds a first element matching selector and processes it with operation.

        Parameters
        ----------
        tag : IElement
            Any `IElement` object to process.
        strict : bool, optional
            If True, enforces results to be found in the element, by default False.
        recursive : bool, optional
            Specifies if search should be recursive.
            If set to `False`, only direct children of the element will be searched.
            By default `True`.

        Returns
        -------
        Any
            Result of the operation applied to the found element.

        Raises
        ------
        TagNotFoundException
            If strict parameter is set to `True` and none matching element was found.
        FailedOperationExecution
            If operation execution failed on the found element.
        """
        return self.operation.execute(
            self.selector.find(tag, strict=strict, recursive=recursive)
        )

    def find_all(
        self,
        tag: IElement,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Any]:
        """
        Finds all elements matching selector and processes them with operation.

        Parameters
        ----------
        tag : IElement
            Any `IElement` object to process.
        recursive : bool, optional
            Specifies if search should be recursive.
            If set to `False`, only direct children of the element will be searched.
            By default `True`.
        limit : int, optional
            Specifies maximum number of results to return in a list.
            By default `None`, everything is returned.

        Returns
        -------
        list[Any]
            A list of results, if none found, the list is empty.

        Raises
        ------
        FailedOperationExecution
            If operation execution failed on any of the found elements.
        """
        return [
            self.operation.execute(element)
            for element in self.selector.find_all(tag, recursive=recursive, limit=limit)
        ]

    def __or__(self, x: Any) -> SelectionPipeline:
        """
        Overrides `__or__` method called also by pipe operator '|'.
        Creates new `SelectionPipeline` by extending operations with provided one.

        Parameters
        ----------
        x : BaseOperation
            `BaseOperation` object used to extend the pipeline.

        Returns
        -------
        SelectionPipeline
            New `SelectionPipeline` with extended operations.

        Raises
        ------
        NotOperationException
            If provided object is not an instance of `BaseOperation`.
        """
        x = check_operation(x)
        operation = self.operation | x
        return SelectionPipeline(selector=self.selector, operation=operation)

    def __eq__(self, x) -> bool:
        # equal only if both selector and operation are the same
        if not isinstance(x, self.__class__):
            return NotImplemented

        return self.selector == x.selector and self.operation == x.operation

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.selector}, {self.operation})"
