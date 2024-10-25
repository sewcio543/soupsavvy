"""
Module with selection pipeline class.
Pipeline for chaining selector and operation together, used as a bridge between
selecting html elements and processing the data.
"""

from __future__ import annotations

from typing import Any, Optional

import soupsavvy.exceptions as exc
from soupsavvy.base import BaseOperation, check_operation
from soupsavvy.interfaces import Comparable, IElement, TagSearcher


class SelectionPipeline(TagSearcher, Comparable):
    """
    Class for chaining searcher and operation together.
    Uses searcher to find information in tag and operation to process the data.

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

    def __init__(self, selector: TagSearcher, operation: BaseOperation) -> None:
        """
        Initializes `SelectionPipeline` with selector and operation.

        Parameters
        ----------
        selector : TagSearcher
            Selector used for finding target information in the tag.
        operation : BaseOperation
            Operation used for processing the data.
        """
        if not isinstance(selector, TagSearcher):
            raise exc.NotTagSearcherException(
                f"Expected {TagSearcher.__name__}, got {type(selector)}"
            )

        self._selector = selector
        self._operation = operation

    @property
    def selector(self) -> TagSearcher:
        """
        Returns `TagSearcher` object of this pipeline used for finding target
        information in the tag.

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
        tag : Tag
            Any `bs4.Tag` object to process.
        strict : bool, optional
            If True, enforces results to be found in the tag, by default False.
        recursive : bool, optional
            Specifies if search should be recursive.
            If set to `False`, only direct children of the tag will be searched.
            By default `True`.

        Returns
        -------
        Any
            Result of the operation applied to the found tag.

        Raises
        ------
        TagNotFoundException
            If strict parameter is set to `True` and none matching tag was found.
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
        tag : Tag
            Any `bs4.Tag` object to process.
        recursive : bool, optional
            Specifies if search should be recursive.
            If set to `False`, only direct children of the tag will be searched.
            By default `True`.
        limit : int, optional
            Specifies maximum number of results to return in a list.
            By default `None`, everything is returned.

        Returns
        -------
        list[Any]
            A list of results, if none found, the list is empty.
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
        if not isinstance(x, SelectionPipeline):
            return False

        return self.selector == x.selector and self.operation == x.operation

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.selector}, {self.operation})"
