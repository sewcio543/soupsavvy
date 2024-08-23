from typing import Any, Optional

from bs4 import Tag

from soupsavvy.operations.base import BaseOperation


class BaseMockOperation(BaseOperation):
    def __eq__(self, x: Any) -> bool:
        return isinstance(x, self.__class__)


class MockTextOperation(BaseMockOperation):
    def execute(self, arg: Optional[Tag]) -> Optional[str]:
        if arg is None:
            return None

        return arg.text


class MockIntOperation(BaseMockOperation):
    def execute(self, arg: str) -> int:
        return int(arg)
