"""Module for utility functions for tag selectors."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from itertools import chain
from typing import Optional

from bs4 import Tag


@dataclass
class TagIterator:
    """
    Wrapper class for iterating over bs4.Tag.

    Parameters
    ----------
    tag : Tag
        BeautifulSoup Tag to iterate over.
    recursive : bool, optional
        If True, iterates over all descendants, otherwise only over direct children.
        Default is True, similar to bs4 implementation.
    include_self : bool, optional
        If True, includes the tag itself in iteration, default is False.
    """

    tag: Tag
    recursive: bool = True
    include_self: bool = False

    def _get_iterator(self) -> Iterator:
        """
        Returns iterator over bs4.Tag descendants or children
        based on recursive parameter value.
        """
        return iter(self.tag.descendants if self.recursive else self.tag.children)

    def __iter__(self) -> TagIterator:
        # Resetting iterator to the beginning.
        iter_ = self._get_iterator()
        self._iter = chain([self.tag], iter_) if self.include_self else iter_
        return self

    def __next__(self) -> Tag:
        """
        Iterates over bs4.Tag skipping all strings (not bs4.Tag).
        If recursive is set to True, iterates over all descendants,
        otherwise only over direct children.
        """
        value = next(self._iter)

        while not isinstance(value, Tag):
            value = next(self._iter)

        return value


class UniqueTag:
    """
    Wrapper class for bs4.Tag to make it hashable by id.
    Hashing in bs4.Tag is implemented through hash of string representation:
    >>> str(self).__hash__()
    Two different bs4.Tag instances with the same content have the same hash,
    which is the root of the problem when operating with sets of bs4.Tag instances.

    Class uses composition over inheritance which makes it responsible
    only for hashing and equality check.

    Class is used in Selectors that use operations on sets of bs4.Tag instances.
    """

    def __init__(self, tag: Tag):
        """
        Initializes UniqueTag instance.

        Parameters
        ----------
        tag : bs4.Tag
            BeautifulSoup Tag instance to wrap.
        """
        self.tag = tag

    def __hash__(self):
        """Hashes bs4.Tag instance by id."""
        return id(self.tag)

    def __eq__(self, other):
        """
        Checks equality of itself with another object.

        For object to be equal to UniqueTag, it should be an instance of UniqueTag
        and have the same hash value, meaning it has to wrap the same bs4.Tag instance.
        In any other case, returns False.
        """
        return isinstance(other, UniqueTag) and hash(self) == hash(other)

    def __str__(self):
        """Returns string representation of UniqueTag instance."""
        return f"{self.__class__.__name__}({id(self.tag)})"


class TagResultSet:
    """
    TagResultSet class is collection that stores and manages results of find_all
    method of selectors. Prerequisites for returned results are:
    - bs4.Tag instances are unique
    - the order of results == order of their appearance in html

    This components consumes list of bs4.Tag instances and provides methods
    for fetching unique results with preserved order.
    It provides operations on sets of results like intersection and union.
    """

    # constants used inside the class
    _ORDER_ATTR = "_order"
    _IS_BASE = "_base"

    def __init__(self, tags: Optional[list[Tag]] = None) -> None:
        """
        Initializes `TagResultSet` instance.

        Parameters
        ----------
        tags : list[Tag], optional
            List of bs4.Tag instances to store in the collection.
            Default is None, which initializes empty collection.
        """
        self._tags = tags or []

    def fetch(self, n: Optional[int] = None) -> list[Tag]:
        """
        Fetches n first unique bs4.Tag instances from collection.
        Ensures that the order of the initial list is preserved.

        Parameters
        ----------
        n : int, optional
            Number of bs4.Tag instances to fetch.
            If default None, fetches all unique bs4.Tag instances.

        Returns
        -------
        list[Tag]
            List of bs4.Tag instances fetched from collection.
        """
        set_ = self._to_set(base=True)
        ordered = self._sort(set_)
        return ordered[:n]

    def _to_set(self, base: bool) -> set[UniqueTag]:
        """
        Converts list of bs4.Tags from collection to set of UniqueTag instances.

        Parameters
        ----------
        base : bool
            If True, sets the tag as base, otherwise as non-base.
            If TagResultSet is used in set operations as a base, it should be True.

        Returns
        -------
        set[UniqueTag]
            Set of UniqueTag instances with set helper attributes.
        """
        # converting to UniqueTag instances due to known hashing issue
        tags = [UniqueTag(tag) for tag in self._tags]

        for i, tag in enumerate(tags):
            # setting attributes used for restoring order
            setattr(tag, self._ORDER_ATTR, i)
            setattr(tag, self._IS_BASE, int(base))

        return set(tags)

    def _sort(self, it: Iterable[UniqueTag]) -> list[Tag]:
        """
        Sorts an iterable of UniqueTag instances by order and base attributes.

        Parameters
        ----------
        it : Iterable[UniqueTag]
            Iterable of UniqueTag instances to sort.

        Returns
        -------
        list[Tag]
            List of bs4.Tag instances sorted by order and base attributes.
        """
        return [
            unique.tag
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
        Performs an intersection operation on two TagResultSet instances
        with current instance as a base,
        preserving the order of tags from the base instance.

        Parameters
        ----------
        other : TagResultSet
            TagResultSet instance to perform intersection with.

        Example
        -------
        >>> base = TagResultSet([x, y, b])
        ... other = TagResultSet([c, y, x])
        ... base & other
        TagResultSet([x, y])

        Returns
        -------
        TagResultSet
            New TagResultSet instance with results of intersection operation.
        """
        base = self._to_set(base=True)
        right = other._to_set(base=False)
        # if set intersection, objects are taken from right operant, which messes up the order
        intersection = [obj for obj in base if obj in right]
        ordered = self._sort(intersection)
        return TagResultSet(ordered)

    def __or__(self, other: TagResultSet) -> TagResultSet:
        """
        Performs a union operation on two TagResultSet instances
        with current instance list of tags as a base, appending new tags
        from other instance at the end of the list.

        Parameters
        ----------
        other : TagResultSet
            TagResultSet instance to perform union with.

        Example
        -------
        >>> base = TagResultSet([x, y, b])
        ... other = TagResultSet([c, y, x])
        ... base | other
        TagResultSet([x, y, b, c])

        Returns
        -------
        TagResultSet
            New TagResultSet instance with results of union operation.
        """
        base = self._to_set(base=True)
        right = other._to_set(base=False)
        updated = base | right
        ordered = self._sort(updated)
        return TagResultSet(ordered)

    def __sub__(self, other: TagResultSet) -> TagResultSet:
        """
        Performs a difference operation on two TagResultSet instances
        with current instance as a base,
        preserving the order of tags from the base instance.

        Parameters
        ----------
        other : TagResultSet
            TagResultSet instance to perform difference with.

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
        Performs a symmetric difference operation on two TagResultSet instances
        with current instance as a base,
        preserving the order of tags from the base instance.

        Parameters
        ----------
        other : TagResultSet
            TagResultSet instance to perform symmetric difference with.

        Example
        -------
        >>> base = TagResultSet([x, y, b])
        ... other = TagResultSet([c, y, x])
        ... base.symmetric_difference(other)
        TagResultSet([b, c])

        Returns
        -------
        TagResultSet
            New TagResultSet instance with results of symmetric difference operation.
        """
        base = self._to_set(base=True)
        right = other._to_set(base=False)
        symmetric_diff = base.symmetric_difference(right)
        ordered = self._sort(symmetric_diff)
        return TagResultSet(ordered)

    def __len__(self) -> int:
        """Returns the number of bs4.Tag instances in the collection."""
        return len(self._tags)

    def __bool__(self) -> bool:
        """Returns True if collection is not empty, otherwise False."""
        return len(self) > 0
