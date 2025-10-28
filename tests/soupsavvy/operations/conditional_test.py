"""Testing module for conditional operations."""

import pytest

from soupsavvy.exceptions import BreakOperationException, FailedOperationExecution
from soupsavvy.operations.conditional import Break, Continue, IfElse
from tests.soupsavvy.conftest import (
    MockIntOperation,
    MockPlus10Operation,
    MockTextOperation,
)


def mock_condition(arg):
    """
    Mock condition function for testing `IfElse` operation equality.
    It requires callables of objects to be the same object.
    """
    return True


@pytest.mark.operation
class TestIfElse:
    """Class with unit test suite for IfElse operation."""

    def test_executes_proper_operation_based_on_condition(self):
        """
        Testes if execute method calls the proper operation based on the condition.
        """
        operation = IfElse(
            lambda x: isinstance(x, str),
            MockIntOperation(),
            MockPlus10Operation(),
        )

        assert operation.execute("10") == 10
        assert operation.execute(10) == 20

    def test_execute_raises_error_when_operation_fails(self):
        """
        Tests if execute method raises FailedOperationExecution when
        chosen operation fails to execute.
        """
        operation = IfElse(
            lambda x: isinstance(x, str),
            MockIntOperation(),
            MockPlus10Operation(),
        )

        with pytest.raises(FailedOperationExecution):
            operation.execute("abc")

    @pytest.mark.parametrize(
        argnames="operations",
        argvalues=[
            (
                IfElse(
                    mock_condition,
                    MockIntOperation(),
                    MockTextOperation(),
                ),
                IfElse(
                    mock_condition,
                    MockIntOperation(),
                    MockTextOperation(),
                ),
            )
        ],
    )
    def test_eq_returns_true_if_same_operation(self, operations: tuple):
        """Tests if __eq__ method returns True if objects are equal."""
        operation1, operation2 = operations
        assert (operation1 == operation2) is True

    @pytest.mark.parametrize(
        argnames="operations",
        argvalues=[
            # different condition
            (
                IfElse(
                    lambda x: True,
                    MockIntOperation(),
                    MockTextOperation(),
                ),
                IfElse(
                    mock_condition,
                    MockIntOperation(),
                    MockTextOperation(),
                ),
            ),
            # different else operation
            (
                IfElse(
                    mock_condition,
                    MockIntOperation(),
                    MockPlus10Operation(),
                ),
                IfElse(
                    mock_condition,
                    MockIntOperation(),
                    MockTextOperation(),
                ),
            ),
            # different if operation
            (
                IfElse(
                    mock_condition,
                    MockPlus10Operation(),
                    MockIntOperation(),
                ),
                IfElse(
                    mock_condition,
                    MockTextOperation(),
                    MockIntOperation(),
                ),
            ),
            # not instance of IfElse
            (
                IfElse(
                    mock_condition,
                    MockPlus10Operation(),
                    MockIntOperation(),
                ),
                MockIntOperation(),
            ),
        ],
    )
    def test_eq_returns_false_if_different_operation(self, operations: tuple):
        """Tests if __eq__ method returns False if objects are not equal."""
        operation1, operation2 = operations
        assert (operation1 == operation2) is False

    @pytest.mark.parametrize(
        argnames="operations",
        argvalues=[
            # not instance of IfElse
            (
                IfElse(
                    mock_condition,
                    MockPlus10Operation(),
                    MockIntOperation(),
                ),
                MockIntOperation(),
            ),
        ],
    )
    def test_equality_check_returns_not_implemented(self, operations: tuple):
        """Tests if equality check returns NotImplemented for non comparable types."""
        operation1, operation2 = operations
        result = operation1.__eq__(operation2)
        assert result is NotImplemented


@pytest.mark.operation
class TestBreak:
    """Class with unit test suite for Break operation."""

    def test_raises_error_and_passes_value_to_exception(self):
        """
        Tests if Break operation raises BreakOperationException
        if executed and passes current result to the exception.
        """
        operation = Break()

        with pytest.raises(BreakOperationException) as info:
            operation.execute("10")
            assert info.value.result == "10"

    @pytest.mark.parametrize(
        argnames="operations",
        argvalues=[(Break(), Break())],
    )
    def test_eq_returns_true_if_same_operation(self, operations: tuple):
        """Tests if __eq__ method returns True if objects are equal."""
        operation1, operation2 = operations
        assert (operation1 == operation2) is True

    @pytest.mark.parametrize(
        argnames="operations",
        argvalues=[(Break(), MockIntOperation())],
    )
    def test_eq_returns_false_if_different_operation(self, operations: tuple):
        """Tests if __eq__ method returns False if objects are not equal."""
        operation1, operation2 = operations
        assert (operation1 == operation2) is False

    @pytest.mark.parametrize(
        argnames="operations",
        argvalues=[(Break(), MockIntOperation())],
    )
    def test_equality_check_returns_not_implemented(self, operations: tuple):
        """Tests if equality check returns NotImplemented for non comparable types."""
        operation1, operation2 = operations
        result = operation1.__eq__(operation2)
        assert result is NotImplemented


@pytest.mark.operation
class TestContinue:
    def test_execute_returns_value_back(self):
        """Tests if execute method returns the same value back."""
        operation = Continue()
        result = operation.execute("10")
        assert result == "10"

    @pytest.mark.parametrize(
        argnames="operations",
        argvalues=[(Continue(), Continue())],
    )
    def test_eq_returns_true_if_same_operation(self, operations: tuple):
        """Tests if __eq__ method returns True if objects are equal."""
        operation1, operation2 = operations
        assert (operation1 == operation2) is True

    @pytest.mark.parametrize(
        argnames="operations",
        argvalues=[(Continue(), MockIntOperation())],
    )
    def test_eq_returns_false_if_different_operation(self, operations: tuple):
        """Tests if __eq__ method returns False if objects are not equal."""
        operation1, operation2 = operations
        assert (operation1 == operation2) is False

    @pytest.mark.parametrize(
        argnames="operations",
        argvalues=[(Continue(), MockIntOperation())],
    )
    def test_equality_check_returns_not_implemented(self, operations: tuple):
        """Tests if equality check returns NotImplemented for non comparable types."""
        operation1, operation2 = operations
        result = operation1.__eq__(operation2)
        assert result is NotImplemented
