"""Module with all serialization operations."""

from typing import Protocol

from soupsavvy.base import BaseOperation


class JSONSerializable(Protocol):
    """
    Protocol for objects that can be serialized to JSON.
    They must have `json` method that returns a dictionary.
    This is a protocol and not a base class to allow for more flexibility.
    """

    def json(self) -> dict: ...


class JSON(BaseOperation):
    """
    Operation to serialize an object to JSON format.
    Argument to `execute` method must implement `JSONSerializable` protocol:
    `json` method that returns a dictionary.

    Common use case is to serialize BaseModel instance.

    Example
    -------
    >>> ssv_model = Model.find(element)
    ... serializer = JSON()
    ... json_data = serializer.execute(ssv_model)
    "{'field1': 'value1', 'field2': 'value2'}"
    """

    def _execute(self, obj: JSONSerializable) -> dict:
        return obj.json()

    def __eq__(self, other):
        return isinstance(other, JSON)
