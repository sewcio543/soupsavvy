from typing import Optional

from bs4 import Tag

from soupsavvy.operations.base import BaseOperation


class ToIntOperation(BaseOperation):
    def execute(self, arg: str) -> int:
        return int(arg)


class MockTextOperation(BaseOperation):
    def execute(self, arg: Optional[Tag]) -> Optional[str]:
        if arg is None:
            return None

        return arg.text
