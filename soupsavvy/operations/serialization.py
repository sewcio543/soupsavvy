"""Module with all serialization operations."""

from soupsavvy.base import BaseOperation
from soupsavvy.interfaces import JSONSerializable


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
        if not isinstance(other, self.__class__):
            return NotImplemented

        return True
