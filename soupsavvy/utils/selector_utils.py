"""
Module for utility functions for selectors, used internally across package
to ensure consistent and reliable results.

Classes
-------
- `TagIterator` - Wrapper class for iterating over `IElement`.
- `ElementWrapper` - Wrapper class for `IElement` instances.
- `TagResultSet` - Collection that stores and manages results of selection.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from itertools import chain
from typing import Optional, Self

from soupsavvy.interfaces import IElement


@dataclass
class TagIterator:
    """
    Wrapper class for iterating over `IElement` instances.

    Parameters
    ----------
    tag : IElement
        `IElement` to iterate over.
    recursive : bool, optional
        If True, iterates over all descendants, otherwise only over direct children.
        Default is True.
    include_self : bool, optional
        If True, includes the element itself in iteration, default is False.
    """

    tag: IElement
    recursive: bool = True
    include_self: bool = False

    def _get_iterator(self) -> Iterator:
        """
        Returns iterator over `IElement` descendants or children
        based on recursive parameter value.
        """
        return iter(self.tag.descendants if self.recursive else self.tag.children)

    def __iter__(self) -> Self:
        # Resetting iterator to the beginning.
        iter_ = self._get_iterator()
        self._iter = chain([self.tag], iter_) if self.include_self else iter_
        return self

    def __next__(self) -> IElement:
        """
        Iterates over `IElement` nodes.
        If recursive is set to True, iterates over all descendants,
        otherwise only over direct children.
        """
        return next(self._iter)


@dataclass
class ElementWrapper:
    """
    Wrapper class for `IElement` instances for operations applied in `TagResultSet`.
    Operations such as setting attributes are performed on wrapper,
    and original `IElement` instance is not modified.
    """

    element: IElement

    def __hash__(self):
        """Hashes instance by `IElement` instance hash value."""
        return hash(self.element)

    def __eq__(self, other):
        """Checks equality based on hash value."""
        return isinstance(other, ElementWrapper) and hash(self) == hash(other)


class TagResultSet:
    """
    `TagResultSet` class is collection that stores and manages results of find_all
    method of selectors. Prerequisites for returned results are:
    - `IElement` instances are unique
    - the order of results == order of their appearance in html

    This components consumes optional list of `IElement` instances
    and provides methods for fetching unique results with preserved order.
    It provides operations on sets of results like intersection and union.
    """

    # constants used inside the class
    _ORDER_ATTR = "_order"
    _IS_BASE = "_base"

    def __init__(self, elements: Optional[list[IElement]] = None) -> None:
        """
        Initializes `TagResultSet` instance.

        Parameters
        ----------
        elements : list[IElement], optional
            List of `IElement` instances to store in the collection.
            Default is None, which initializes empty collection.
        """
        self._elements = elements or []

    def fetch(self, n: Optional[int] = None) -> list[IElement]:
        """
        Fetches n first unique `IElement` instances from collection.
        Ensures that the order of the initial list is preserved.

        Parameters
        ----------
        n : int, optional
            Number of `IElement` instances to fetch.
            If default None, fetches all unique instances.

        Returns
        -------
        list[IElement]
            List of `IElement` instances fetched from collection.
        """
        set_ = self._to_set(base=True)
        ordered = self._sort(set_)
        return ordered[:n]

    def _to_set(self, base: bool) -> set[ElementWrapper]:
        """
        Converts list of `IElement` from collection to set of UniqueTag instances.

        Parameters
        ----------
        base : bool
            If True, sets the element as base, otherwise as non-base.
            If TagResultSet is used in set operations as a base, it should be True.

        Returns
        -------
        set[ElementWrapper]
            Set of ElementWrapper instances with set helper attributes.
        """
        elements = [ElementWrapper(element) for element in self._elements]

        for i, element in enumerate(elements):
            # setting attributes used for restoring order
            setattr(element, self._ORDER_ATTR, i)
            setattr(element, self._IS_BASE, int(base))

        return set(elements)

    def _sort(self, it: Iterable[ElementWrapper]) -> list[IElement]:
        """
        Sorts an iterable of `ElementWrapper` instances by order and base attributes.

        Parameters
        ----------
        it : Iterable[ElementWrapper]
            Iterable of `ElementWrapper` instances to sort.

        Returns
        -------
        list[IElement]
            List of `IElement` instances sorted by order and base attributes.
        """
        return [
            unique.element
            for unique in sorted(
                it,
                key=lambda x: (
                    # Sorting by base descending - base goes first
                    -getattr(x, self.__class__._IS_BASE),
                    # Sorting by order ascending
                    getattr(x, self._ORDER_ATTR),
                ),
            )
        ]

    def __and__(self, other: TagResultSet) -> TagResultSet:
        """
        Performs an intersection operation on two `TagResultSet` instances
        with current instance as a base,
        preserving the order of tags from the base instance.

        Parameters
        ----------
        other : TagResultSet
            `TagResultSet` instance to perform intersection with.

        Example
        -------
        >>> base = TagResultSet([x, y, b])
        ... other = TagResultSet([c, y, x])
        ... base & other
        TagResultSet([x, y])

        Returns
        -------
        TagResultSet
            New `TagResultSet` instance with results of intersection operation.
        """
        base = self._to_set(base=True)
        right = other._to_set(base=False)
        # if set intersection, objects are taken from right operant, which messes up the order
        intersection = [obj for obj in base if obj in right]
        ordered = self._sort(intersection)
        return TagResultSet(ordered)

    def __or__(self, other: TagResultSet) -> TagResultSet:
        """
        Performs a union operation on two `TagResultSet` instances
        with current instance list of tags as a base, appending new tags
        from other instance at the end of the list.

        Parameters
        ----------
        other : TagResultSet
            `TagResultSet` instance to perform union with.

        Example
        -------
        >>> base = TagResultSet([x, y, b])
        ... other = TagResultSet([c, y, x])
        ... base | other
        TagResultSet([x, y, b, c])

        Returns
        -------
        TagResultSet
            New `TagResultSet` instance with results of union operation.
        """
        base = self._to_set(base=True)
        right = other._to_set(base=False)
        updated = base | right
        ordered = self._sort(updated)
        return TagResultSet(ordered)

    def __sub__(self, other: TagResultSet) -> TagResultSet:
        """
        Performs a difference operation on two `TagResultSet` instances
        with current instance as a base,
        preserving the order of tags from the base instance.

        Parameters
        ----------
        other : TagResultSet
            `TagResultSet` instance to perform difference with.

        Example
        -------
        >>> base = TagResultSet([x, y, b])
        ... other = TagResultSet([c, y, x])
        ... base - other
        TagResultSet([b])

        Returns
        -------
        TagResultSet
            New TagResultSet instance with results of difference operation.
        """
        base = self._to_set(base=True)
        right = other._to_set(base=False)
        difference = base - right
        ordered = self._sort(difference)
        return TagResultSet(ordered)

    def symmetric_difference(self, other: TagResultSet) -> TagResultSet:
        """
        Performs a symmetric difference operation on two `TagResultSet` instances
        with current instance as a base,
        preserving the order of tags from the base instance.

        Parameters
        ----------
        other : TagResultSet
            `TagResultSet` instance to perform symmetric difference with.

        Example
        -------
        >>> base = TagResultSet([x, y, b])
        ... other = TagResultSet([c, y, x])
        ... base.symmetric_difference(other)
        TagResultSet([b, c])

        Returns
        -------
        TagResultSet
            New `TagResultSet` instance with results of symmetric difference operation.
        """
        base = self._to_set(base=True)
        right = other._to_set(base=False)
        symmetric_diff = base.symmetric_difference(right)
        ordered = self._sort(symmetric_diff)
        return TagResultSet(ordered)

    def __len__(self) -> int:
        """Returns the number of `IElement` instances in the collection."""
        return len(self._elements)

    def __bool__(self) -> bool:
        """Returns True if collection is not empty, otherwise False."""
        return len(self) > 0
