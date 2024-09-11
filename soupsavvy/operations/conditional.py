"""
Module for conditional operations to control flow in the pipeline.

* IfElse - Executes different operations based on the condition.
* Break - Stops the pipeline execution.
* Continue - Skips the operation and continues with the next one.
"""

from collections.abc import Callable
from typing import Any, Optional

import soupsavvy.exceptions as exc
from soupsavvy.base import BaseOperation, OperationSearcherMixin, check_operation

Condition = Callable[[Any], bool]


class IfElse(OperationSearcherMixin):
    """
    Operation to control flow in the pipeline.
    Allows to execute different operations based on the condition.

    Example
    -------
    >>> from soupsavvy.operations import IfElse, Operation
    ... operation = IfElse(
    ...     lambda x: x == 0,
    ...     Operation(lambda x: None),
    ...     Operation(lambda x: x / 100),
    ... )
    ... operation.execute(0)
    None
    ... operation.execute(100)
    1

    Implements `TagSearcher` interface for convenience. It can conditionally
    apply operations to the tag and can be used as model field.

    Example
    -------
    >>> from soupsavvy.operations import IfElse, Operation, Text
    ... operation = IfElse(
    ...     lambda x: x.get("id") == "user",
    ...     Text(),
    ...     Href(),
    ... )
    ... operation.find(user_tag)
    username
    ... operation.find(other_tag)
    www.example.com
    """

    def __init__(
        self,
        condition: Condition,
        if_: BaseOperation,
        else_: BaseOperation,
    ) -> None:
        """
        Initializes IfElse operation with condition and two operations.

        Parameters
        ----------
        condition : Callable[[Any], bool]
            Condition to check if the operation should be executed.
            If callable returns True, `if_` operation is executed, otherwise `else_`.
        if_ : BaseOperation
            Operation to execute if condition is fulfilled.
        else_ : BaseOperation
            Operation to execute if condition is not fulfilled.
        """
        self._condition = condition
        self._if_operation = check_operation(if_)
        self._else_operation = check_operation(else_)

    def _execute(self, arg: Any) -> Any:
        condition = self._condition(arg)
        operation = self._if_operation if condition else self._else_operation
        return operation.execute(arg)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, IfElse):
            return False

        return (
            self._condition is other._condition
            and self._if_operation == other._if_operation
            and self._else_operation == other._else_operation
        )


class Break(OperationSearcherMixin):
    """
    Operation to break the pipeline execution and return the current result.
    Can be used in selection/operation pipelines with `IfElse` operation
    to conditionally stop the execution.

    Example
    -------
    >>> from soupsavvy.operations import Break, IfElse, Operation
    ... operation = IfElse(
    ...     lambda x: x == 0,
    ...     Break(),
    ...     Operation(lambda x: 100 / x),
    ... ) | Operation(lambda x: x + 1)
    ... operation.execute(0)
    0
    ... operation.execute(100)
    2

    If `Break` operation is executed, the pipeline will stop and return the result,
    so next operation is not executed.
    """

    def _execute(self, arg: Any) -> Any:
        raise exc.BreakOperationException(arg)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Break)


class Continue(OperationSearcherMixin):
    """
    Operation to skip the current operation ad move to the next one.
    Can be used in selection/operation pipelines with `IfElse` operation
    to conditionally skip the operation.

    Example
    -------
    >>> from soupsavvy.operations import Continue, IfElse, Operation
    ... operation = IfElse(
    ...     lambda x: x == 0,
    ...     Continue(),
    ...     Operation(lambda x: x / 100),
    ... ) | Operation(lambda x: x - 1)
    ... operation.execute(0)
    -1
    ... operation.execute(100)
    0

    If `Continue` operation is executed,
    operation is skipped and the next one is executed.
    """

    def _execute(self, arg: Any) -> Any:
        return arg

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Continue)
