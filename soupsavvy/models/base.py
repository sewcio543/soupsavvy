"""
Module with base model class used as a parent for all user defined
`soupsavvy` models.
"""

from __future__ import annotations

from abc import ABC
from collections.abc import Callable
from dataclasses import dataclass
from functools import reduce
from typing import Any, Literal, Optional, Type, TypeVar, Union, overload

from bs4 import Tag
from typing_extensions import Self

import soupsavvy.exceptions as exc
import soupsavvy.models.constants as c
from soupsavvy.base import SoupSelector, check_selector
from soupsavvy.interfaces import Comparable, TagSearcher, TagSearcherExceptions

# Generic type variable for model migration
T = TypeVar("T")


@dataclass
class MigrationSchema:
    """
    Defines schema for model migration in need of providing additional parameters
    to the target model initialization in nested models.

    Attributes
    ----------
    target : Type
        Target model class to migrate to.
    params : dict, optional
        Additional parameters to pass to the target model initialization.
    """

    target: Type
    params: Optional[dict] = None


def post(field: str) -> Callable[[Callable], Callable]:
    """
    Decorator to mark a method as a post-processor for a model field.
    The method will be called after the field is extracted from the tag
    in model instance initialization.

    Example
    -------
    class MyModel(BaseModel):
        ...
        field = ...

        @post("field")
        def post_process_field(self, value):
            return value.strip()

    Methods of custom model class, that are decorated with `@post` decorator,
    must accept only one argument, which is the value of the field to be processed.
    """

    def decorator(func):
        setattr(func, c.POST_ATTR, field)
        return func

    return decorator


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

        setattr(cls, c.POST_PROCESSORS, {})
        post_processors = getattr(cls, c.POST_PROCESSORS)

        # Inherit post-processors from base classes
        for base in bases:
            post_processors.update(getattr(base, c.POST_PROCESSORS, {}))

        if name in c.BASE_MODELS:
            return

        scope = getattr(cls, c.SCOPE)

        if scope is None:
            raise exc.ScopeNotDefinedException(
                f"Missing '{c.SCOPE}' class attribute in '{name}'."
            )

        message = (
            f"'{c.SCOPE}' attribute of the model class '{cls.__name__}' "
            f"needs to be '{SoupSelector.__name__}' instance, got '{type(scope)}'."
        )
        check_selector(scope, message=message)

        fields = cls._get_fields()

        if not fields:
            raise exc.FieldsNotDefinedException(
                f"Model '{cls.__name__}' has no fields defined. At least one required."
            )

        # register post processors
        for name in dir(cls):
            obj = getattr(cls, name)

            if not callable(obj) or name.startswith("__"):
                continue

            field = getattr(obj, c.POST_ATTR, None)

            if field in fields:
                post_processors[field] = obj

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
        return getattr(cls, c.SCOPE)

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
            if getattr(cls, c.INHERIT_FIELDS)
            else [cls]
        )

        return reduce(
            dict.__or__,
            [
                {
                    key: value
                    for key, value in class_.__dict__.items()
                    if (
                        # accepted field must be TagSearcher
                        isinstance(value, TagSearcher)
                        # or BaseModel subclass
                        or (isinstance(value, type) and issubclass(value, BaseModel))
                    )
                    and key not in c.SPECIAL_FIELDS
                }
                for class_ in classes
            ],
        )


class BaseModel(TagSearcher, Comparable, metaclass=ModelMeta):
    """Base class for all user-defined models in `soupsavvy`."""

    __scope__: SoupSelector = None  # type: ignore
    __inherit_fields__: bool = True

    __post_processors__: dict[str, Callable] = {}

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
        fields = self.__class__.fields.keys()

        for field in fields:

            try:
                value = kwargs.pop(field)
            except KeyError:
                raise exc.MissingFieldsException(
                    f"Cannot initialize model '{self.__class__.__name__}' "
                    f"without '{field}' field."
                )

            func = getattr(self, c.POST_PROCESSORS).get(field)

            if func is not None:
                value = func(self, value)

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

    @property
    def attributes(self) -> dict[str, Any]:
        """
        Returns a dictionary of model instance attributes representing
        model fields and their respective values.

        Returns
        -------
        dict[str, Any]
            A dictionary mapping model field names to their respective values.
        """
        return {field: getattr(self, field) for field in self.__class__.fields.keys()}

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
                    strict=c.DEFAULT_STRICT,
                    recursive=c.DEFAULT_RECURSIVE,
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

    def migrate(
        self,
        model: Type[T],
        mapping: Optional[dict[Type[BaseModel], Union[Type, MigrationSchema]]] = None,
        **kwargs,
    ) -> T:
        """
        Migrates the model instance to another model class using its fields
        in target class initialization.

        Parameters
        ----------
        model : Type[Model]
            The target model class to migrate the instance to.
        mapping : dict[Type[BaseModel], Union[Type, MigrationSchema]], optional
            Mapping of base model fields to target models. By default, if field
            is instance of BaseModel, it will be passed directly to the target model.
        kwargs : Any
            Additional keyword arguments to pass to model initialization.

        Returns
        -------
        Model
            An instance of the target model class.
        """
        if mapping is None:
            return model(**self.attributes, **kwargs)

        params = self.attributes.copy()

        for name, value in self.attributes.items():
            if not isinstance(value, BaseModel):
                continue

            schema = mapping.get(value.__class__)

            if schema is None:
                continue

            if isinstance(schema, MigrationSchema):
                params[name] = value.migrate(
                    schema.target,
                    mapping=mapping,
                    **(schema.params or {}),
                )
                continue

            params[name] = value.migrate(schema, mapping=mapping)

        return model(**params, **kwargs)

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
