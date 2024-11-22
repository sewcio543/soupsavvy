"""
Module with `soupsavvy` interfaces used across the package.

- `Executable` - Interface for operations that can be executed on single argument.
- `Comparable` - Interface for objects that can be compared for equality.
- `TagSearcher` - Interface for objects that can search within `IElement`.
- `IElement` - Interface for any tree structure compatible with `soupsavvy`.
- `SelectionApi` - Interface for selection of elements based on specific selector.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any, NoReturn, Optional, Pattern, Union

from typing_extensions import Self

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
    Interface for objects that can search within `IElement`.
    Derived classes must implement the `find` and `find_all` methods,
    that process `IElement` object and return results.
    """

    @abstractmethod
    def find(
        self,
        tag: IElement,
        strict: bool = False,
        recursive: bool = True,
    ) -> Any:
        """
        Processes `IElement` object and returns result.

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
            Processed result from the element.
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
        Processes `IElement` object and returns list of results.

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
            A list of results from processed element.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} is an interface "
            "and does not implement this method."
        )


class IElement(ABC):
    """
    Interface representing a general HTML node within a tree structure.
    `IElement` defines methods for common DOM operations, such as searching for elements,
    retrieving attributes, and navigating between nodes.

    This interface enables consistent access to various HTML-parsing libraries or
    custom tree structures. Any implementation should wrap a node-like structure
    and allow `soupsavvy` components to operate on it seamlessly.

    Current Implementations:
    - `SoupElement`: Wraps a `BeautifulSoup` node.
    - `LXMLElement`: Wraps an `lxml` node.
    - `SeleniumElement`: Wraps a `Selenium WebElement`.
    """

    _NOT_IMPLEMENTED_MESSAGE = (
        "IElement is an abstract interface and does not implement this method."
    )
    _NODE_TYPE: type[Any] = object

    def __init__(self, node: Any, *args, **kwargs) -> None:
        """
        Initializes the implementation with the given node.

        Parameters
        ----------
        node : Any
            Node to wrap for specific implementation.
        *args: Any
            Additional positional arguments to pass to the constructor.
        **kwargs: Any
            Additional keyword arguments to pass to the constructor.
        """
        if not isinstance(node, self._NODE_TYPE):
            raise TypeError(
                f"Expected node to be of type {self._NODE_TYPE}, "
                f"but got {type(node)} instead."
            )

        self._node = node

    @classmethod
    def from_node(cls, node: Any) -> Self:
        """
        Creates a new instance of the implementation from a node.

        Parameters
        ----------
        node : Any
            Node to wrap for specific implementation.

        Returns
        -------
        Self
            New instance of the implementation with the given node.
        """
        return cls(node)

    @abstractmethod
    def find_all(
        self,
        name: Optional[str] = None,
        attrs: Optional[dict[str, Union[str, Pattern[str]]]] = None,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Self]:
        """
        Finds all elements that match specified element name and attributes.

        Parameters
        ----------
        name : str, optional
            Name of the element to search for. If `None`, matches all elements.
        attrs : dict[str, str | Pattern[str]], optional
            Dictionary of attributes to match. Supports exact matches and regex patterns.
        recursive : bool, optional
            If `True`, searches recursively through all descendants.
            If `False`, searches only direct children.
        limit : int, optional
            Maximum number of elements to return. If `None`, returns all matching elements.

        Returns
        -------
        list[Self]
            List of elements that match the criteria, in depth-first order.
        """
        self._raise_not_implemented()

    @property
    def node(self) -> Any:
        """Returns the underlying node wrapped by the instance."""
        return self._node

    def get(self) -> Any:
        """Returns the node wrapped by the instance."""
        return self.node

    @abstractmethod
    def find_subsequent_siblings(self, limit: Optional[int] = None) -> list[Self]:
        """
        Finds siblings that follow this node in the document structure.

        Parameters
        ----------
        limit : int, optional
            Maximum number of sibling nodes to return. If `None`, returns all siblings.

        Returns
        -------
        list[Self]
            List of subsequent sibling elements, in document order.
        """
        self._raise_not_implemented()

    @abstractmethod
    def find_ancestors(self, limit: Optional[int] = None) -> list[Self]:
        """
        Finds all ancestor nodes up to the root of the document.

        Parameters
        ----------
        limit : int, optional
            Maximum number of ancestors to return, starting from the closest ancestor.
            If `None`, returns all ancestors.

        Returns
        -------
        list[Self]
            List of ancestor nodes, from nearest to root.
        """
        self._raise_not_implemented()

    @property
    @abstractmethod
    def children(self) -> Iterable[Self]:
        """
        Returns an iterable of the direct child elements of this node.

        Notes
        -----
        Only tag elements are included; text and comment nodes are excluded.

        Returns
        -------
        Iterable[Self]
            Iterable of direct child nodes, in document order.
        """
        self._raise_not_implemented()

    @property
    @abstractmethod
    def descendants(self) -> Iterable[Self]:
        """
        Returns an iterable of all descendant nodes of this node.

        Notes
        -----
        Only tag elements are included; text and comment nodes are excluded.
        Nodes are returned in depth-first order.

        Returns
        -------
        Iterable[Self]
            Iterable of all descendant nodes.
        """
        self._raise_not_implemented()

    @property
    @abstractmethod
    def parent(self) -> Optional[Self]:
        """
        Returns the immediate parent node of this element, if it exists.

        Returns
        -------
        Optional[Self]
            The parent element, or `None` if this is the root node.
        """
        self._raise_not_implemented()

    @abstractmethod
    def get_attribute(self, name: str) -> Optional[str]:
        """
        Retrieves the value of a specified attribute for this node.

        Parameters
        ----------
        name : str
            Name of the attribute.

        Returns
        -------
        Optional[str]
            The attribute value as a string, or `None` if the attribute does not exist.
        """
        self._raise_not_implemented()

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the tag name of this element."""
        self._raise_not_implemented()

    @property
    @abstractmethod
    def text(self) -> str:
        """
        Gets the combined text content of this element.

        Notes
        -----
        Concatenates all text nodes within this element. The format may vary
        slightly across implementations depending on handling of whitespace or
        nested elements.

        Returns
        -------
        str
            Text content of this element, or an empty string if none is found.
        """
        self._raise_not_implemented()

    def css(self, selector: Any) -> SelectionApi:
        """
        Returns a `SelectionApi` for CSS-based selection.

        Parameters
        ----------
        selector : Any
            The CSS selector to apply.

        Returns
        -------
        SelectionApi
            Initialized `SelectionApi` instance for CSS selection.
        """
        self._raise_not_implemented()

    def xpath(self, selector) -> SelectionApi:
        """
        Returns a `SelectionApi` for XPath-based selection.

        Parameters
        ----------
        selector : Any
            The XPath selector to apply.

        Returns
        -------
        SelectionApi
            Initialized `SelectionApi` instance for XPath selection.
        """
        self._raise_not_implemented()

    @classmethod
    def _raise_not_implemented(cls) -> NoReturn:
        """Raises a `NotImplementedError` indicating that this method is abstract."""
        raise NotImplementedError(cls._NOT_IMPLEMENTED_MESSAGE)

    @classmethod
    def _map(cls, elements: Iterable[Any]) -> Iterable[Self]:
        """Maps elements to the current implementation."""
        return map(cls, elements)

    def __hash__(self):
        """Hashes element object using the wrapped node's hash."""
        return hash(self._node)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.node is other.node

    def __str__(self) -> str:
        return str(self._node)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._node!r})"


class SelectionApi(ABC):
    """
    Interface for selecting elements based on a specific selector.

    `SelectionApi` is designed to handle complex CSS or XPath selections,
    simplifying element matching across various document structures.
    Implementing classes should define `select` for element matching.
    """

    def __init__(self, selector: Any) -> None:
        """
        Initializes `SelectionApi` with given selector.

        Parameters
        ----------
        selector : Any
            The selector used for locating elements.
        """
        self.selector = selector

    @abstractmethod
    def select(self, element: IElement) -> list[IElement]:
        """
        Selects elements within a given node that match the selector.

        Parameters
        ----------
        element : IElement
            The element to search within.

        Returns
        -------
        list[IElement]
            A list of elements matching the selector within the provided element.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} is abstract and does not implement select method."
        )
