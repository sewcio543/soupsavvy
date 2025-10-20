"""
Module with wrappers for selectors used mostly in model schemas.
Wrappers are used to control behavior and define how fields of the models are defined.

Classes
-------
- `All` - Wrapper to find all information matching criteria.
- `Default` - Wrapper to set default value if information is not found.
- `Required` - Wrapper to enforce that information must be found.
"""

from typing import Any, Optional

import soupsavvy.exceptions as exc
from soupsavvy.base import check_operation, check_tag_searcher
from soupsavvy.interfaces import Comparable, IElement, TagSearcher, TagSearcherType
from soupsavvy.operations.selection_pipeline import SelectionPipeline


class FieldWrapper(TagSearcher, Comparable):
    """
    A wrapper for `TagSearcher` valid objects, that acts as a higher order searcher,
    which controls behavior of the wrapped searcher.
    Used as field in defined model.
    Subclasses must implement `find` method with their specific behavior.
    """

    def __init__(self, selector: TagSearcherType) -> None:
        """
        Initializes wrapper with a `TagSearcher` valid object.

        Parameters
        ----------
        selector : TagSearcher
            The `TagSearcher` valid object to be wrapped.

        Raises
        ------
        NotTagSearcherException
            If provided object is not a valid `TagSearcher`.
        """
        self._selector = check_tag_searcher(selector)

    @property
    def selector(self) -> TagSearcher:
        """
        Returns searcher, that is wrapped by this wrapper.

        Returns
        -------
        TagSearcher
            `TagSearcher` instance wrapped by this wrapper.
        """
        return self._selector

    def find_all(
        self,
        tag: IElement,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Any]:
        """
        Find all matching element using the wrapped selector.
        Used for compatibility with `TagSearcher` interface,
        delegates to wrapped selector.

        Parameters
        ----------
        tag : IElement
            Any `IElement` to search within.
        recursive : bool, optional
            Whether to search recursively, by default True.
        limit : int, optional
            Limit the number of results, by default None.

        Returns
        -------
        list[Any]
            A list of found results.
        """
        return self.selector.find_all(tag, recursive=recursive, limit=limit)

    def __eq__(self, x: Any) -> bool:
        """
        Check if two `FieldWrapper` instances are equal.
        They need to be of the same class and wrap the same selector.

        Parameters
        ----------
        x : Any
            The object to compare with.

        Returns
        -------
        bool
            True if the instances are equal, False otherwise.
        """
        return isinstance(x, self.__class__) and self.selector == x.selector

    def __or__(self, x: Any) -> SelectionPipeline:
        """
        Overrides `__or__` method called also by pipe operator '|'.
        Combines this `FieldWrapper` with an operation.

        Parameters
        ----------
        x : BaseOperation
            The operation to be combined with this `FieldWrapper`.

        Returns
        -------
        SelectionPipeline
            New `SelectionPipeline` object created from
            combining selector and operation.

        Raises
        ------
        NotOperationException
            If provided object is not an instance of `BaseOperation`.
        """
        x = check_operation(x)
        return SelectionPipeline(selector=self, operation=x)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.selector})"

    def __repr__(self) -> str:
        return str(self)


class All(FieldWrapper):
    """
    Field wrapper for selecting multiple elements matching the selector.
    Forces find method to fall back to find_all method and return all matches.

    Example
    -------
    >>> from soupsavvy.models import All
    ... from soupsavvy import TypeSelector
    ... selector = All(TypeSelector("div"))
    ... selector.find(tag)
    [element1, element2, element3]
    """

    def find(
        self, tag: IElement, strict: bool = False, recursive: bool = True
    ) -> list[Any]:
        """
        Find all matching tags using the wrapped selector,
        enforcing the use of find_all method.

        Parameters
        ----------
        tag : IElement
            Any `IElement` to search within.
        strict : bool, optional
            Ignored, as this method always falls back to `find_all`.
        recursive : bool, optional
            Whether to search recursively, by default True.

        Returns
        -------
        list[Any]
            A list of matching results.
        """
        return self.selector.find_all(tag, recursive=recursive)


class Required(FieldWrapper):
    """
    Field wrapper for enforcing matched element not to be None.
    Raises an exception if searcher does not find any matches.

    Example
    -------
    >>> from soupsavvy.models import Required
    ... from soupsavvy import TypeSelector
    ... selector = Required(TypeSelector("div"))
    ... selector.find(tag)
    RequiredConstraintException
    """

    def find(self, tag: IElement, strict: bool = False, recursive: bool = True) -> Any:
        """
        Finds a required element using the wrapped selector,
        enforcing matched element not to be None.
        If any exception is raised during the search, it's propagated to the caller.

        Parameters
        ----------
        tag : IElement
            Any `IElement` to search within.
        strict : bool, optional
            If True, raises an exception if no matches are found, by default False.
        recursive : bool, optional
            Whether to search recursively, by default True.

        Returns
        -------
        Any
            The found element.

        Raises
        ------
        RequiredConstraintException
            If selector returns None, indicating that required element was not found.
        """
        result = self.selector.find(tag=tag, strict=strict, recursive=recursive)

        if result is None:
            raise exc.RequiredConstraintException("Required element was not found")

        return result


class Default(FieldWrapper):
    """
    Field wrapper for returning a default value if no match is found.

    Example
    -------
    >>> from soupsavvy.models import Default
    ... from soupsavvy import TypeSelector
    ... selector = Default(TypeSelector("div"), default="1234")
    ... selector.find(tag)
    "1234"
    """

    def __init__(self, selector: TagSearcher, default: Any) -> None:
        """
        Initializes `Default` field wrapper.

        Parameters
        ----------
        selector : TagSearcher
            The `TagSearcher` instance to be wrapped.
        default : Any
            The default value to return if no match is found.
        """
        super().__init__(selector)
        self.default = default

    def find(self, tag: IElement, strict: bool = False, recursive: bool = True):
        """
        Finds an element, returning a default value if None was returned
        by wrapped selector. Any exception raised during the search is propagated.

        Parameters
        ----------
        tag : IElement
            Any `IElement` to search within.
        strict : bool, optional
            If True, raises an exception if no matches are found, by default False.
        recursive : bool, optional
            Whether to search recursively, by default True.

        Returns
        -------
        Any
            The found element or the default value if not found.
        """
        result = self.selector.find(tag=tag, strict=strict, recursive=recursive)
        return self.default if result is None else result

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.selector}, default={self.default})"
