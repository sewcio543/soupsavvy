from __future__ import annotations

import inspect
from typing import Any, Callable, List

from bs4 import Tag

import soupsavvy.exceptions as exc
from soupsavvy.operations.base import BaseOperation


class OperationPipeline(BaseOperation):
    def __init__(self, *operations: BaseOperation) -> None:
        self.operations: List[BaseOperation] = list(operations)

    def _execute(self, arg: Any) -> Any:
        """Execute each operation in sequence, passing the result to the next."""
        for operation in self.operations:
            arg = operation.execute(arg)
        return arg

    def __or__(self, other: BaseOperation) -> OperationPipeline:
        """Allows chaining multiple operations using the `|` operator."""
        self.operations.append(other)
        return self

    def __eq__(self, x: Any) -> bool:
        if not isinstance(x, OperationPipeline):
            return False

        return self.operations == x.operations


class Operation(BaseOperation):
    def __init__(self, func: Callable) -> None:
        self.operation = self._check_callable(func)

    def _check_callable(self, obj: Any) -> Callable:
        """
        Check if the input is a valid callable that can be used as an operation.
        Input must be callable with exactly one mandatory argument.

        Parameters
        ----------
        obj : Any
            Input passes to Operation initialization.

        Returns
        -------
        Callable
            The input callable if it is a valid operation.

        Raises
        ------
        InvalidOperationFunction
            If the input is not valid operation callable.
        """
        if not isinstance(obj, Callable):
            raise exc.InvalidOperationFunction(
                f"Expected Callable as input, got {type(obj)}"
            )

        signature = inspect.signature(obj)
        params = signature.parameters.values()

        if not params:
            raise exc.InvalidOperationFunction(
                "Expected callable with at least one parameter, got none."
            )

        mandatory_keyword_only = [
            p
            for p in params
            if p.default == inspect.Parameter.empty
            and p.kind == inspect.Parameter.KEYWORD_ONLY
        ]

        if mandatory_keyword_only:
            raise exc.InvalidOperationFunction(
                f"Callable with keyword-only without default is not valid."
            )

        mandatory_params = [
            p
            for p in params
            if p.default == inspect.Parameter.empty
            and p.kind
            in {
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.POSITIONAL_ONLY,
            }
        ]

        if len(mandatory_params) > 1:
            # it can be 0 with signature def foo(arg1=1)
            raise exc.InvalidOperationFunction(
                f"Expected callable with one mandatory argument, got {len(mandatory_params)}"
            )

        return obj

    def _execute(self, arg: Any) -> Any:
        """Execute the custom operation."""
        return self.operation(arg)

    def __eq__(self, x: Any) -> bool:
        if not isinstance(x, Operation):
            return False

        return self.operation is x.operation


class Text(BaseOperation):
    def __init__(self, separator: str = "", strip: bool = False) -> None:
        self.separator = separator
        self.strip = strip

    def _execute(self, arg: Tag) -> str:
        """Extract text from a BeautifulSoup Tag."""
        return arg.get_text(separator=self.separator, strip=self.strip)

    def __eq__(self, x: Any) -> bool:
        if not isinstance(x, Text):
            return False

        return self.separator == x.separator and self.strip == x.strip


class Attribute(BaseOperation):
    def __init__(self, attribute: str, default: Any = None) -> None:
        self.attribute = attribute
        self.default = default

    def _execute(self, arg: Tag) -> Any:
        """Extract a single attribute from a BeautifulSoup Tag."""
        return arg.get(self.attribute, default=self.default)

    def __eq__(self, x: Any) -> bool:
        if not isinstance(x, Attribute):
            return False

        return self.attribute == x.attribute and self.default == x.default
