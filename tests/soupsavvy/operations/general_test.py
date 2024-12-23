"""Testing module for general operations."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import pytest

from soupsavvy.exceptions import FailedOperationExecution, NotOperationException
from soupsavvy.operations.general import Operation, OperationPipeline
from tests.soupsavvy.conftest import (
    MockBreakOperation,
    MockIntOperation,
    MockLinkSelector,
    MockPlus10Operation,
    MockTextOperation,
)


@dataclass
class OperationTestInput:
    """Dataclass for Operation test inputs."""

    operation: Callable
    arg: Any
    expected: Any


def mock_operation_func(arg: Any, *args, **kwargs) -> bool:
    """
    Mock operation function for testing. If arg is "+", returns True, otherwise False.
    If arg is None, raises ValueError.
    """
    if arg is None:
        raise ValueError("Argument cannot be None.")

    return arg == "+"


def mock_args_func(arg: Any, *args, **kwargs) -> tuple:
    """
    Mock operation function for testing.
    Accepts any number of positional and keyword arguments,
    which are returned in form on tuple with arg.
    """
    return (arg, args, kwargs)


@pytest.mark.operation
class TestOperation:
    """Class with unit test suite for Operation class."""

    @pytest.mark.parametrize(
        argnames="setup",
        argvalues=[
            OperationTestInput(str.upper, "hello", "HELLO"),
            OperationTestInput(lambda x: x + 10, 10, 20),
            OperationTestInput(mock_operation_func, "+", True),
            OperationTestInput(mock_operation_func, "-", False),
        ],
    )
    def test_execute_calls_custom_operation(self, setup: OperationTestInput):
        """Tests if execute method calls the custom operation."""
        operation = Operation(setup.operation)
        result = operation.execute(setup.arg)
        assert result == setup.expected

    def test_saves_init_arguments_and_passes_them_into_operation(self):
        """
        Tests if Operation saves provided arguments and passes them when executing
        operation function.
        """
        operation = Operation(mock_args_func, 1, 2, param="param", string="string")

        assert operation.args == (1, 2)
        assert operation.kwargs == {"param": "param", "string": "string"}

        result = operation.execute("arg")
        assert result == ("arg", (1, 2), {"param": "param", "string": "string"})

    def test_has_empty_parameter_attributes_when_not_provided(self):
        """
        Tests if Operation has empty args and kwargs attributes
        when no arguments are provided.
        Nothing except for arg is passed to operation function.
        """
        operation = Operation(mock_args_func)

        assert operation.args == tuple()
        assert operation.kwargs == {}

        result = operation.execute("arg")
        assert result == ("arg", (), {})

    def test_raises_error_if_operation_fails_to_execute(self):
        """
        Tests if execute method raises FailedOperationExecution if operation fails.
        """
        operation = Operation(mock_operation_func)

        with pytest.raises(FailedOperationExecution):
            operation.execute(None)

    def test_raises_error_if_invalid_operation(self):
        """
        Tests if execute method raises FailedOperationExecution if callable
        defined as operation cannot be called with one positional argument.
        """

        def mandatory_keyword_param(arg1, arg2): ...

        operation = Operation(mandatory_keyword_param)

        with pytest.raises(FailedOperationExecution):
            operation.execute(None)

    @pytest.mark.parametrize(
        argnames="operations",
        argvalues=[
            (Operation(mock_args_func), Operation(mock_args_func)),
            (
                Operation(mock_args_func, "param"),
                Operation(mock_args_func, "param"),
            ),
            (
                Operation(mock_args_func, param="param"),
                Operation(mock_args_func, param="param"),
            ),
            (
                Operation(mock_args_func, 3, 4, string="string", param="param"),
                Operation(mock_args_func, 3, 4, string="string", param="param"),
            ),
        ],
    )
    def test_eq_returns_true_if_same_operation(self, operations: tuple):
        """Tests if __eq__ method returns True if objects are equal."""
        operation1, operation2 = operations
        assert (operation1 == operation2) is True

    @pytest.mark.parametrize(
        argnames="operations",
        argvalues=[
            (Operation(str.upper), Operation(str.lower)),
            (Operation(lambda x: x), Operation(lambda x: x)),
            (Operation(lambda x: x), MockIntOperation()),
            (Operation(mock_args_func, "param"), Operation(mock_args_func)),
            (
                Operation(mock_args_func, param="param"),
                Operation(mock_args_func),
            ),
            (
                Operation(mock_args_func, param="param"),
                Operation(mock_args_func, "param"),
            ),
            (
                Operation(mock_args_func, 1),
                Operation(mock_args_func, 2),
            ),
            (
                Operation(mock_args_func, 1, 2),
                Operation(mock_args_func, 1),
            ),
            (
                Operation(mock_args_func, param="param"),
                Operation(mock_args_func, param="string"),
            ),
            (
                Operation(mock_args_func, param="param"),
                Operation(mock_args_func, string="param"),
            ),
            (
                Operation(mock_args_func, param="param", string="string"),
                Operation(mock_args_func, param="param"),
            ),
            (
                Operation(mock_args_func, 1, param="param"),
                Operation(mock_args_func, 1, param="string"),
            ),
            (
                Operation(mock_args_func, 1, param="param"),
                Operation(mock_args_func, 2, param="param"),
            ),
        ],
    )
    def test_eq_returns_false_if_different_operation(self, operations: tuple):
        """Tests if __eq__ method returns False if functions are not the same."""
        operation1, operation2 = operations
        assert (operation1 == operation2) is False


class MockText(str):
    """Mock class that imitates IElement with text attribute."""

    @property
    def text(self):
        return self


@pytest.mark.operation
class TestOperationPipeline:
    """Class with unit test suite for OperationPipeline class."""

    def test_raises_error_on_init_if_not_base_operation(self):
        """
        Tests if OperationPipeline init raises NotOperationException
        if not used with instance of BaseOperation.
        """
        with pytest.raises(NotOperationException):
            OperationPipeline(MockTextOperation(), "selector")  # type: ignore

    def test_executes_operations_and_return_correct_value(self):
        """
        Tests if execute method executes all operations in sequence
        and returns correct value.
        """
        text = MockText("10")
        operation = OperationPipeline(MockTextOperation(), MockIntOperation())
        result = operation.execute(text)
        assert result == 10

    def test_break_stops_pipeline_and_returns_current_result(self):
        """
        Tests if execute method stops the pipeline execution if operation
        raised BreakOperationException and returns results retrieved from exception.
        Subsequent operations are not executed.
        """
        text = MockText("10")
        operation = OperationPipeline(
            MockTextOperation(),
            MockBreakOperation(MockIntOperation()),
            MockPlus10Operation(),
        )
        result = operation.execute(text)
        assert result == 10

    def test_raises_error_if_any_operation_fails(self):
        """
        Tests if execute method raises FailedOperationExecution
        if any operation fails to execute.
        """
        text = MockText("abc")
        operation = OperationPipeline(MockTextOperation(), MockIntOperation())

        with pytest.raises(FailedOperationExecution):
            operation.execute(text)

    def test_or_operator_on_pipeline_creates_new_extended_pipeline(self):
        """
        Tests if `|` operator creates new OperationPipeline with extended operations.
        """
        operation = OperationPipeline(MockTextOperation(), MockIntOperation())
        result = operation | MockTextOperation()

        assert result is not operation
        assert isinstance(result, OperationPipeline)
        assert result.operations == [
            MockTextOperation(),
            MockIntOperation(),
            MockTextOperation(),
        ]

    def test_or_operator_raises_error_if_no_operator(self):
        """
        Tests if `|` operator raises NotOperationException
        if provided object is not BaseOperation.
        """
        operation = OperationPipeline(MockTextOperation(), MockIntOperation())

        with pytest.raises(NotOperationException):
            operation | MockLinkSelector()

    @pytest.mark.parametrize(
        argnames="operations",
        argvalues=[
            # with two same operations
            (
                OperationPipeline(MockTextOperation(), MockIntOperation()),
                OperationPipeline(MockTextOperation(), MockIntOperation()),
            ),
            # with three same operations
            (
                OperationPipeline(
                    MockTextOperation(), MockIntOperation(), MockTextOperation()
                ),
                OperationPipeline(
                    MockTextOperation(), MockIntOperation(), MockTextOperation()
                ),
            ),
        ],
    )
    def test_eq_returns_true_if_same_operation(self, operations: tuple):
        """Tests if __eq__ method returns True if objects are equal."""
        operation1, operation2 = operations
        assert (operation1 == operation2) is True

    @pytest.mark.parametrize(
        argnames="operations",
        argvalues=[
            # with different order
            (
                OperationPipeline(MockTextOperation(), MockIntOperation()),
                OperationPipeline(MockIntOperation(), MockTextOperation()),
            ),
            # with on extra operation
            (
                OperationPipeline(MockTextOperation(), MockIntOperation()),
                OperationPipeline(
                    MockTextOperation(), MockIntOperation(), MockTextOperation()
                ),
            ),
            # different operation type
            (
                OperationPipeline(MockTextOperation(), MockIntOperation()),
                MockIntOperation(),
            ),
            # not operation
            (
                OperationPipeline(MockTextOperation(), MockIntOperation()),
                MockLinkSelector(),
            ),
        ],
    )
    def test_eq_returns_false_if_different_operation(self, operations: tuple):
        """Tests if __eq__ method returns False if objects are not equal."""
        operation1, operation2 = operations
        assert (operation1 == operation2) is False
