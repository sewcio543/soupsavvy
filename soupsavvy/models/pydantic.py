from __future__ import annotations

from functools import reduce

from pydantic import BaseModel as PydanticBaseModel
from pydantic._internal._model_construction import ModelMetaclass as PydanticModelMeta

import soupsavvy.models.constants as c
from soupsavvy.interfaces import TagSearcher
from soupsavvy.models.base import BaseModel, ModelMeta

# attributes of pydantic model that with user defined fields
_MODEL_FIELDS = "model_fields"


class CombinedMeta(ModelMeta, PydanticModelMeta):
    """
    Combined metaclass that merges the behavior of ModelMeta (from soupsavvy)
    and PydanticModelMeta (from pydantic).
    """

    def _get_fields(cls) -> dict[str, TagSearcher]:
        """
        Returns the fields of the model class with their
        respective TagSearcher instances based on the `__inherit_fields__` setting.
        """
        classes = (
            [
                base
                for base in reversed(cls.__mro__)
                if issubclass(base, BaseModel)
                and not (base is BaseModel or base is BasePydanticModel)
            ]
            if getattr(cls, c.INHERIT_FIELDS)
            else [cls]
        )

        return reduce(
            dict.__or__,
            [
                {
                    key: value.default
                    # we expect it to have this attribute
                    for key, value in getattr(class_, _MODEL_FIELDS).items()
                    if (
                        # accepted field must be TagSearcher
                        isinstance(value.default, TagSearcher)
                        # or BaseModel subclass
                        or (
                            isinstance(value.default, type)
                            and issubclass(value.default, BaseModel)
                        )
                    )
                    and key not in c.SPECIAL_FIELDS
                }
                for class_ in classes
            ],
        )


class BasePydanticModel(PydanticBaseModel, BaseModel, metaclass=CombinedMeta):

    def __init__(self, **kwargs) -> None:
        """
        Initializes a model instance with provided field values.
        This method ensures that Pydantic validation is applied to the fields.

        Parameters
        ----------
        kwargs : Any
            Field values to initialize the model with, provided as keyword arguments.

        Raises
        ------
        MissingFieldsException
            If any required fields are missing from the provided kwargs.
        UnknownModelFieldException
            If any unknown fields are provided in the kwargs.
        ValidationError
            If Pydantic validation fails.
        """
        # Perform validation with Pydantic
        super().__init__(**kwargs)
        # Perform soupsavvy BaseModel initialization
        BaseModel.__init__(self, **kwargs)
