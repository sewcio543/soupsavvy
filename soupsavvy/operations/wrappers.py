"""
Module for operations wrappers,
operations that control behavior of the wrapped operation.

* SkipNone - Skips the operation if the input is None.
* Suppress - Suppresses exceptions raised by the operation.
"""

from __future__ import annotations

from typing import Any, Type, Union

import soupsavvy.exceptions as exc
from soupsavvy.base import BaseOperation, OperationSearcherMixin, check_operation

# allowed exception types to suppress
ExceptionCategory = Union[Type[Exception], tuple[Type[Exception], ...]]


class OperationWrapper(OperationSearcherMixin):
    """
    A wrapper class for operations that extends the base operation functionality.
    Acts as a higher order operation, which controls behavior of the wrapped operation.
    """

    def __init__(self, operation: BaseOperation) -> None:
        """
        Initialize Higher Order Operation.

        Parameters
        ----------
        operation : BaseOperation
            The operation to be wrapped.

        Raises
        ------
        NotOperationException
            If provided object is not an instance of BaseOperation.
        """
        self.operation = check_operation(operation)

    def __eq__(self, x: Any) -> bool:
        """
        Check if two OperationWrapper instances are equal.
        They need to be of the same class and wrap the same operation.

        Parameters
        ----------
        x : Any
            The object to compare with.

        Returns
        -------
        bool
            True if the instances are equal, False otherwise.
        """
        return isinstance(x, self.__class__) and self.operation == x.operation

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.operation})"

    def __repr__(self) -> str:
        return str(self)


class SkipNone(OperationWrapper):
    """
    A wrapper that skips the operation if the input is None.
    Used to prevent exceptions where it's safe and expected to skip the operation.

    Example
    -------
    >>> from soupsavvy.operations import Text
    ... from soupsavvy.models import SkipNone
    ... operation = SkipNone(Text())
    ... operation.execute(None)
    None

    When element was not found, which can be expected, skips operation
    and returns None.
    """

    def _execute(self, arg: Any) -> Any:
        if arg is None:
            return None

        return self.operation.execute(arg)


class Suppress(OperationWrapper):
    """
    A wrapper that executes the operation and suppresses exceptions raised,
    returning None instead. Used to catch exceptions where it's expected
    this might happen.

    Example
    -------
    >>> from soupsavvy.operations import Operation
    ... from soupsavvy.models import Suppress
    ... operation = Suppress(Operation(int))
    ... operation.execute("")
    None

    This can be used with `Default` operation to provide a default value
    when the operation fails.

    Example
    -------
    >>> from soupsavvy.operations import Operation
    ... from soupsavvy.models import Suppress
    ... operation = Default(Suppress(Operation(int)), 0)
    ... operation.execute("")
    None

    Operations in example can be used to try to convert string to integer
    from text of tag, that can potentially be empty. In such case, if it's not required,
    default can be set to None or known value.

    Suppress also accepts category of exceptions to suppress, by default it suppresses
    all exceptions that inherit from Exception.

    Example
    -------
    >>> from soupsavvy.operations import Operation
    ... from soupsavvy.models import Suppress
    ... operation = Suppress(Operation(int), category=ValueError)
    ... operation.execute("not an integer")
    None

    Category can be a tuple of exceptions as well, `issubclass` is used to check
    if the cause of exception is subclass of provided category.

    Example
    -------
    >>> from soupsavvy.operations import Operation
    ... from soupsavvy.models import Suppress
    ... operation = Suppress(Operation(int), category=(AttributeError, ValueError))
    ... operation.execute("not an integer")
    FailedOperationExecution
    """

    def __init__(
        self,
        operation: BaseOperation,
        category: ExceptionCategory = Exception,
    ) -> None:
        """
        Initialize Suppress OperationWrapper.

        Parameters
        ----------
        operation : BaseOperation
            The operation to be wrapped.
        category : Type[Exception] | tuple[Type[Exception], ...], optional
            The exception type(s) to suppress. By default, suppresses all exceptions
            that inherit from Exception.

        Raises
        ------
        NotOperationException
            If provided object is not an instance of BaseOperation.
        """
        super().__init__(operation)
        self._category = category

    def _execute(self, arg: Any) -> Any:
        try:
            return self.operation.execute(arg)
        except exc.FailedOperationExecution as e:
            cause = e.__cause__.__class__

            if not issubclass(cause, self._category):
                raise
            return None
