"""Module for base classes and interfaces for tag selectors."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import reduce
from itertools import chain
from typing import Any, Iterable, Literal, Optional, overload

from bs4 import NavigableString, Tag

from soupsavvy.tags.exceptions import (
    NavigableStringException,
    NotSelectableSoupException,
    TagNotFoundException,
)
from soupsavvy.tags.namespace import FindResult
from soupsavvy.tags.tag_utils import TagIterator, UniqueTag


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
    It could optionally implement:
    * '_find' method that returns result of bs4.Tag 'find' method.
    By default '_find' method is implemented by calling 'find_all' method
    and returning first element if any found or None otherwise.
    If different logic is required or performance can be improved, '_find' method
    can be overridden in child class.
    """

    @overload
    def find(
        self,
        tag: Tag,
        strict: Literal[False] = ...,
        recursive: bool = ...,
    ) -> Optional[Tag]: ...

    @overload
    def find(
        self,
        tag: Tag,
        strict: Literal[True] = ...,
        recursive: bool = ...,
    ) -> Tag: ...

    def find(
        self,
        tag: Tag,
        strict: bool = False,
        recursive: bool = True,
    ) -> Optional[Tag]:
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
        recursive : bool, optional
            bs4.Tag.find method parameter that specifies if search should be recursive.
            If set to False, only direct children of the tag will be searched.
            By default True.

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
        result = self._find(tag, recursive=recursive)

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
    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
        """
        Finds all matching elements in provided BeautifulSoup Tag.

        Parameters
        ----------
        tag : Tag
            Any BeautifulSoup Tag object.
        recursive : bool, optional
            bs4.Tag.find method parameter that specifies if search should be recursive.
            If set to False, only direct children of the tag will be searched.
            By default True.
        limit : int, optional
            bs4.Tag.find_all method parameter that specifies maximum number of elements
            to return. If set to None, all elements are returned. By default None.

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

    def _find(self, tag: Tag, recursive: bool = True) -> FindResult:
        """
        Returns an object that is a result of markup search.

        Parameters
        ----------
        tag : Tag
            Any BeautifulSoup Tag object.
        recursive : bool, optional
            bs4.Tag.find method parameter that specifies if search should be recursive.
            If set to False, only direct children of the tag will be searched.
            By default True.

        Returns
        -------
        NavigableString | Tag | None:
            Result of bs4.Tag find method with tag parameters.
        """
        elements = self.find_all(tag, recursive=recursive, limit=1)
        return elements[0] if elements else None

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
                f"Bitwise OR not supported for types {type(self)} and {type(x)}, "
                f"expected an instance of {SelectableSoup.__name__}."
            )

        return SoupUnionTag(self, x)

    def __invert__(self) -> SelectableSoup:
        """
        Overrides __invert__ method called also by tilde operator '~'.
        Syntactical Sugar for bitwise NOT operator, that creates a NotElementTag
        matching everything that is not matched by the SelectableSoup.

        Parameters
        ----------
        x : SelectableSoup
            SelectableSoup object to be negated into new NotElementTag.

        Returns
        -------
        NotElementTag
            Negation of SelectableSoup that can be used to get all elements
            that do not match the SelectableSoup.
        SelectableSoup
            Any SelectableSoup object in case of directly inverting
            NotElementTag to get original SelectableSoup.

        Raises
        ------
        TypeError
            If provided object is not of SelectableSoup type.
        """
        return NotElementTag(self)

    def __and__(self, x: SelectableSoup) -> AndElementTag:
        """
        Overrides __and__ method called also by ampersand operator '&'.
        Syntactical Sugar for bitwise AND operator, that creates an AndElementTag
        matching everything that is matched by both SelectableSoup.

        Parameters
        ----------
        x : SelectableSoup
            SelectableSoup object to be combined into new AndElementTag
            with current SelectableSoup.

        Returns
        -------
        AndElementTag
            Intersection of two SelectableSoup that can be used to get all elements
            that match both SelectableSoup.

        Raises
        ------
        TypeError
            If provided object is not of SelectableSoup type.
        """
        if not isinstance(x, SelectableSoup):
            raise TypeError(
                f"Bitwise AND not supported for types {type(self)} and {type(x)}, "
                f"expected an instance of {SelectableSoup.__name__}."
            )

        return AndElementTag(self, x)

    def __gt__(self, x: SelectableSoup) -> ParentTag:
        """
        Overrides __gt__ method called also by greater than operator '>'.
        Syntactical Sugar for greater than operator, that creates a ParentTag
        which is equivalent to child element css selector.

        Example
        -------
        >>> div > a

        matches all 'a' elements that are direct children of 'div' elements.
        The same can be achieved by using '>' operator on two SelectableSoup objects.

        Example
        -------
        >>> ElementTag("div") > ElementTag("a")

        Which results in ParentTag(ElementTag("div"), ElementTag("a")) object.

        Parameters
        ----------
        x : SelectableSoup
            SelectableSoup object to be combined into new ParentTag as child
            of current SelectableSoup.

        Returns
        -------
        ParentTag
            ParentTag object that can be used to get all elements
            that are direct children of the current SelectableSoup.

        Raises
        ------
        TypeError
            If provided object is not of SelectableSoup type.
        """
        if not isinstance(x, SelectableSoup):
            raise TypeError(
                f"GT operator not supported for types {type(self)} and {type(x)}, "
                f"expected an instance of {SelectableSoup.__name__}."
            )

        return ParentTag(self, x)


class SingleSelectableSoup(SelectableSoup):
    """
    Extension of SelectableSoup interface that defines a single element.

    Notes
    -----
    To implement SingleSelectableSoup interface, child class must implement:
    * '_find_params' property that returns dict representing Tag.find
    and find_all parameters that are passed as keyword arguments into these methods.
    """

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
        return tag.find_all(**self._find_params, recursive=recursive, limit=limit)

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


class SelectableCSS(ABC):
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


class IterableSoup(ABC):
    """
    Interface for Tags that uses multiple steps to find elements.

    Notes
    -----
    To implement IterableSoup interface, child class must implement
    call super init method with provided tags as arguments to check and assign them.
    """

    def __init__(self, tags: Iterable[SelectableSoup]) -> None:
        """
        Initializes IterableSoup object with provided tags.
        Checks if all tags are instances of SelectableSoup and assigns
        them to 'steps' attribute.

        Parameters
        ----------
        tags: Iterable[SelectableSoup]
            SelectableSoup objects passed to IterableSoup.

        Raises
        ------
        NotSelectableSoupException
            If any of provided parameters is not an instance of SelectableSoup.
        """
        invalid = [arg for arg in tags if not isinstance(arg, SelectableSoup)]

        if invalid:
            raise NotSelectableSoupException(
                f"Parameters {invalid} are not instances of SelectableSoup."
            )

        self.steps = tags


@dataclass(init=False)
class SoupUnionTag(SelectableSoup, IterableSoup):
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
        At least two SelectableSoup objects are required to create SoupUnionTag.

        Parameters
        ----------
        tags: SelectableSoup
            SelectableSoup objects to match accepted as positional arguments.

        Raises
        ------
        NotSelectableSoupException
            If any of provided parameters is not an instance of SelectableSoup.
        """
        super().__init__([tag1, tag2, *tags])

    def _find(self, tag: Tag, recursive: bool = True) -> FindResult:
        # iterates all tags and returns first element that matches
        for _tag_ in self.steps:
            result = _tag_.find(tag, recursive=recursive)

            if result is not None:
                return result

        return None

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
        return reduce(
            list.__add__,
            (
                _tag_.find_all(tag, recursive=recursive, limit=limit)
                for _tag_ in self.steps
            ),
        )


@dataclass(init=False)
class NotElementTag(SelectableSoup, IterableSoup):
    def __init__(
        self,
        tag: SelectableSoup,
        /,
        *tags: SelectableSoup,
    ) -> None:
        """
        Initializes NotElementTags object with provided positional arguments as tags.
        At least one SelectableSoup object is required to create NotElementTags.

        Example
        -------
        >>> NotElementTag(ElementTag(tag="div")

        matches all elements that do not have "div" tag name.

        Example
        -------
        >>> <span> class="widget">Hello World</span> ✔️
        >>> <div class="menu">Hello World</div> ❌

        Object can be initialized with multiple selectors as well, in which case
        all selectors must match for element to be excluded from the result.

        Object can be created as well by using bitwise NOT operator '~'
        on a SelectableSoup object.

        Example
        -------
        >>> ~ElementTag(tag="div")

        Which is equivalent to the first example.

        Parameters
        ----------
        tags: SelectableSoup
            SelectableSoup objects to negate match accepted as positional arguments.

        Raises
        ------
        NotSelectableSoupException
            If any of provided parameters is not an instance of SelectableSoup.
        """
        self._multiple = bool(tags)
        super().__init__([tag, *tags])

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
        matching = set()

        for step in self.steps:
            matching |= {
                UniqueTag(element)
                for element in step.find_all(tag, recursive=recursive)
            }

        return [
            element
            for element in TagIterator(tag, recursive=recursive)
            if UniqueTag(element) not in matching
        ][:limit]

    def __invert__(self) -> SelectableSoup:
        """
        Overrides __invert__ method to cancel out negation by returning
        the tag in case of single selector, or SoupUnionTag in case of multiple.
        """
        if not self._multiple:
            return next(iter(self.steps))

        return SoupUnionTag(*self.steps)


@dataclass(init=False)
class AndElementTag(SelectableSoup, IterableSoup):
    def __init__(
        self,
        tag1: SelectableSoup,
        tag2: SelectableSoup,
        /,
        *tags: SelectableSoup,
    ) -> None:
        """
        Initializes AndElementTag object with provided positional arguments as tags.
        At least two SelectableSoup objects are required to create AndElementTag.

        Example
        -------
        >>> AndElementTag(
        ...    ElementTag(tag="div"),
        ...    AttributeTag(name="class", value="widget")
        ... )

        matches all elements that have "div" tag name AND 'class' attribute "widget".

        Example
        -------
        >>> <div class="widget">Hello World</div> ✔️
        >>> <span class="widget">Hello World</span> ❌
        >>> <div class="menu">Hello World</div> ❌

        Object can be initialized with multiple selectors as well, in which case
        all selectors must match for element to be included in the result.

        Object can be created as well by using bitwise AND operator '&'
        on two SelectableSoup objects.

        Example
        -------
        >>> ElementTag(tag="div") & AttributeTag(name="class", value="widget")

        Which is equivalent to the first example.

        Parameters
        ----------
        tags: SelectableSoup
            SelectableSoup objects to match accepted as positional arguments.

        Raises
        ------
        NotSelectableSoupException
            If any of provided parameters is not an instance of SelectableSoup.
        """
        super().__init__([tag1, tag2, *tags])

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
        steps = iter(self.steps)
        matching = [
            UniqueTag(element)
            for element in next(steps).find_all(tag, recursive=recursive)
        ]

        for step in steps:
            # not using set on purpose to keep order of elements
            step_elements = [
                UniqueTag(element)
                for element in step.find_all(tag, recursive=recursive)
            ]
            matching = [element for element in matching if element in step_elements]

        return [element.tag for element in matching][:limit]


class ParentTag(SelectableSoup):
    def __init__(self, parent: SelectableSoup, child: SelectableSoup):
        self.parent = parent
        self.child = child

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
        # first find all parent tags
        parents = self.parent.find_all(tag, recursive=recursive)
        # find all direct matching children of parents
        children = chain.from_iterable(
            self.child.find_all(parent, recursive=False) for parent in parents
        )
        return list(children)[:limit]


class PrecedingTag(SelectableSoup):
    def __init__(self, previous: SelectableSoup, next: SelectableSoup):
        self.previous = previous
        self.next = next

    def find_all(
        self,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Tag]:
        parents = self.previous.find_all(tag, recursive=recursive)
        # find all direct matching children of parents
        matches = []

        for parent in parents:
            if parent.parent is None:
                continue

            if parent.find_next_sibling() in self.next.find_all(
                parent.parent, recursive=False
            ):
                matches.append(parent)

            if len(matches) == limit:
                break

        return matches
