"""
Module with `soupsavvy` interfaces used across the package.

* `Executable` - Interface for operations that can be executed on single argument.
* `Comparable` - Interface for objects that can be compared for equality.
* `TagSearcher` - Interface for objects that can search within BeautifulSoup tags.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional

from bs4 import Tag

import soupsavvy.exceptions as exc


class Executable(ABC):
    """
    Interface for operations that can be executed on single argument.
    Derived classes must implement the `execute` method.
    """

    @abstractmethod
    def execute(self, arg: Any) -> Any:
        """Executes the operation on the given argument."""
        pass


class Comparable(ABC):
    """
    Interface for objects that can be compared for equality.
    Derived classes must implement the `__eq__` method.
    """

    @abstractmethod
    def __eq__(self, x: Any) -> bool:
        pass


# possible exceptions raised when TagSearcher fails
TagSearcherExceptions = (exc.FailedOperationExecution, exc.TagNotFoundException)


class TagSearcher(ABC):
    """
    Interface for objects that can search within BeautifulSoup tags.
    """

    @abstractmethod
    def find(
        self,
        tag: Tag,
        strict: bool = False,
        recursive: bool = True,
    ) -> Any:
        """
        Finds first target information within the given tag and returns the result.

        Parameters
        ----------
        tag : Tag
            Any BeautifulSoup Tag object.
        strict : bool, optional
            If True, enforces results to be found in the tag, by default False.
        recursive : bool, optional
            bs4.Tag.find method parameter that specifies if search should be recursive.
            If set to False, only direct children of the tag will be searched.
            By default True.

        Returns
        -------
        Any
            Result of the search operation.
        """

    @abstractmethod
    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Any]:
        """
        Finds all target information within the given tag and returns the result.

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
