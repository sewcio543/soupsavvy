"""
Module with `soupsavvy` interfaces used across the package.

- `Executable` - Interface for operations that can be executed on single argument.
- `Comparable` - Interface for objects that can be compared for equality.
- `TagSearcher` - Interface for objects that can search within `bs4.Tag`.
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
        raise NotImplementedError(
            f"{self.__class__.__name__} is an interface "
            "and does not implement this method."
        )


class Comparable(ABC):
    """
    Interface for objects that can be compared for equality.
    Derived classes must implement the `__eq__` method.
    """

    @abstractmethod
    def __eq__(self, x: Any) -> bool:
        raise NotImplementedError(
            f"{self.__class__.__name__} is an interface "
            "and does not implement this method."
        )


# possible exceptions raised when TagSearcher fails
TagSearcherExceptions = (exc.FailedOperationExecution, exc.TagNotFoundException)


class TagSearcher(ABC):
    """
    Interface for objects that can search within `bs4.Tag`.
    Derived classes must implement the `find` and `find_all` methods,
    that process `bs4.Tag` object and return results.
    """

    @abstractmethod
    def find(
        self,
        tag: Tag,
        strict: bool = False,
        recursive: bool = True,
    ) -> Any:
        """
        Processes `bs4.Tag` object and returns result.

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
            Processed result from the tag.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} is an interface "
            "and does not implement this method."
        )

    @abstractmethod
    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Any]:
        """
        Processes `bs4.Tag` object and returns list of results.

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
            A list of results from processed tag.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} is an interface "
            "and does not implement this method."
        )
