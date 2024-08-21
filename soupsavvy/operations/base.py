from __future__ import annotations

from typing import TYPE_CHECKING, Any

from soupsavvy.interfaces import Executable

if TYPE_CHECKING:
    from soupsavvy.operations.operations import OperationPipeline


class BaseOperation(Executable):
    def execute(self, arg: Any) -> Any: ...

    def __or__(self, other: Any) -> OperationPipeline:
        """Allows chaining multiple operations using the `|` operator."""
        from soupsavvy.operations.operations import OperationPipeline

        if not isinstance(other, BaseOperation):
            raise TypeError(
                f"unsupported operand type(s) for |: 'OperationPipeline' and '{type(other)}'"
            )

        return OperationPipeline(self, other)
