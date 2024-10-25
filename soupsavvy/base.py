"""
Module for base classes used across the package.
Introduces another layer of abstraction for operations and selectors.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, Generic, Literal, Optional, Union, overload

from typing_extensions import deprecated

import soupsavvy.exceptions as exc
from soupsavvy.interfaces import Comparable, Executable, T, TagSearcher

if TYPE_CHECKING:
    from soupsavvy.operations.general import OperationPipeline
    from soupsavvy.operations.selection_pipeline import SelectionPipeline
    from soupsavvy.selectors.combinators import (
        AncestorCombinator,
        ChildCombinator,
        DescendantCombinator,
        NextSiblingCombinator,
        ParentCombinator,
        SubsequentSiblingCombinator,
    )
    from soupsavvy.selectors.logical import AndSelector, SelectorList, XORSelector


def check_selector(x: Any, message: Optional[str] = None) -> SoupSelector:
    """
    Checks if provided object is a valid `soupsavvy` selector.
    Checks for instance of `SoupSelector` and raises an exception if not.
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
        If provided object is not an instance of `SoupSelector`.
    """
    message = message or f"Object {x} is not an instance of {SoupSelector.__name__}."

    if not isinstance(x, SoupSelector):
        raise exc.NotSoupSelectorException(message)

    return x


def check_operation(x: Any, message: Optional[str] = None) -> BaseOperation:
    """
    Checks if provided object is a valid `soupsavvy` operation.
    Checks for instance of `BaseOperation` and raises an exception if not.
    Returns provided object if fulfills the condition for convenience.

    Parameters
    ----------
    x : Any
        Any object to be validated as correct operation.
    message : str, optional
        Custom message to be displayed in case of raising an exception.
        By default None, which results in default message.

    Raises
    ------
    NotOperationException
        If provided object is not an instance of `BaseOperation`.
    """
    message = message or f"Object {x} is not an instance of {BaseOperation.__name__}."

    if not isinstance(x, BaseOperation):
        raise exc.NotOperationException(message)

    return x


class SoupSelector(TagSearcher, Comparable, Generic[T]):
    """
    Base class for all `soupsavvy` selectors, that define declarative search procedure
    of searching for elements in BeautifulSoup Tag.

    Selectors can be combined with other selectors to create search procedures.
    They can be chained with operations to extract and transform the data.

    Methods
    -------
    - find(tag: T, strict: bool = False, recursive: bool = True) -> Optional[Tag]

        Finds first element matching selector in provided tag if found.
        If no element is found, returns None by default,
        or raises an exception if `strict` mode is enabled.
        Additionally `recursive` parameter can be set to search only direct children.

    - find_all(tag: T, recursive: bool = True, limit: Optional[int] = None) -> list[Tag]

        Finds all elements matching selector in provided tag and returns them in a list.
        Additionally `limit` and `recursive` parameters can be set.

    Notes
    -----
    - Specific selector inheriting from this class, need to implement:
        - `find_all` method that returns a list of matching elements in bs4.Tag.
        - `__eq__` method to compare two selectors for equality.
    - Optionally `find` method can be implemented to return first matching element,
    but, by default, it uses `find_all` under the hood.
    """

    @overload
    def find(
        self,
        tag: T,
        strict: Literal[False] = ...,
        recursive: bool = ...,
    ) -> Optional[T]: ...

    @overload
    def find(
        self,
        tag: T,
        strict: Literal[True] = ...,
        recursive: bool = ...,
    ) -> T: ...

    @overload
    def find(
        self,
        tag: T,
        strict: bool = ...,
        recursive: bool = ...,
    ) -> Optional[T]: ...

    def find(
        self,
        tag: T,
        strict: bool = False,
        recursive: bool = True,
    ) -> Optional[T]:
        """
        Finds the first matching element in provided `Tag`.

        Parameters
        ----------
        tag : Tag
            Any `bs4.Tag` object to search within.
        strict : bool, optional
            If `True`, raises an exception if tag was not found in markup,
            if `False` and tag was not found, returns `None`.
            Value of this parameter does not affect behavior if element
            was successfully found. By default `False`.
        recursive : bool, optional
            Specifies if search should be recursive.
            If set to `False`, only direct children of the tag will be searched.
            By default `True`.

        Returns
        -------
        Tag | None
            First `bs4.Tag` object matching selector or `None` if none matching.

        Raises
        ------
        TagNotFoundException
            If strict parameter is set to `True` and none matching tag was found.
        """
        result = self._find(tag, recursive=recursive)

        if result is None:
            if strict:
                raise exc.TagNotFoundException("Tag was not found in markup.")
            return None

        return result

    @abstractmethod
    def find_all(
        self,
        tag: T,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[T]:
        """
        Finds all elements matching selector in provided `Tag`.

        Parameters
        ----------
        tag : Tag
            Any `bs4.Tag` object to search within.
        recursive : bool, optional
            Specifies if search should be recursive.
            If set to `False`, only direct children of the tag will be searched.
            By default `True`.
        limit : int, optional
            Specifies maximum number of elements to return.
            By default `None`, all found elements are returned.

        Returns
        -------
        list[Tag]
            List of `bs4.Tag` objects matching selector. If none found, the list is empty.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} is an interface, "
            "and does not implement this method."
        )

    def _find(self, tag: T, recursive: bool = True) -> Optional[T]:
        """
        Returns an object that is a result of tag search.

        Parameters
        ----------
        tag : Tag
            Any `bs4.Tag` object to search within.
        recursive : bool, optional
            Specifies if search should be recursive.
            If set to `False`, only direct children of the tag will be searched.
            By default `True`.

        Returns
        -------
        NavigableString | Tag | None:
            Result of selector search within provided `bs4.Tag`.
        """
        elements = self.find_all(tag, recursive=recursive, limit=1)
        return elements[0] if elements else None

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        """
        Checks self and other object for equality.

        This method is abstract and must be implemented by all selectors.

        Calling `find` or `find_all` methods on selectors that are equal
        should return the same results, provided the same parameters.

        Example
        -------
        >>> selector1 = TypeSelector("div")
        ... selector2 = TypeSelector("div")
        ... selector1 == selector2
        True
        ... selector1.find(tag) == selector2.find(tag)
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
        Overrides `__or__` method called also by pipe operator `|`.

        Syntactical Sugar for logical disjunction, that creates `SelectorList`,
        when combining two `SoupSelector` objects, or `SelectionPipeline`,
        when combining `SoupSelector` with `BaseOperation`.

        Parameters
        ----------
        x : SoupSelector | BaseOperation
            `SoupSelector` object to be combined into new `SelectorList`
            object as `SelectorList(this, other)` or `BaseOperation` to bew chained
            with it as `SelectionPipeline(this, other)`.

        Returns
        -------
        SelectorList
            Union of two `SoupSelector` objects, that can be used to get all elements
            that match at least one of the elements in the Union.
        SelectionPipeline
            Pipeline of `SoupSelector` and `BaseOperation` objects that can be used
            to extract and transform the data from the elements.

        Raises
        ------
        NotSoupSelectorException
            If provided object is not an instance of `SoupSelector`
            or `BaseOperation`.
        """
        from soupsavvy.base import BaseOperation
        from soupsavvy.operations.selection_pipeline import SelectionPipeline
        from soupsavvy.selectors.logical import SelectorList

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
        Overrides `__invert__` method called also by tilde operator `~`.
        Syntactical Sugar for bitwise NOT operator, that creates `NotSelector` instance
        matching everything that is not matched by this `SoupSelector`.

        Parameters
        ----------
        x : SoupSelector
            `SoupSelector` object to be negated into new `NotSelector` as `NotSelector(this)`.

        Returns
        -------
        NotSelector
            `NotSelector(this)`.
        SoupSelector
            Any `SoupSelector` object in case of directly inverting
            `NotSelector` to get original `SoupSelector`.

        Raises
        ------
        NotSoupSelectorException
            If provided object is not an instance of `SoupSelector`.
        """
        from soupsavvy.selectors.logical import NotSelector

        return NotSelector(self)

    def __and__(self, x: SoupSelector) -> AndSelector:
        """
        Overrides `__and_`_ method called also by ampersand operator `&`.
        Syntactical Sugar for bitwise AND operator, that creates `AndSelector` instance
        matching everything that is matched by both `SoupSelector` objects.

        Parameters
        ----------
        x : SoupSelector
            `SoupSelector` object to be combined into new `AndSelector`
            object as `AndSelector(this, other)`.

        Returns
        -------
        AndSelector
            `AndSelector(this, other)`.

        Raises
        ------
        NotSoupSelectorException
            If provided object is not an instance of `SoupSelector`.
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
        Overrides `__gt__` method called also by greater-than operator `>`.
        Syntactical Sugar for greater-than operator, that creates `ChildCombinator`.

        Parameters
        ----------
        x : SoupSelector
            `SoupSelector` object to be combined into new `ChildCombinator`
            object as `ChildCombinator(this, other)`.

        Returns
        -------
        ChildCombinator
            `ChildCombinator(this, other)`
        Raises
        ------
        NotSoupSelectorException
            If provided object is not an instance of `SoupSelector`.
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
        Overrides `__lt__` method called also by less-than operator `<`.
        Syntactical Sugar for less-than operator, that creates `ParentCombinator` instance.

        Example
        -------
        >>> TypeSelector("a") < TypeSelector("div")

        Parameters
        ----------
        x : SoupSelector
            `SoupSelector` object to be combined into new `ParentCombinator`
            object as `ParentCombinator(this, other)`.

        Returns
        -------
        ParentCombinator
            `ParentCombinator(this, other)`

        Raises
        ------
        NotSoupSelectorException
            If provided object is not an instance of `SoupSelector`.
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
        Overrides `__add__` method called also by plus operator `+`.
        Syntactical Sugar for addition operator, that creates `NextSiblingCombinator`
        instance.

        Example
        -------
        >>> TypeSelector("div") + TypeSelector("a")

        Parameters
        ----------
        x : SoupSelector
            `SoupSelector` object to be combined into new` NextSiblingCombinator`
            object as `NextSiblingCombinator(this, other)`.

        Returns
        -------
        NextSiblingCombinator
            `NextSiblingCombinator(this, other)`

        Raises
        ------
        NotSoupSelectorException
            If provided object is not an instance of `SoupSelector`.
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
        Overrides `__mul__` method called also by multiplication operator `*`.
        Syntactical Sugar for multiplication operator, that creates
        `SubsequentSiblingCombinator` instance.

        Example
        -------
        >>> TypeSelector("div") * TypeSelector("a")

        Parameters
        ----------
        x : SoupSelector
            `SoupSelector` object to be combined into new `SubsequentSiblingCombinator`
            object as `SubsequentSiblingCombinator(this, other)`.

        Returns
        -------
        SubsequentSiblingCombinator
            `SubsequentSiblingCombinator(this, other)`

        Raises
        ------
        NotSoupSelectorException
            If provided object is not an instance of `SoupSelector`.
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
        Overrides `__rshift__` method called also by right shift operator `>>`.
        Syntactical Sugar for right shift operator,
        that creates `DescendantCombinator` instance.

        Example
        -------
        >>> TypeSelector("div") >> TypeSelector("a")

        Parameters
        ----------
        x : SoupSelector
            `SoupSelector` object to be combined into new `DescendantCombinator`
            object as `DescendantCombinator(this, other)`.

        Returns
        -------
        DescendantCombinator
            `DescendantCombinator(this, other)`

        Raises
        ------
        NotSoupSelectorException
            If provided object is not an instance of `SoupSelector`.
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
        Overrides `__lshift__` method called also by left shift operator `<<`.
        Syntactical Sugar for left-shift operator, that creates `AncestorCombinator` instance.

        Example
        -------
        >>> TypeSelector("a") << TypeSelector("div")

        Parameters
        ----------
        x : SoupSelector
            `SoupSelector` object to be combined into new `AncestorCombinator`
            object as `AncestorCombinator(this, other)`.

        Returns
        -------
        AncestorCombinator
            `AncestorCombinator(this, other)`

        Raises
        ------
        NotSoupSelectorException
            If provided object is not an instance of `SoupSelector`.
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

    def __xor__(self, x: SoupSelector) -> XORSelector:
        """
        Overrides `__xor__` method called also by `xor` (caret) operator `^`.
        Syntactical Sugar `xor` operator, that creates `XORSelector` instance.

        Example
        -------
        >>> TypeSelector("a") ^ TypeSelector("div")

        Parameters
        ----------
        x : SoupSelector
            `SoupSelector` object to be combined into new `XORSelector`
            object as `XORSelector(this, other)`.

        Returns
        -------
        XORSelector
            `XORSelector(this, other)`

        Raises
        ------
        NotSoupSelectorException
            If provided object is not an instance of `SoupSelector`.
        """
        from soupsavvy.selectors.logical import XORSelector

        message = (
            f"XOR operator not supported for types {type(self)} and {type(x)}, "
            f"expected an instance of {SoupSelector.__name__}."
        )
        check_selector(x, message=message)

        if isinstance(self, XORSelector):
            args = [*self.selectors, x]
            # return new XORSelector with updated steps
            return XORSelector(*args)

        return XORSelector(self, x)


class SelectableCSS(ABC):
    """
    Interface for selectors, that can clearly and unambiguously defined css selector,
    used to search for elements, that matches the same tags as find methods.

    Notes
    -----
    To implement SelectableCSS interface, child class must implement:
    - 'selector' property, which return a string representing css selector.
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
    @deprecated("'selector' property is deprecated, use 'css' instead.")
    def selector(self) -> str:
        """Returns string representing element css selector."""
        return self.css


class CompositeSoupSelector(SoupSelector):
    """
    Interface for selectors consisting of multiple selectors.

    Notes
    -----
    To implement `CompositeSoupSelector` interface, child class must
    call its init method with provided selectors to set up the object.

    Attributes
    ----------
    selectors : list[SoupSelector]
        List of `SoupSelector` objects used for searching elements.
    """

    # if the order of selectors is not relevant - by default True
    COMMUTATIVE = True

    def __init__(self, selectors: Iterable[SoupSelector]) -> None:
        """
        Initializes composite selector object with provided selectors.
        Checks if all selectors are instances of `SoupSelector`.

        Parameters
        ----------
        selectors: Iterable[SoupSelector]
            Selectors used to search for elements.

        Raises
        ------
        NotSoupSelectorException
            If any of provided parameters is not an instance of `SoupSelector`.
        """
        self._selectors = [check_selector(selector) for selector in selectors]

    @property
    def selectors(self) -> list[SoupSelector]:
        """
        Returns a list of selectors that composite selector consists of.

        Returns
        -------
        list[SoupSelector]
            List of `SoupSelector` objects used for searching elements.
        """
        return self._selectors

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


class BaseOperation(Executable, Comparable):
    """
    Base class for all `soupsavvy` operations.
    Operations are used to process the selection results from the soup,
    extract and transform the data.

    Operations can be chained together using the pipe operator '|'.

    Example
    -------
    >>> from soupsavvy.operations import Operation
    ... operation = Operation(str.lower) | Operation(str.strip)
    ... operation.execute("  TEXT  ")
    'text'

    Operations can be combined with selectors to extract and transform
    target information.

    Example
    -------
    >>> from soupsavvy import TypeSelector
    ... from soupsavvy.operations import Operation, Text
    ... selector = TypeSelector("div") | Text() | Operation(int)
    ... selector.find(soup)
    42

    `BaseOperation` inherits from `Comparable` interface,
    `__eq__` method needs to be implemented in derived classes.
    """

    def execute(self, arg: Any) -> Any:
        """
        Execute the operation on the given argument and return the result.

        Parameters
        ----------
        arg : Any
            Argument to be processed by the operation.

        Returns
        -------
        Any
            Result of the operation.
        """
        try:
            return self._execute(arg)
        except exc.BreakOperationException:
            # break exception is propagated to the caller to handle
            raise
        except Exception as e:
            raise exc.FailedOperationExecution(
                f"Failed to execute operation: {e}"
            ) from e

    @abstractmethod
    def _execute(self, arg: Any) -> Any:
        """Internal method for executing the operation."""

        raise NotImplementedError(
            f"{self.__class__.__name__} is an interface, "
            "and does not implement this method."
        )

    def __or__(self, x: Any) -> OperationPipeline:
        """
        Overrides `__or__` method called also by pipe operator '|'.
        Syntactical Sugar for logical disjunction, that creates `OperationPipeline` instance,
        which chains two operations together.

        Parameters
        ----------
        x : BaseOperation
            `BaseOperation` object to be combined into new `OperationPipeline`
            with this operation.

        Returns
        -------
        OperationPipeline
            `OperationPipeline(this, other)`.

        Raises
        ------
        NotOperationException
            If provided object is not an instance of `BaseOperation`.
        """
        from soupsavvy.operations.general import OperationPipeline

        message = (
            f"Bitwise OR not supported for types {type(self)} and {type(x)}, "
            f"expected an instance of {BaseOperation.__name__}."
        )
        other = check_operation(x, message=message)
        return OperationPipeline(self, other)


class OperationSearcherMixin(BaseOperation, TagSearcher):
    """
    Mixin of `BaseOperation` and `TagSearcher` interfaces.
    Allows operations to be used as field searchers in model
    to perform operation directly on scope element.
    """

    def find_all(
        self,
        tag: T,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Any]:
        """
        Processes provided element and returns the result in a list.

        Parameters
        ----------
        tag : Tag
            Any `bs4.Tag` object to process.
        recursive : bool, optional
            Ignored, for consistency with interface.
        limit : int, optional
            Ignored, for consistency with interface.

        Returns
        -------
        list[Any]
            Result of applied operation on element in a list.
        """
        return [self.execute(tag)]

    def find(
        self,
        tag: T,
        strict: bool = False,
        recursive: bool = True,
    ) -> Any:
        """
        Processes provided element and returns the result.

        Parameters
        ----------
        tag : Tag
            Any `bs4.Tag` object to process.
        strict : bool, optional
            Ignored, for consistency with interface.
        limit : int, optional
            Ignored, for consistency with interface.

        Returns
        -------
        Any
            Result of applied operation on element.
        """
        return self.execute(tag)
