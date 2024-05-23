"""Module for utility functions for tag selectors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Optional

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
    """

    tag: Tag
    recursive: bool = True

    def _get_iterator(self) -> Iterator:
        """
        Returns iterator over bs4.Tag descendants or children
        based on recursive parameter value.
        """
        return iter(self.tag.descendants if self.recursive else self.tag.children)

    def __iter__(self) -> TagIterator:
        # Resetting iterator to the beginning.
        self._iter = self._get_iterator()
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
    _ORDER_ATTR = "_order"
    _IS_BASE = "_base"

    def __init__(self, tags: Optional[list[Tag]] = None) -> None:
        self.tags = tags or []

    def get_unique(self) -> list[Tag]:
        set_ = self._setup(base=True)
        ordered = self._order(set_)
        return ordered

    def _setup(self, base: bool) -> set[UniqueTag]:
        tags = [UniqueTag(tag) for tag in self.tags]

        for i, tag in enumerate(tags):
            setattr(tag, self._ORDER_ATTR, i)
            setattr(tag, self._IS_BASE, int(base))

        return set(tags)

    def _order(self, set_: set[UniqueTag]) -> list[Tag]:
        return [
            unique.tag
            for unique in sorted(
                set_,
                key=lambda x: (
                    # Sorting by base descending - base goes first
                    -getattr(x, self.__class__._IS_BASE, -1),
                    # Sorting by order ascending
                    getattr(x, self._ORDER_ATTR, -1),
                ),
            )
        ]

    def intersection(self, other: TagResultSet) -> TagResultSet:
        intersection = self._setup(base=True) & other._setup(base=False)
        ordered = self._order(intersection)
        return TagResultSet(ordered)

    def update(self, other: TagResultSet, limit: Optional[int] = None) -> TagResultSet:
        updated = self._setup(base=True) | other._setup(base=False)
        ordered = self._order(updated)
        return TagResultSet(ordered)

    def __and__(self, other: TagResultSet) -> TagResultSet:
        return self.intersection(other)

    def __or__(self, other: TagResultSet) -> TagResultSet:
        return self.update(other)

    def __len__(self) -> int:
        return len(self.tags)
