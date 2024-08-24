"""
Module with base model class used as a parent for all user defined
`soupsavvy` models.
"""

from __future__ import annotations

from abc import ABC
from functools import reduce
from typing import Any, Literal, Optional, overload

from bs4 import Tag
from typing_extensions import Self

import soupsavvy.exceptions as exc
from soupsavvy.interfaces import Comparable, TagSearcher, TagSearcherExceptions
from soupsavvy.selectors.base import SoupSelector, check_selector

# default recursive value for finding fields of model within the scope
_DEFAULT_RECURSIVE = True

_SCOPE = "__scope__"
_INHERIT_FIELDS = "__inherit_fields__"

_SPECIAL_FIELDS = {_SCOPE, _INHERIT_FIELDS}


class ModelMeta(type(ABC)):
    """
    Metaclass for all models derived from `BaseModel`. This metaclass ensures that
    certain attributes and methods are defined and properly configured in each model class.

    It handles validation and inheritance of specific attributes that control the behavior
    of the models, such as `__scope__` and `__inherit_fields__`.

    Parameters
    ----------
    name : str
        The name of the class being created.
    bases : tuple
        The base classes from which the new class inherits.
    class_dict : dict
        The dictionary containing the class attributes.

    Attributes
    ----------
    scope : SoupSelector
        Returns the `__scope__` attribute, which defines the scope within which the model
        is to be found.
    fields : dict of {str: TagSearcher}
        Aggregates and returns the TagSearcher fields from the current model class and
        its base classes, depending on the `__inherit_fields__` setting.

    Raises
    ------
    MissingModelScopeException
        If `__scope__` is not defined in the model.
    """

    def __init__(cls, name, bases, class_dict):

        super().__init__(name, bases, class_dict)

        if name == "BaseModel":
            return

        for field in _SPECIAL_FIELDS:
            if hasattr(cls, field):
                continue

            for base in cls.__mro__:
                if issubclass(base, BaseModel) and hasattr(base, field):
                    setattr(cls, field, getattr(base, field))
                    break

        scope = getattr(cls, _SCOPE)

        if scope is None:
            raise exc.MissingModelScopeException(
                f"Missing '{_SCOPE}' class attribute in '{name}'."
            )

        message = (
            f"'{_SCOPE}' attribute of the model class '{cls.__name__}' "
            f"needs to be '{SoupSelector.__name__}' instance, got '{type(scope)}'."
        )
        check_selector(scope, message=message)

    @property
    def scope(cls) -> SoupSelector:
        """
        Returns the `__scope__` attribute,
        which defines the scope selector for the model.

        Returns
        -------
        SoupSelector
            The scope selector used to identify the model within the HTML content.
        """
        return getattr(cls, _SCOPE)

    @property
    def fields(cls) -> dict[str, TagSearcher]:
        """
        Aggregates and returns the TagSearcher fields
        from the current model and its base classes.
        The fields are aggregated based on the `__inherit_fields__` setting.

        Returns
        -------
        dict[str, TagSearcher]
            A dictionary mapping field names to their respective TagSearcher instances.
        """
        classes = (
            [
                base
                for base in reversed(cls.__mro__)
                if issubclass(base, BaseModel) and base is not BaseModel
            ]
            if getattr(cls, _INHERIT_FIELDS)
            else [cls]
        )

        return reduce(
            dict.__or__,
            [
                {
                    key: value
                    for key, value in c.__dict__.items()
                    if isinstance(value, TagSearcher) and key not in _SPECIAL_FIELDS
                }
                for c in classes
            ],
        )


class BaseModel(TagSearcher, Comparable, metaclass=ModelMeta):
    """
    Base class for all models, providing common functionality for HTML tag searching and
    comparison. All models should inherit from this class.

    This class provides the fundamental operations required for finding and initializing
    model instances within HTML tags.

    Attributes
    ----------
    __scope__ : SoupSelector
        Defines the scope within which the model is searched. Must be defined in derived classes.
    __inherit_fields__ : bool
        Controls whether fields from base classes are inherited by the derived model class.
        Defaults to True.

    Raises
    ------
    MissingFieldsException
        If any required fields are missing during initialization.
    """

    __scope__ = None
    __inherit_fields__ = True

    def __init__(self, **kwargs) -> None:
        """
        Initializes a model instance with provided field values.

        Parameters
        ----------
        **kwargs : dict
            A dictionary of field names and their corresponding values.

        Raises
        ------
        MissingFieldsException
            If any required fields are missing from the provided kwargs.
        """
        for field in self.__class__.fields.keys():
            if field not in kwargs:
                raise exc.MissingFieldsException(
                    f"Cannot initialize model '{self.__class__.__name__}' "
                    f"without '{field}' field."
                )

            setattr(self, field, kwargs[field])

        self.__post_init__()

    def __post_init__(self) -> None:
        """
        Post-initialization hook. Can be overridden by subclasses to perform additional
        initialization steps after the base initialization.
        """

    @overload
    @classmethod
    def find(
        cls,
        tag: Tag,
        strict: Literal[True] = ...,
        recursive: bool = ...,
    ) -> Self: ...

    @overload
    @classmethod
    def find(
        cls,
        tag: Tag,
        strict: Literal[False] = ...,
        recursive: bool = ...,
    ) -> Optional[Self]: ...

    @overload
    @classmethod
    def find(
        cls,
        tag: Tag,
        strict: bool = ...,
        recursive: bool = ...,
    ) -> Optional[Self]: ...

    @classmethod
    def find(
        cls,
        tag: Tag,
        strict: bool = False,
        recursive: bool = True,
    ) -> Optional[Self]:
        """
        Searches for and returns an instance of the model within the provided tag.

        Parameters
        ----------
        tag : Tag
            The HTML tag within which to search for the model.
        strict : bool, optional
            Whether to raise an exception if the model is not found. Default is False.
        recursive : bool, optional
            Whether the search for the model scope should be recursive. Default is True.

        Returns
        -------
        Optional[Self]
            An instance of the model if found, otherwise None.

        Raises
        ------
        ModelNotFoundException
            If the model's scope is not found and strict is True.
        """
        bound = cls.scope.find(tag=tag, strict=False, recursive=recursive)

        if bound is not None:
            return cls._find(tag=bound, strict=strict)

        if strict:
            raise exc.ModelNotFoundException(
                f"Scope for the model '{cls.__name__}' was not found "
                f"from '{cls.scope}' in tag."
            )

        return None

    @classmethod
    def _find(cls, tag: Tag, strict: bool = False) -> Self:
        """
        Internal method to find and initialize a model instance from a given tag.

        Parameters
        ----------
        tag : Tag
            The tag within which to search for model fields.
        strict : bool, optional
            Whether to raise an exception if any fields are not found. Default is False.

        Returns
        -------
        Self
            An instance of the model.

        Raises
        ------
        ModelNotFoundException
            If a required field cannot be found.
        """
        params = {}

        for key, selector in cls.fields.items():
            try:
                result = selector.find(
                    tag=tag, strict=strict, recursive=_DEFAULT_RECURSIVE
                )
            except TagSearcherExceptions as e:
                raise exc.ModelNotFoundException(
                    f"Extracting field '{key}' failed in model '{cls.__name__}'."
                ) from e

            params[key] = result

        return cls(**params)

    @classmethod
    def find_all(
        cls,
        tag: Tag,
        recursive: bool = True,
        limit: Optional[int] = None,
    ) -> list[Self]:
        """
        Searches for and returns all instances of the model within the provided tag.

        Parameters
        ----------
        tag : Tag
            The HTML tag within which to search for model instances.
        recursive : bool, optional
            Whether the search should be recursive. Default is True.
        limit : int, optional
            The maximum number of model instances to return. Default is None.

        Returns
        -------
        list of Self
            A list of model instances found within the tag.
        """
        elements = cls.scope.find_all(tag=tag, recursive=recursive, limit=limit)
        return [cls._find(element, strict=False) for element in elements]

    def __str__(self) -> str:
        params = ", ".join(
            f"{name}={getattr(self, name)}" for name in self.__class__.fields.keys()
        )
        return f"{self.__class__.__name__}({params})"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, x: Any) -> bool:
        if not isinstance(x, self.__class__):
            return False

        fields = self.__class__.fields.keys()
        return all(getattr(self, key) == getattr(x, key) for key in fields)
