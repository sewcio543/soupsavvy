from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

import soupsavvy.exceptions as exc
from soupsavvy.interfaces import Comparable, Executable

if TYPE_CHECKING:
    from soupsavvy.operations.general import OperationPipeline


def check_operator(x: Any, message: Optional[str] = None) -> BaseOperation:
    """
    Checks if provided object is a valid `soupsavvy` operation.
    Checks for instance of BaseOperation and raises an exception if not.
    Returns provided object if fulfills the condition for convenience.

    Parameters
    ----------
    x : Any
        Any object to be validated as correct operation.
    message : str, optional
        Custom message to be displayed in case of raising an exception.
        By default None, which results in default message.

    Raises
    ------
    NotOperationException
        If provided object is not an instance of BaseOperation.
    """
    message = message or f"Object {x} is not an instance of {BaseOperation.__name__}."

    if not isinstance(x, BaseOperation):
        raise exc.NotOperationException(message)

    return x


class BaseOperation(Executable, Comparable):
    def execute(self, arg: Any) -> Any:
        """Execute the operation on the given argument."""
        try:
            return self._execute(arg)
        except Exception as e:
            raise exc.FailedOperationExecution(
                f"Failed to execute operation: {e}"
            ) from e

    def _execute(self, arg: Any) -> Any:
        raise NotImplementedError

    def __or__(self, x: Any) -> OperationPipeline:
        """Allows chaining multiple operations using the `|` operator."""
        from soupsavvy.operations.general import OperationPipeline

        message = (
            f"Bitwise OR not supported for types {type(self)} and {type(x)}, "
            f"expected an instance of {BaseOperation.__name__}."
        )
        other = check_operator(x, message=message)
        return OperationPipeline(self, other)
