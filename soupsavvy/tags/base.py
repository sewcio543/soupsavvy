"""Module for base classes and interfaces for tag selectors."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Iterable, Literal, Optional, overload

from bs4 import NavigableString, Tag

from soupsavvy.exceptions import (
    NavigableStringException,
    NotSoupSelectorException,
    TagNotFoundException,
)
from soupsavvy.tags.namespace import FindResult

if TYPE_CHECKING:
    from soupsavvy.tags.combinators import (
        ChildCombinator,
        DescendantCombinator,
        NextSiblingCombinator,
        SelectorList,
        SubsequentSiblingCombinator,
    )
    from soupsavvy.tags.components import AndSelector, NotSelector


class SoupSelector(ABC):
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
    To implement SoupSelector interface child class must implement:
    * 'find_all' method that returns a list of matching elements in bs4.Tag.
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
                "invalid operation for SoupSelector find."
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

    def _check_selector_type(self, x: Any, message: Optional[str] = None) -> None:
        """
        Checks if provided object is an instance of SoupSelector.

        Parameters
        ----------
        x : Any
            Any object to be checked if it is an instance of SoupSelector.
        message : str, optional
            Custom message to be displayed in case of raising an exception.
            By default None, which results in default message.

        Raises
        ------
        NotSoupSelectorException
            If provided object is not an instance of SoupSelector.
        """
        message = (
            message or f"Object {x} is not an instance of {SoupSelector.__name__}."
        )

        if not isinstance(x, SoupSelector):
            raise NotSoupSelectorException(message)

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        """
        Check self and other object for equality.

        This method is abstract and must be implemented by all selectors.
        Selectors are considered equal if their find methods return the same result.

        Calling find or find_all methods on selectors that are equal
        should return the same results.

        Example
        -------
        >>> selector1 = ElementTag("div")
        >>> selector2 = ElementTag("div")
        >>> selector1 == selector2
        True
        >>> selector1.find(tag) == selector2.find(tag)
        True
        """

        raise NotImplementedError(
            f"{self.__class__.__name__} is an interface, "
            "and does not implement this method."
        )

    def __or__(self, x: SoupSelector) -> SelectorList:
        """
        Overrides __or__ method called also by pipe operator '|'.
        Syntactical Sugar for logical disjunction, that creates a SoupSelector
        matching at least one of the elements.

        Parameters
        ----------
        x : SoupSelector
            SoupSelector object to be combined into new SoupUnionTag.

        Returns
        -------
        SoupUnionTag
            Union of two SoupSelector that can be used to get all elements
            that match at least one of the elements in the Union.

        Raises
        ------
        NotSoupSelectorException
            If provided object is not of SoupSelector type.
        """
        from soupsavvy.tags.combinators import SelectorList

        message = (
            f"Bitwise OR not supported for types {type(self)} and {type(x)}, "
            f"expected an instance of {SoupSelector.__name__}."
        )
        self._check_selector_type(x, message=message)

        if isinstance(self, SelectorList):
            args = [*self.selectors, x]
            # return new SelectorList with updated steps
            return SelectorList(*args)

        return SelectorList(self, x)

    def __invert__(self) -> SoupSelector:
        """
        Overrides __invert__ method called also by tilde operator '~'.
        Syntactical Sugar for bitwise NOT operator, that creates a NotElementTag
        matching everything that is not matched by the SoupSelector.

        Parameters
        ----------
        x : SoupSelector
            SoupSelector object to be negated into new NotElementTag.

        Returns
        -------
        NotElementTag
            Negation of SoupSelector that can be used to get all elements
            that do not match the SoupSelector.
        SoupSelector
            Any SoupSelector object in case of directly inverting
            NotElementTag to get original SoupSelector.

        Raises
        ------
        NotSoupSelectorException
            If provided object is not of SoupSelector type.
        """
        from soupsavvy.tags.components import NotSelector

        return NotSelector(self)

    def __and__(self, x: SoupSelector) -> AndSelector:
        """
        Overrides __and__ method called also by ampersand operator '&'.
        Syntactical Sugar for bitwise AND operator, that creates an AndElementTag
        matching everything that is matched by both SoupSelector.

        Parameters
        ----------
        x : SoupSelector
            SoupSelector object to be combined into new AndElementTag
            with current SoupSelector.

        Returns
        -------
        AndElementTag
            Intersection of two SoupSelector that can be used to get all elements
            that match both SoupSelector.

        Raises
        ------
        NotSoupSelectorException
            If provided object is not of SoupSelector type.
        """
        from soupsavvy.tags.components import AndSelector

        message = (
            f"Bitwise AND not supported for types {type(self)} and {type(x)}, "
            f"expected an instance of {SoupSelector.__name__}."
        )
        self._check_selector_type(x, message=message)

        if isinstance(self, AndSelector):
            args = [*self.selectors, x]
            # return new AndSelector with updated steps
            return AndSelector(*args)

        return AndSelector(self, x)

    def __gt__(self, x: SoupSelector) -> ChildCombinator:
        """
        Overrides __gt__ method called also by greater than operator '>'.
        Syntactical Sugar for greater than operator, that creates a ChildCombinator
        which is equivalent to child combinator in css.

        Example
        -------
        >>> div > a

        matches all 'a' elements that are direct children of 'div' elements.
        The same can be achieved by using '>' operator on two SoupSelector objects.

        Example
        -------
        >>> ElementTag("div") > ElementTag("a")

        Which results in

        Example
        -------
        >>> ChildCombinator(ElementTag("div"), ElementTag("a"))

        Parameters
        ----------
        x : SoupSelector
            SoupSelector object to be combined into new ChildCombinator as child
            of current SoupSelector.

        Returns
        -------
        ChildCombinator
            ChildCombinator object that can be used to get all matching elements
            that are direct children of the current SoupSelector.

        Raises
        ------
        NotSoupSelectorException
            If provided object is not of SoupSelector type.
        """
        from soupsavvy.tags.combinators import ChildCombinator

        message = (
            f"GT operator not supported for types {type(self)} and {type(x)}, "
            f"expected an instance of {SoupSelector.__name__}."
        )
        self._check_selector_type(x, message=message)

        if isinstance(self, ChildCombinator):
            args = [*self.selectors, x]
            # return new ChildCombinator with updated steps
            return ChildCombinator(*args)

        return ChildCombinator(self, x)

    def __add__(self, x: SoupSelector) -> NextSiblingCombinator:
        """
        Overrides __add__ method called also by plus operator '+'.
        Syntactical Sugar for addition operator, that creates a NextSiblingCombinator
        which is equivalent to next sibling element css selector.

        Example
        -------
        >>> div + a

        matches all 'a' elements that immediately follow 'div' elements,
        it means that both elements are children of the same parent element.

        The same can be achieved by using '+' operator on two SoupSelector objects.

        Example
        -------
        >>> ElementTag("div") + ElementTag("a")

        Which results in

        Example
        -------
        >>> NextSiblingCombinator(ElementTag("div"), ElementTag("a"))

        Parameters
        ----------
        x : SoupSelector
            SoupSelector object to be combined into new NextSiblingCombinator as next
            sibling of current SoupSelector.

        Returns
        -------
        NextSiblingCombinator
            NextSiblingCombinator object that can be used to get all matching elements
            that are next siblings of the current SoupSelector.

        Raises
        ------
        NotSoupSelectorException
            If provided object is not of SoupSelector type.
        """
        from soupsavvy.tags.combinators import NextSiblingCombinator

        message = (
            f"ADD operator not supported for types {type(self)} and {type(x)}, "
            f"expected an instance of {SoupSelector.__name__}."
        )
        self._check_selector_type(x, message=message)

        if isinstance(self, NextSiblingCombinator):
            args = [*self.selectors, x]
            # return new NextSiblingCombinator with updated steps
            return NextSiblingCombinator(*args)

        return NextSiblingCombinator(self, x)

    def __mul__(self, x: SoupSelector) -> SubsequentSiblingCombinator:
        """
        Overrides __mul__ method called also by multiplication operator '*'.
        Syntactical Sugar for multiplication operator, that creates
        a SubsequentSiblingCombinator which is equivalent to subsequent sibling
        element css selector.

        Example
        -------
        >>> div ~ a

        matches all 'a' elements that follow 'div' elements and share the same parent.
        The same can be achieved by using '*' operator on two SoupSelector objects.

        Example
        -------
        >>> ElementTag("div") * ElementTag("a")

        Which results in

        Example
        -------
        >>> SubsequentSiblingCombinator(ElementTag("div"), ElementTag("a"))

        Parameters
        ----------
        x : SoupSelector
            SoupSelector object to be combined into new SubsequentSiblingCombinator
            as following sibling of current SoupSelector.

        Returns
        -------
        SubsequentSiblingCombinator
            SubsequentSiblingCombinator object that can be used to get all
            matching elements that are following siblings of the current SoupSelector.

        Raises
        ------
        NotSoupSelectorException
            If provided object is not of SoupSelector type.
        """
        from soupsavvy.tags.combinators import SubsequentSiblingCombinator

        message = (
            f"MUL operator not supported for types {type(self)} and {type(x)}, "
            f"expected an instance of {SoupSelector.__name__}."
        )
        self._check_selector_type(x, message=message)

        if isinstance(self, SubsequentSiblingCombinator):
            args = [*self.selectors, x]
            # return new SubsequentSiblingCombinator with updated steps
            return SubsequentSiblingCombinator(*args)

        return SubsequentSiblingCombinator(self, x)

    def __rshift__(self, x: SoupSelector) -> DescendantCombinator:
        """
        Overrides __rshift__ method called also by right shift operator '>>'.
        Syntactical Sugar for right shift operator, that creates a StepsElementTag
        which is equivalent to descendant combinator in css, typically represented
        by a single space character.

        Example
        -------
        >>> div a

        matches all 'a' elements with 'div' as their ancestor.

        Example
        -------
        >>> ElementTag("div") >> ElementTag("a")

        Which results in

        Example
        -------
        >>> StepsElementTag(ElementTag("div"), ElementTag("a"))

        Parameters
        ----------
        x : SoupSelector
            SoupSelector object to be combined into new StepsElementTag as descendant
            of current SoupSelector.

        Returns
        -------
        StepsElementTag
            StepsElementTag object that can be used to get all matching elements
            that are descendants of the current SoupSelector.

        Raises
        ------
        NotSoupSelectorException
            If provided object is not of SoupSelector type.

        Notes
        -----
        For more information on descendant combinator see:
        https://developer.mozilla.org/en-US/docs/Web/CSS/Descendant_combinator
        """
        from soupsavvy.tags.combinators import DescendantCombinator

        message = (
            f"RIGHT SHIFT operator not supported for types {type(self)} and {type(x)}, "
            f"expected an instance of {SoupSelector.__name__}."
        )
        self._check_selector_type(x, message=message)

        if isinstance(self, DescendantCombinator):
            args = [*self.selectors, x]
            # return new DescendantCombinator with updated steps
            return DescendantCombinator(*args)

        return DescendantCombinator(self, x)


class SingleSoupSelector(SoupSelector):
    """
    Extension of SoupSelector interface that defines a single element.

    Notes
    -----
    To implement SingleSoupSelector interface, child class must implement:
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


class MultipleSoupSelector(SoupSelector):
    """
    Interface for Tags that uses multiple steps to find elements.

    Notes
    -----
    To implement MultipleSoupSelector interface, child class must implement
    call super init method with provided tags as arguments to check and assign them.

    Attributes
    ----------
    selectors : list[SoupSelector]
        List of SoupSelector objects passed to MultipleSoupSelector.
    """

    def __init__(self, selectors: Iterable[SoupSelector]) -> None:
        """
        Initializes MultipleSoupSelector object with provided tags.
        Checks if all tags are instances of SoupSelector and assigns
        them to 'selectors' attribute.

        Parameters
        ----------
        selectors: Iterable[SoupSelector]
            SoupSelector objects passed to MultipleSoupSelector.

        Raises
        ------
        NotSoupSelectorException
            If any of provided parameters is not an instance of SoupSelector.
        """
        invalid = [arg for arg in selectors if not isinstance(arg, SoupSelector)]

        if invalid:
            raise NotSoupSelectorException(
                f"Parameters {invalid} are not instances of SoupSelector."
            )

        self.selectors = list(selectors)

    def __eq__(self, other: object) -> bool:
        # check for MultipleSoupSelector type for type checking sake
        if not isinstance(other, MultipleSoupSelector):
            return False
        elif type(self) is not type(other):
            # checking for exact type match - isinstance(other, self.__class__)
            # when other is subclass of self.__class__ would call other.__eq__(self)
            # which is not desired behavior, as it returns False
            return False

        return self.selectors == other.selectors

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({', '.join(map(str, self.selectors))})"

    def __repr__(self) -> str:
        return str(self)
