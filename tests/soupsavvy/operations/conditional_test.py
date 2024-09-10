"""Testing module for general operations."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import pytest

from soupsavvy.exceptions import (
    BreakOperationException,
    FailedOperationExecution,
    NotOperationException,
)
from soupsavvy.operations.conditional import Break, Continue, IfElse
from tests.soupsavvy.conftest import (
    MockBreakOperation,
    MockIntOperation,
    MockLinkSelector,
    MockPlus10Operation,
    MockTextOperation,
)


def mock_condition(arg):
    """
    Mock condition function for testing `IfElse` operation equality.
    It requires callables of objects to be the same object.
    """
    return True


class TestIfElse:
    def test_execute(self):
        operation = IfElse(
            lambda x: isinstance(x, str),
            MockIntOperation(),
            MockPlus10Operation(),
        )

        assert operation.execute("10") == 10
        assert operation.execute(10) == 20

    def test_execute_fails(self):
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


class TestBreak:
    def test_execute(self):
        operation = Break(MockIntOperation())

        with pytest.raises(BreakOperationException) as info:
            operation.execute("10")
            assert info.value.result == 10

    def test_execute_fails(self):
        operation = Break(MockIntOperation())

        with pytest.raises(FailedOperationExecution):
            operation.execute("abc")

    @pytest.mark.parametrize(
        argnames="operations",
        argvalues=[
            (
                Break(MockIntOperation()),
                Break(MockIntOperation()),
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
            (
                Break(MockIntOperation()),
                Break(MockTextOperation()),
            ),
            (
                Break(MockIntOperation()),
                MockIntOperation(),
            ),
        ],
    )
    def test_eq_returns_false_if_different_operation(self, operations: tuple):
        """Tests if __eq__ method returns False if objects are not equal."""
        operation1, operation2 = operations
        assert (operation1 == operation2) is False


class TestContinue:
    def test_execute(self):
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
        argvalues=[
            (Continue(), MockIntOperation()),
        ],
    )
    def test_eq_returns_false_if_different_operation(self, operations: tuple):
        """Tests if __eq__ method returns False if objects are not equal."""
        operation1, operation2 = operations
        assert (operation1 == operation2) is False