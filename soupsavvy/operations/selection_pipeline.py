"""
Module for selection pipeline class.
Pipeline for chaining selector and operation together, used as a bridge between
selecting html elements and processing the data.
"""

from __future__ import annotations

from typing import Any, Optional

from bs4 import Tag

import soupsavvy.exceptions as exc
from soupsavvy.base import BaseOperation, check_operation
from soupsavvy.interfaces import Comparable, TagSearcher


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
        Initializes SelectionPipeline with selector and operation.

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
        Returns TagSearcher object of this pipeline used for finding target
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
        Returns BaseOperation object of this pipeline used for processing the data.

        Returns
        -------
        BaseOperation
            BaseOperation object used in this pipeline.
        """
        return self._operation

    def find(
        self,
        tag: Tag,
        strict: bool = False,
        recursive: bool = True,
    ) -> Any:
        """
        Finds a first element matching selector and processes it with operation.

        Parameters
        ----------
        tag : Tag
            Any BeautifulSoup Tag object.
        strict : bool, optional
            If True, raises an exception if tag was not found in markup,
            if False and tag was not found, returns None by defaulting to BeautifulSoup
            implementation. Value of this parameter does not affect behavior if tag
            was successfully found in the markup. By default False.
        recursive : bool, optional
            bs4.Tag.find method parameter that specifies if search should be recursive.
            If set to False, only direct children of the tag will be searched.
            By default True.

        Returns
        -------
        Any
            Result of the operation applied to the found tag.

        Raises
        ------
        TagNotFoundException
            If strict parameter is set to True and tag was not found in markup.
        """
        return self.operation.execute(
            self.selector.find(tag, strict=strict, recursive=recursive)
        )

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Any]:
        """
        Finds all elements matching selector and processes them with operation.

        Parameters
        ----------
        tag : Tag
            Any BeautifulSoup Tag object.
        recursive : bool, optional
            bs4.Tag.find method parameter that specifies if search should be recursive.
            If set to False, only direct children of the tag will be searched.
            By default True.
        limit : int, optional
            bs4.Tag.find_all method parameter that specifies maximum number of results
            to return. If set to None, all results are returned. By default None.

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
        Overrides __or__ method called also by pipe operator '|'.
        Creates new SelectionPipeline by extending operations with provided one.

        Parameters
        ----------
        x : BaseOperation
            BaseOperation object used to extend the pipeline.

        Returns
        -------
        SelectionPipeline
            New `SelectionPipeline` with extended operations.

        Raises
        ------
        NotOperationException
            If provided object is not of type BaseOperation.
        """
        x = check_operation(x)
        operation = self.operation | x
        return SelectionPipeline(selector=self.selector, operation=operation)

    def __eq__(self, x) -> bool:
        # equal only if both selector and operation are the same
        if not isinstance(x, SelectionPipeline):
            return False

        return self.selector == x.selector and self.operation == x.operation
