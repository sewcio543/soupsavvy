"""
Module with `soupsavvy` interfaces used across the package.

- `Executable` - Interface for operations that can be executed on single argument.
- `Comparable` - Interface for objects that can be compared for equality.
- `TagSearcher` - Interface for objects that can search within `bs4.Tag`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any, Optional, Pattern, Self, TypeVar, Union

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
        tag: IElement,
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
        tag: IElement,
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


class IElement(ABC):
    @abstractmethod
    def find_all(
        self,
        name: Optional[str] = None,
        attrs: Optional[dict[str, Union[str, Pattern[str]]]] = None,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Self]:
        raise NotImplementedError("Method not implemented")

    @classmethod
    def from_node(cls, node: Any) -> Self:
        raise NotImplementedError("Method not implemented")

    @property
    def node(self) -> Any:
        return None

    def get(self) -> Any:
        return self.node

    @abstractmethod
    def find_next_siblings(self, limit: Optional[int] = None) -> list[Self]:
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def find_ancestors(self, limit: Optional[int] = None) -> list[Self]:
        raise NotImplementedError("Method not implemented")

    @property
    @abstractmethod
    def children(self) -> Iterable[Self]:
        raise NotImplementedError("Method not implemented")

    @property
    @abstractmethod
    def descendants(self) -> Iterable[Self]:
        raise NotImplementedError("Method not implemented")

    @property
    @abstractmethod
    def parent(self) -> Optional[Self]:
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def get_attribute_list(self, name: str) -> list[str]:
        raise NotImplementedError("Method not implemented")

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError("Method not implemented")

    @property
    @abstractmethod
    def text(self) -> str:
        raise NotImplementedError("Method not implemented")

    def prettify(self) -> str:
        return str(self)

    def css(self, selector) -> SelectionApi:
        raise NotImplementedError("Method not implemented")

    def xpath(self, selector) -> SelectionApi:
        raise NotImplementedError("Method not implemented")


class SelectionApi(ABC):
    def __init__(self, selector) -> None:
        self.selector = selector

    @abstractmethod
    def select(self, element: IElement) -> list[IElement]:
        raise NotImplementedError("Method not implemented")


Element = TypeVar("Element", bound=IElement)
