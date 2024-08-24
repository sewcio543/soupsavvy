"""Module for base classes and interfaces for tag selectors."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Iterable, Literal, Optional, Union, overload

from bs4 import NavigableString, Tag

import soupsavvy.exceptions as exc
import soupsavvy.selectors.namespace as ns
from soupsavvy.interfaces import Comparable, TagSearcher
from soupsavvy.operations.base import BaseOperation
from soupsavvy.utils.deprecation import deprecated_function

if TYPE_CHECKING:
    from soupsavvy.operations.selection_pipeline import SelectionPipeline
    from soupsavvy.selectors.combinators import (
        AncestorCombinator,
        ChildCombinator,
        DescendantCombinator,
        NextSiblingCombinator,
        ParentCombinator,
        SelectorList,
        SubsequentSiblingCombinator,
    )
    from soupsavvy.selectors.logical import AndSelector


def check_selector(x: Any, message: Optional[str] = None) -> SoupSelector:
    """
    Checks if provided object is a valid `soupsavvy` selector.
    Checks for instance of SoupSelector and raises an exception if not.
    Returns provided object if fulfills the condition for convenience.

    Parameters
    ----------
    x : Any
        Any object to be validated as correct selector.
    message : str, optional
        Custom message to be displayed in case of raising an exception.
        By default None, which results in default message.

    Raises
    ------
    NotSoupSelectorException
        If provided object is not an instance of SoupSelector.
    """
    message = message or f"Object {x} is not an instance of {SoupSelector.__name__}."

    if not isinstance(x, SoupSelector):
        raise exc.NotSoupSelectorException(message)

    return x


class SoupSelector(TagSearcher, Comparable):
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
        strict: bool = ...,
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
                raise exc.TagNotFoundException("Tag was not found in markup.")
            return None

        if isinstance(result, NavigableString):
            raise exc.NavigableStringException(
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

    def _find(self, tag: Tag, recursive: bool = True) -> ns.FindResult:
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
        >>> selector1 = TypeSelector("div")
        >>> selector2 = TypeSelector("div")
        >>> selector1 == selector2
        True
        >>> selector1.find(tag) == selector2.find(tag)
        True
        """

        raise NotImplementedError(
            f"{self.__class__.__name__} is an interface, "
            "and does not implement this method."
        )

    @overload
    def __or__(self, x: SoupSelector) -> SelectorList: ...

    @overload
    def __or__(self, x: BaseOperation) -> SelectionPipeline: ...

    def __or__(
        self, x: Union[SoupSelector, BaseOperation]
    ) -> Union[SelectorList, SelectionPipeline]:
        """
        Overrides __or__ method called also by pipe operator '|'.
        Syntactical Sugar for logical disjunction, that creates SelectorList,
        which matches at least one of the elements.

        Parameters
        ----------
        x : SoupSelector
            SoupSelector object to be combined into new SelectorList with current one.

        Returns
        -------
        SelectorList
            Union of two SoupSelector that can be used to get all elements
            that match at least one of the elements in the Union.

        Raises
        ------
        NotSoupSelectorException
            If provided object is not of SoupSelector type.
        """
        from soupsavvy.operations.selection_pipeline import SelectionPipeline
        from soupsavvy.selectors.combinators import SelectorList

        if isinstance(x, BaseOperation):
            return SelectionPipeline(selector=self, operation=x)

        message = (
            f"Bitwise OR not supported for types {type(self)} and {type(x)}, "
            f"expected an instance of {SoupSelector.__name__} or {BaseOperation.__name__}."
        )
        check_selector(x, message=message)

        if isinstance(self, SelectorList):
            args = [*self.selectors, x]
            # return new SelectorList with updated steps
            return SelectorList(*args)

        return SelectorList(self, x)

    def __invert__(self) -> SoupSelector:
        """
        Overrides __invert__ method called also by tilde operator '~'.
        Syntactical Sugar for bitwise NOT operator, that creates a NotSelector
        matching everything that is not matched by the SoupSelector.

        Parameters
        ----------
        x : SoupSelector
            SoupSelector object to be negated into new NotSelector.

        Returns
        -------
        NotSelector
            Negation of SoupSelector that can be used to get all elements
            that do not match the SoupSelector.
        SoupSelector
            Any SoupSelector object in case of directly inverting
            NotSelector to get original SoupSelector.

        Raises
        ------
        NotSoupSelectorException
            If provided object is not of SoupSelector type.
        """
        from soupsavvy.selectors.logical import NotSelector

        return NotSelector(self)

    def __and__(self, x: SoupSelector) -> AndSelector:
        """
        Overrides __and__ method called also by ampersand operator '&'.
        Syntactical Sugar for bitwise AND operator, that creates an AndSelector
        matching everything that is matched by both SoupSelector.

        Parameters
        ----------
        x : SoupSelector
            SoupSelector object to be combined into new AndSelector
            with current SoupSelector.

        Returns
        -------
        AndSelector
            Intersection of two SoupSelector that can be used to get all elements
            that match both SoupSelector.

        Raises
        ------
        NotSoupSelectorException
            If provided object is not of SoupSelector type.
        """
        from soupsavvy.selectors.logical import AndSelector

        message = (
            f"Bitwise AND not supported for types {type(self)} and {type(x)}, "
            f"expected an instance of {SoupSelector.__name__}."
        )
        check_selector(x, message=message)

        if isinstance(self, AndSelector):
            args = [*self.selectors, x]
            # return new AndSelector with updated steps
            return AndSelector(*args)

        return AndSelector(self, x)

    def __gt__(self, x: SoupSelector) -> ChildCombinator:
        """
        Overrides __gt__ method called also by greater-than operator '>'.
        Syntactical Sugar for greater-than operator, that creates a ChildCombinator
        which is equivalent to child combinator in css.

        Example
        -------
        >>> div > a

        matches all 'a' elements that are direct children of 'div' elements.
        The same can be achieved by using '>' operator on two SoupSelector objects.

        Example
        -------
        >>> TypeSelector("div") > TypeSelector("a")

        Which results in

        Example
        -------
        >>> ChildCombinator(TypeSelector("div"), TypeSelector("a"))

        Parameters
        ----------
        x : SoupSelector
            SoupSelector object to be combined into new ChildCombinator
            as selector for children of elements matched by current SoupSelector.

        Returns
        -------
        ChildCombinator
            ChildCombinator object that can be used to get all matching elements
            that are direct children of the elements matched by current SoupSelector.

        Raises
        ------
        NotSoupSelectorException
            If provided object is not of SoupSelector type.
        """
        from soupsavvy.selectors.combinators import ChildCombinator

        message = (
            f"GT operator not supported for types {type(self)} and {type(x)}, "
            f"expected an instance of {SoupSelector.__name__}."
        )
        check_selector(x, message=message)

        if isinstance(self, ChildCombinator):
            args = [*self.selectors, x]
            # return new ChildCombinator with updated steps
            return ChildCombinator(*args)

        return ChildCombinator(self, x)

    def __lt__(self, x: SoupSelector) -> ParentCombinator:
        """
        Overrides __lt__ method called also by less-than operator '<'.
        Syntactical Sugar for less-than operator, that creates a ParentCombinator.

        Example
        -------
        >>> TypeSelector("a") < TypeSelector("div")

        Which results in

        Example
        -------
        >>> ParentCombinator(TypeSelector("a"), TypeSelector("div"))

        Matches all 'div' elements that are parents of 'a' elements.

        Parameters
        ----------
        x : SoupSelector
            SoupSelector object to be combined into new ParentCombinator
            as selector for parent of elements matched by current SoupSelector.

        Returns
        -------
        ParentCombinator
            ParentCombinator object that can be used to get all matching elements
            that are parents of the elements matched by current SoupSelector.

        Raises
        ------
        NotSoupSelectorException
            If provided object is not of SoupSelector type.
        """
        from soupsavvy.selectors.combinators import ParentCombinator

        message = (
            f"LT operator not supported for types {type(self)} and {type(x)}, "
            f"expected an instance of {SoupSelector.__name__}."
        )
        check_selector(x, message=message)

        if isinstance(self, ParentCombinator):
            args = [*self.selectors, x]
            # return new ParentCombinator with updated steps
            return ParentCombinator(*args)

        return ParentCombinator(self, x)

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
        >>> TypeSelector("div") + TypeSelector("a")

        Which results in

        Example
        -------
        >>> NextSiblingCombinator(TypeSelector("div"), TypeSelector("a"))

        Parameters
        ----------
        x : SoupSelector
            SoupSelector object to be combined into new NextSiblingCombinator
            as selector for next sibling of current SoupSelector.

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
        from soupsavvy.selectors.combinators import NextSiblingCombinator

        message = (
            f"ADD operator not supported for types {type(self)} and {type(x)}, "
            f"expected an instance of {SoupSelector.__name__}."
        )
        check_selector(x, message=message)

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
        >>> TypeSelector("div") * TypeSelector("a")

        Which results in

        Example
        -------
        >>> SubsequentSiblingCombinator(TypeSelector("div"), TypeSelector("a"))

        Parameters
        ----------
        x : SoupSelector
            SoupSelector object to be combined into new SubsequentSiblingCombinator
            as selector for following sibling of current SoupSelector.

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
        from soupsavvy.selectors.combinators import SubsequentSiblingCombinator

        message = (
            f"MUL operator not supported for types {type(self)} and {type(x)}, "
            f"expected an instance of {SoupSelector.__name__}."
        )
        check_selector(x, message=message)

        if isinstance(self, SubsequentSiblingCombinator):
            args = [*self.selectors, x]
            # return new SubsequentSiblingCombinator with updated steps
            return SubsequentSiblingCombinator(*args)

        return SubsequentSiblingCombinator(self, x)

    def __rshift__(self, x: SoupSelector) -> DescendantCombinator:
        """
        Overrides __rshift__ method called also by right shift operator '>>'.
        Syntactical Sugar for right shift operator, that creates a DescendantCombinator
        which is equivalent to descendant combinator in css, typically represented
        by a single space character.

        Example
        -------
        >>> div a

        matches all 'a' elements with 'div' as their ancestor.

        Example
        -------
        >>> TypeSelector("div") >> TypeSelector("a")

        Which results in

        Example
        -------
        >>> DescendantCombinator(TypeSelector("div"), TypeSelector("a"))

        Parameters
        ----------
        x : SoupSelector
            SoupSelector object to be combined into new DescendantCombinator
            as selector for descendant of current SoupSelector.

        Returns
        -------
        DescendantCombinator
            DescendantCombinator object that can be used to get all matching elements
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
        from soupsavvy.selectors.combinators import DescendantCombinator

        message = (
            f"RIGHT SHIFT operator not supported for types {type(self)} and {type(x)}, "
            f"expected an instance of {SoupSelector.__name__}."
        )
        check_selector(x, message=message)

        if isinstance(self, DescendantCombinator):
            args = [*self.selectors, x]
            # return new DescendantCombinator with updated steps
            return DescendantCombinator(*args)

        return DescendantCombinator(self, x)

    def __lshift__(self, x: SoupSelector) -> AncestorCombinator:
        """
        Overrides __lshift__ method called also by left shift operator '<<'.
        Syntactical Sugar for left-shift operator, that creates an AncestorCombinator.

        Example
        -------
        >>> TypeSelector("a") << TypeSelector("div")

        Which results in

        Example
        -------
        >>> AncestorCombinator(TypeSelector("a"), TypeSelector("div"))

        Matches all 'div' elements that are ancestors of 'a' elements.

        Parameters
        ----------
        x : SoupSelector
            SoupSelector object to be combined into new AncestorCombinator
            as ancestor selector of current SoupSelector.

        Returns
        -------
        AncestorCombinator
            AncestorCombinator object that can be used to get all matching elements
            that are ancestors of the elements matched by current SoupSelector.

        Raises
        ------
        NotSoupSelectorException
            If provided object is not of SoupSelector type.
        """
        from soupsavvy.selectors.combinators import AncestorCombinator

        message = (
            f"LEFT SHIFT operator not supported for types {type(self)} and {type(x)}, "
            f"expected an instance of {SoupSelector.__name__}."
        )
        check_selector(x, message=message)

        if isinstance(self, AncestorCombinator):
            args = [*self.selectors, x]
            # return new AncestorCombinator with updated steps
            return AncestorCombinator(*args)

        return AncestorCombinator(self, x)


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
    def css(self) -> str:
        """Returns string representing element css selector."""
        raise NotImplementedError(
            f"{self.__class__.__name__} is an interface, "
            "and does not implement this property."
        )

    @property
    @deprecated_function(
        message="'selector' property is deprecated, use 'css' instead."
    )
    def selector(self) -> str:
        """Returns string representing element css selector."""
        return self.css


class CompositeSoupSelector(SoupSelector):
    """
    Interface for Tags that uses multiple steps to find elements.

    Notes
    -----
    To implement CompositeSoupSelector interface, child class must implement
    call super init method with provided tags as arguments to check and assign them.

    Attributes
    ----------
    selectors : list[SoupSelector]
        List of SoupSelector objects passed to CompositeSoupSelector.
    """

    # if the order of selectors is not relevant - by default True
    COMMUTATIVE = True

    def __init__(self, selectors: Iterable[SoupSelector]) -> None:
        """
        Initializes CompositeSoupSelector object with provided tags.
        Checks if all tags are instances of SoupSelector and assigns
        them to 'selectors' attribute.

        Parameters
        ----------
        selectors: Iterable[SoupSelector]
            SoupSelector objects passed to CompositeSoupSelector.

        Raises
        ------
        NotSoupSelectorException
            If any of provided parameters is not an instance of SoupSelector.
        """
        self.selectors = [check_selector(selector) for selector in selectors]

    def __eq__(self, other: object) -> bool:
        # check for CompositeSoupSelector type for type checking sake
        if not isinstance(other, CompositeSoupSelector):
            return False
        elif type(self) is not type(other):
            # checking for exact type match - isinstance(other, self.__class__)
            # when other is subclass of self.__class__ would call other.__eq__(self)
            # which is not desired behavior, as it returns False
            return False

        if not self.__class__.COMMUTATIVE:
            return self.selectors == other.selectors

        # if order is irrelevant, check if all selectors are covered by other
        # and vice versa - selector lists can be of different size as well
        return all(
            any(self_selector == other_selector for other_selector in other.selectors)
            for self_selector in self.selectors
        ) and all(
            any(other_selector == self_selector for self_selector in self.selectors)
            for other_selector in other.selectors
        )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({', '.join(map(str, self.selectors))})"

    def __repr__(self) -> str:
        return str(self)
