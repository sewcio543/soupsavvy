"""Testing module for general operations."""

import pytest

from soupsavvy.exceptions import NotOperationException
from soupsavvy.operations.base import check_operator
from soupsavvy.operations.general import OperationPipeline
from tests.soupsavvy.operations.conftest import MockIntOperation, MockTextOperation
from tests.soupsavvy.selectors.conftest import MockLinkSelector


class TestBaseOperation:
    """Unit test suite for BaseOperation class."""

    @pytest.mark.parametrize(
        argnames="value",
        argvalues=["text", str.lower, MockLinkSelector()],
        ids=["str", "function", "selector"],
    )
    def test_or_operator_raises_exception_if_not_base_operation(self, value):
        """
        Tests if `|` operator raises NotOperationException
        if not used with instance of BaseOperation.
        """

        with pytest.raises(NotOperationException):
            MockTextOperation() | value

    def test_or_operator_returns_operation_pipeline_with_base_operation(self):
        """
        Tests if `|` operator returns OperationPipeline if used with BaseOperation.
        """
        operation1 = MockTextOperation()
        operation2 = MockIntOperation()
        result = operation1 | operation2

        assert isinstance(result, OperationPipeline)
        assert result.operations == [operation1, operation2]


class TestCheckOperator:
    """
    Class for testing check_operator function.
    Ensures that provided object is a valid `soupsavvy` operation.
    """

    def test_passes_check_and_returns_the_same_object(self):
        """
        Tests if check_operator returns the same object
        if it is instance of BaseOperation.
        """
        operation = MockTextOperation()
        result = check_operator(operation)
        assert result is operation

    @pytest.mark.parametrize(
        argnames="param",
        argvalues=["operation", str.lower, MockLinkSelector()],
        ids=["str", "function", "selector"],
    )
    def test_raises_exception_when_not_operation(self, param):
        """
        Tests if check_operator raises NotOperationException
        if object is not instance of BaseOperation.
        """
        with pytest.raises(NotOperationException):
            check_operator("selector")

    def test_raises_exception_with_custom_message_when_specified(self):
        """
        Tests if check_operator raises NotOperationException with custom message
        if object is not instance of BaseOperation and message is specified.
        """
        message = "Custom message"

        with pytest.raises(NotOperationException, match=message):
            check_operator("operation", message=message)
