"""Module for utility functions for tag selectors."""

from dataclasses import dataclass
from typing import Iterator

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

    def __iter__(self) -> Iterator[Tag]:
        """
        Returns iterator over bs4.Tag.
        If recursive is set to True, iterates over all descendants,
        otherwise only over direct children.
        """
        if self.recursive:
            return iter(self.tag.descendants)  # type: ignore

        return iter(self.tag.children)  # type: ignore


class UniqueTag:
    def __init__(self, tag):
        self.tag = tag

    def __hash__(self):
        return id(self.tag)

    def __eq__(self, other):
        return self.tag == other.tag
