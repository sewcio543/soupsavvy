from __future__ import annotations

from typing import Any, Callable, List

from bs4 import Tag

from soupsavvy.operations.base import BaseOperation

# Type aliases for clarity
OperationFunc = Callable[[Any], Any]


class OperationPipeline(BaseOperation):
    def __init__(self, *operations: BaseOperation) -> None:
        self.operations: List[BaseOperation] = list(operations)

    def execute(self, arg: Any) -> Any:
        """Execute each operation in sequence, passing the result to the next."""
        for operation in self.operations:
            arg = operation.execute(arg)
        return arg

    def __or__(self, other: BaseOperation) -> OperationPipeline:
        """Allows chaining multiple operations using the `|` operator."""
        self.operations.append(other)
        return self


class Operation(BaseOperation):
    def __init__(self, operation: OperationFunc) -> None:
        self.operation = operation

    def execute(self, arg: Any) -> Any:
        """Execute the custom operation."""
        return self.operation(arg)


class Text(BaseOperation):
    def __init__(self, separator: str = "", strip: bool = False) -> None:
        self.separator = separator
        self.strip = strip

    def execute(self, arg: Tag) -> str:
        """Extract text from a BeautifulSoup Tag."""
        return arg.get_text(separator=self.separator, strip=self.strip)


class Attribute(BaseOperation):
    def __init__(self, attribute: str) -> None:
        self.attribute = attribute

    def execute(self, arg: Tag) -> Any:
        """Extract a single attribute from a BeautifulSoup Tag."""
        return arg.get(self.attribute)
