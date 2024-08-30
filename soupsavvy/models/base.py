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
# default strict value for finding fields of model within the scope
_DEFAULT_STRICT = False

_SCOPE = "__scope__"
_INHERIT_FIELDS = "__inherit_fields__"

_SPECIAL_FIELDS = {_SCOPE, _INHERIT_FIELDS}


class ModelMeta(type(ABC)):
    """
    Metaclass for all models derived from `BaseModel`. This metaclass ensures that
    certain attributes and methods are defined
    and properly configured in each model class.

    It handles validation of provided attributes and controls inheritance of fields.
    Meta inherits from `type(ABC)` to avoid metaclass conflicts.

    Attributes
    ----------
    scope : SoupSelector
        Returns the `__scope__` attribute, which defines the scope
        within which the model is to be found.
    fields : dict[str, TagSearcher]
        Fields that defines the model and search operations.
    """

    def __init__(cls, name, bases, class_dict):
        """
        Initializes the model class and validates its attributes.
        For each user-defined model, which is a subclass of `BaseModel`,
        checks if scope and fields are properly defined.

        Raises
        ------
        ScopeNotDefinedException
            If the scope attribute is missing in the model class.
        FieldsNotDefinedException
            If no fields are defined in the model class.
        """
        super().__init__(name, bases, class_dict)

        if name == "BaseModel":
            return

        scope = getattr(cls, _SCOPE)

        if scope is None:
            raise exc.ScopeNotDefinedException(
                f"Missing '{_SCOPE}' class attribute in '{name}'."
            )

        message = (
            f"'{_SCOPE}' attribute of the model class '{cls.__name__}' "
            f"needs to be '{SoupSelector.__name__}' instance, got '{type(scope)}'."
        )
        check_selector(scope, message=message)

        if not cls._get_fields():
            raise exc.FieldsNotDefinedException(
                f"Model '{cls.__name__}' has no fields defined. At least one required."
            )

    @property
    def scope(cls) -> SoupSelector:
        """
        Returns the `__scope__` attribute,
        which defines the scope selector for the model.

        Returns
        -------
        SoupSelector
            The scope selector used to identify the element in which
            the model is searched.
        """
        return getattr(cls, _SCOPE)

    @property
    def fields(cls) -> dict[str, TagSearcher]:
        """
        Returns the fields of the model class with their
        respective TagSearcher instances. The fields are aggregated based on
        the `__inherit_fields__` setting.

        Returns
        -------
        dict[str, TagSearcher]
            A dictionary mapping field names to their respective TagSearcher instances.
        """
        return cls._get_fields()

    def _get_fields(cls) -> dict[str, TagSearcher]:
        """
        Returns the fields of the model class with their
        respective TagSearcher instances based on the `__inherit_fields__` setting.
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
                    if (
                        # accepted field must be TagSearcher
                        isinstance(value, TagSearcher)
                        # or BaseModel subclass
                        or (isinstance(value, type) and issubclass(value, BaseModel))
                    )
                    and key not in _SPECIAL_FIELDS
                }
                for c in classes
            ],
        )


class BaseModel(TagSearcher, Comparable, metaclass=ModelMeta):
    """Base class for all user-defined models in `soupsavvy`."""

    __scope__: SoupSelector = None  # type: ignore
    __inherit_fields__: bool = True

    def __init__(self, **kwargs) -> None:
        """
        Initializes a model instance with provided field values.
        Model should not be initialized directly, but through the `find` methods.

        Parameters
        ----------
        kwargs : Any
            Field values to initialize the model with provided
            as keyword arguments.

        Raises
        ------
        MissingFieldsException
            If any required fields are missing from the provided kwargs.
        UnknownModelFieldException
            If any unknown fields are provided in the kwargs.
        """

        for field in self.__class__.fields.keys():

            try:
                value = kwargs.pop(field)
            except KeyError:
                raise exc.MissingFieldsException(
                    f"Cannot initialize model '{self.__class__.__name__}' "
                    f"without '{field}' field."
                )

            setattr(self, field, value)

        if kwargs:
            raise exc.UnknownModelFieldException(
                f"Model '{self.__class__.__name__}' has no fields defined "
                f"for: {kwargs.keys()}"
            )

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
        By default, perform recursive, non-strict search for model fields
        within the scope element.

        Parameters
        ----------
        tag : Tag
            Any BeautifulSoup Tag object within which to search for the model.
        strict : bool, optional
            Whether to raise an exception if the scope element
            for the model is not found. Default is False, None is returned.
        recursive : bool, optional
            Whether the search for the model scope element should be recursive.
            Default is True.

        Returns
        -------
        Self | None
            An instance of the model if found, otherwise None.

        Raises
        ------
        ModelNotFoundException
            If the model's scope is not found and strict is True.
        FieldExtractionException
            If any model field failed to be extracted.
        """
        bound = cls.scope.find(tag=tag, strict=False, recursive=recursive)

        if bound is not None:
            return cls._find(bound)

        if strict:
            raise exc.ModelNotFoundException(
                f"Scope for the model '{cls.__name__}' was not found "
                f"from '{cls.scope}' in tag."
            )

        return None

    @classmethod
    def _find(cls, tag: Tag) -> Self:
        """
        Internal method to find and initialize a model instance from a given tag.
        By default, perform recursive, non-strict search for model fields.

        Parameters
        ----------
        tag : Tag
            The tag within which to search for model fields (scope element).

        Returns
        -------
        Self
            An instance of the model.

        Raises
        ------
        FieldExtractionException
            If any model field failed to be extracted.
        """
        params = {}

        for key, selector in cls.fields.items():
            try:
                result = selector.find(
                    tag=tag,
                    strict=_DEFAULT_STRICT,
                    recursive=_DEFAULT_RECURSIVE,
                )
            except exc.RequiredConstraintException as e:
                raise exc.FieldExtractionException(
                    f"Field '{key}' is required and was not found in model '{cls.__name__}' "
                    f"for element:\n{tag}."
                ) from e
            except TagSearcherExceptions as e:
                raise exc.FieldExtractionException(
                    f"Extracting field '{key}' failed in model '{cls.__name__}' "
                    f"for element:\n{tag}."
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
        By default, perform recursive, non-strict search for model fields
        just like in `find` method.

        Parameters
        ----------
        tag : Tag
            Any BeautifulSoup Tag object within which to search for the model.
        recursive : bool, optional
            Whether the search for the model scope element should be recursive.
            Default is True.
        limit : int, optional
            Maximum number of model instances to return. Default is None, which
            returns all instances found.

        Returns
        -------
        list[Self]
            A list of model instances found within the tag.
        """
        elements = cls.scope.find_all(tag=tag, recursive=recursive, limit=limit)
        return [cls._find(element) for element in elements]

    def __str__(self) -> str:
        params = [
            f"{name}={repr(getattr(self, name))}"
            for name in self.__class__.fields.keys()
        ]
        return f"{self.__class__.__name__}({', '.join(params)})"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, x: Any) -> bool:
        """
        Checks if provided object is equal to the model instance.
        They need to be of the same class and have the same field values.
        """
        if not isinstance(x, self.__class__):
            return False

        fields = self.__class__.fields.keys()
        return all(getattr(self, key) == getattr(x, key) for key in fields)
