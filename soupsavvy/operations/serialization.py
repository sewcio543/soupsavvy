from abc import ABC, abstractmethod

from soupsavvy.base import BaseOperation


class JSONSerializable(ABC):
    @abstractmethod
    def json(self) -> dict:
        raise NotImplementedError


class JSON(BaseOperation):
    def _execute(self, obj: JSONSerializable) -> dict:
        return obj.json()

    def __eq__(self, other):
        return isinstance(other, JSON)
