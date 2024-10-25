"""
Module with `soupsavvy` interfaces used across the package.

- `Executable` - Interface for operations that can be executed on single argument.
- `Comparable` - Interface for objects that can be compared for equality.
- `TagSearcher` - Interface for objects that can search within `bs4.Tag`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable
from typing import Any, Generic, Optional, Pattern, TypeVar, Union

import soupsavvy.exceptions as exc

try:
    from lxml.etree import _Element as HtmlElement
except ImportError as e:
    pass


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


T = TypeVar("T", bound="IElement")


class IElement(ABC, Generic[T]):
    @abstractmethod
    def find_all(
        self,
        name: Optional[str] = None,
        attrs: Optional[dict[str, Union[str, Pattern[str]]]] = None,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[T]:
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def find_next_siblings(self, limit: Optional[int] = None) -> list[T]:
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def find_ancestors(self, limit: Optional[int] = None) -> list[T]:
        raise NotImplementedError("Method not implemented")

    @property
    @abstractmethod
    def children(self) -> Iterable[T]:
        raise NotImplementedError("Method not implemented")

    @property
    @abstractmethod
    def descendants(self) -> Iterable[T]:
        raise NotImplementedError("Method not implemented")

    @property
    @abstractmethod
    def parent(self) -> Optional[T]:
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def get_text(self, separator: str = "", strip: bool = False) -> str:
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

    def to_lxml(self) -> HtmlElement:
        raise NotImplementedError("Method not implemented")

    def prettify(self) -> str:
        return str(self)

    def css(self, selector: str) -> Callable[[IElement], list[IElement]]:
        raise NotImplementedError("Method not implemented")
