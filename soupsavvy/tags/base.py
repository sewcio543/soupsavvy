"""Module for base classes and interfaces for tag selectors."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import reduce
from typing import Any, Literal, Optional, overload

from bs4 import NavigableString, Tag

from soupsavvy.tags.exceptions import (
    NavigableStringException,
    NotSelectableSoupException,
    TagNotFoundException,
)
from soupsavvy.tags.namespace import FIND_RESULT


class SelectableSoup(ABC):
    """
    Interface for classes that define tags and provide functionality
    to find them in BeautifulSoup Tags.

    Methods
    -------
    find(tag: Tag, strict: bool = False)
        Finds tag element in BeautifulSoup Tag by wrapping Tag find method
        and passing parameters specific to given tag.
        If strict parameter is set to True and element is not found exception is raised.
        If strict is set to False, which is a default and element is not found
        result of Tag.find is return, which is None.
        Otherwise matching Tag is returned.
    find_all(tag: Tag)
        Finds all tag elements in BeautifulSoup Tag by wrapping Tag find_all method
        and passing parameters specific to given tag.

    Notes
    -----
    To implement SelectableSoup interface child class must implement:
    * 'find_all' method that returns result of bs4.Tag 'find_all' method.
    * '_find' method that returns result of bs4.Tag 'find' method.
    """

    @overload
    def find(
        self,
        tag: Tag,
        strict: Literal[False] = ...,
    ) -> Optional[Tag]: ...

    @overload
    def find(
        self,
        tag: Tag,
        strict: Literal[True] = ...,
    ) -> Tag: ...

    def find(self, tag: Tag, strict: bool = False) -> Optional[Tag]:
        """
        Finds a first matching element in provided BeautifulSoup Tag.

        Parameters
        ----------
        tag : Tag
            Any BeautifulSoup Tag object.
        strict : bool, optional
            If True, raises an exception if tag was not found in markup,
            if False and tag was not found, returns None by defaulting to BeautifulSoup
            implementation. Value of this parameter does not affect behavior if tag
            was successfully found in the markup. By default False.
        exception: Exception, optional
            Exception instance to be raised when strict parameter is set to True
            and tag was not found in markup. By default TagNotFoundException is raised.

        Returns
        -------
        Tag | None
            BeautifulSoup Tag if it tag was found in the markup, else None.

        Notes
        -----
        If result is an instance of NavigableString,
        exception is raised to avoid any type of inconsistency downstream.

        Raises
        ------
        TagNotFoundException
            If strict parameter is set to True and tag was not found in markup.
        NavigableStringException
            If NavigableString was returned by bs4.
        """
        result = self._find(tag)

        if result is None:
            if strict:
                raise TagNotFoundException("Tag was not found in markup.")
            return None

        if isinstance(result, NavigableString):
            raise NavigableStringException(
                f"NavigableString was returned for {result} string search, "
                "invalid operation for SelectableSoup find."
            )

        return result

    @abstractmethod
    def find_all(self, tag: Tag) -> list[Tag]:
        """
        Finds all matching elements in provided BeautifulSoup Tag.

        Parameters
        ----------
        tag : Tag
            Any BeautifulSoup Tag object.

        Returns
        -------
        list[Tag]
            A list of Tag objects matching tag specifications.
            If none found, the list is empty.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} is an interface, "
            "and does not implement this method."
        )

    @abstractmethod
    def _find(self, tag: Tag) -> FIND_RESULT:
        """
        Returns an object that is a result of markup search.

        Parameters
        ----------
        tag : Tag
            Any BeautifulSoup Tag object.

        Returns
        -------
        NavigableString | Tag | None:
            Result of bs4.Tag find method with tag parameters.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} is an interface, "
            "and does not implement this method."
        )

    def __or__(self, x: SelectableSoup) -> SoupUnionTag:
        """
        Overrides __or__ method called also by pipe operator '|'.
        Syntactical Sugar for logical disjunction, that creates a SelectableSoup
        matching at least one of the elements.

        Parameters
        ----------
        x : SelectableSoup
            SelectableSoup object to be combined into new SoupUnionTag.

        Returns
        -------
        SoupUnionTag
            Union of two SelectableSoup that can be used to get all elements
            that match at least one of the elements in the Union.

        Raises
        ------
        TypeError
            If provided object is not of SelectableSoup type.
        """
        if not isinstance(x, SelectableSoup):
            raise TypeError(
                f"Bitwise or not supported for types {type(self)} and {type(x)}, "
                f"expected an instance of {SelectableSoup.__name__}."
            )

        return SoupUnionTag(self, x)


class SingleSelectableSoup(SelectableSoup):
    """
    Extension of SelectableSoup interface that defines a single element.

    Notes
    -----
    To implement SingleSelectableSoup interface, child class must implement:
    * 'wildcard' property that defines whether tag matches all html elements.
    * '_find_params' property that returns dict representing Tag.find
    and find_all parameters that are passed as keyword arguments into these methods.
    """

    def find_all(self, tag: Tag) -> list[Tag]:
        return tag.find_all(**self._find_params)

    def _find(self, tag: Tag) -> FIND_RESULT:
        return tag.find(**self._find_params)

    @property
    @abstractmethod
    def _find_params(self) -> dict[str, Any]:
        """
        Returns keyword arguments for Tag.find and Tag.find_all in form of dictionary,
        Arguments are specific for searched Tag.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} is an interface, "
            "and does not implement this property."
        )


class SelectableCSS:
    """
    Interface for Tags that can be searched with css selector.

    Notes
    -----
    To implement SelectableCSS interface, child class must implement:
    * 'selector' property, which return a string representing element css selector.
    """

    @property
    @abstractmethod
    def selector(self) -> str:
        """Returns string representing element css selector."""
        raise NotImplementedError(
            f"{self.__class__.__name__} is an interface, "
            "and does not implement this property."
        )


@dataclass(init=False)
class SoupUnionTag(SelectableSoup):
    """
    Class representing an Union of multiple soup selectors.
    Provides elements matching any of the selectors in an Union.

    Example
    -------
    >>> SoupUnionTag(
    >>>     ElementTag("a"),
    >>>     ElementTag("div", [AttributeTag(name="class", value="widget")])
    >>> )

    matches all elements that have "a" tag name OR 'class' attribute "widget".

    Example
    -------
    >>> <a>Hello World</a> ✔️
    >>> <div class="widget">Hello World</div> ✔️
    >>> <div>Hello Python</div> ❌

    Parameters
    ----------
    tags : SelectableSoup
        SelectableSoup objects to match accepted as positional arguments.

    Notes
    -----
    SoupUnionTag does not implement SelectableSoup interface
    as it allows SelectableSoup as positional init arguments.
    """

    def __init__(
        self,
        tag1: SelectableSoup,
        tag2: SelectableSoup,
        /,
        *tags: SelectableSoup,
    ) -> None:
        """
        Initializes SoupUnionTag object with provided positional arguments as tags.
        At least two SelectableSoup object required to create SoupUnionTag.

        Parameters
        ----------
        tags: SelectableSoup
            SelectableSoup objects to match accepted as positional arguments.

        Raises
        ------
        NotSelectableSoupException
            If any of provided parameters is not an instance of SelectableSoup.
        """
        args = [tag1, tag2] + list(tags)
        invalid = [arg for arg in args if not isinstance(arg, SelectableSoup)]
        if invalid:
            raise NotSelectableSoupException(
                f"Parameters {invalid} are not instances of SelectableSoup."
            )
        self.tags = args

    def _find(self, tag: Tag) -> FIND_RESULT:
        # iterates all tags and returns first element that matches
        for _tag_ in self.tags:
            result = _tag_.find(tag)
            if result is not None:
                return result

        return None

    def find_all(self, tag: Tag) -> list[Tag]:
        return reduce(list.__add__, (_tag_.find_all(tag) for _tag_ in self.tags))
