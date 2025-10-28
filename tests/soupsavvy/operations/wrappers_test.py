"""Module with unit tests for wrapper operations."""

import pytest

from soupsavvy.exceptions import FailedOperationExecution, NotOperationException
from soupsavvy.operations.wrappers import OperationWrapper, SkipNone, Suppress
from tests.soupsavvy.conftest import (
    BaseMockOperation,
    MockIntOperation,
    MockLinkSelector,
    MockTextOperation,
)


class MockOperationWrapper(OperationWrapper):
    """Mock class for testing OperationWrapper interface."""

    def _execute(self, arg): ...


class MockOperationWrapper2(OperationWrapper):
    """Mock class for testing OperationWrapper interface."""

    def _execute(self, arg): ...


@pytest.mark.operation
class TestOperationWrapper:
    """Unit test suite for OperationWrapper interface."""

    def test_raises_error_if_invalid_operation_passed(self):
        """
        Tests if raises NotOperationException if invalid operation is passed.
        It expects instance of BaseOperation.
        """
        with pytest.raises(NotOperationException):
            MockOperationWrapper2(MockLinkSelector())  # type: ignore

    @pytest.mark.parametrize(
        argnames="operations",
        argvalues=[
            # wrapped operations are equal
            (
                MockOperationWrapper(MockTextOperation()),
                MockOperationWrapper(MockTextOperation()),
            ),
        ],
    )
    def test_two_tag_selectors_are_equal(self, operations: tuple):
        """Tests if two wrappers are equal."""
        assert (operations[0] == operations[1]) is True

    @pytest.mark.parametrize(
        argnames="operations",
        argvalues=[
            # wrapped operations are not equal
            (
                MockOperationWrapper(MockTextOperation()),
                MockOperationWrapper(MockIntOperation()),
            ),
            # different higher order operation wrapper
            (
                MockOperationWrapper(MockTextOperation()),
                MockOperationWrapper2(MockTextOperation()),
            ),
            # not operation
            (MockOperationWrapper(MockTextOperation()), MockLinkSelector()),
        ],
    )
    def test_two_tag_selectors_are_not_equal(self, operations: tuple):
        """Tests if two wrappers are not equal."""
        assert (operations[0] == operations[1]) is False

    @pytest.mark.parametrize(
        argnames="operations",
        argvalues=[
            # different higher order operation wrapper
            (
                MockOperationWrapper(MockTextOperation()),
                MockOperationWrapper2(MockTextOperation()),
            ),
            # not operation
            (MockOperationWrapper(MockTextOperation()), MockLinkSelector()),
            # simple operation
            (MockOperationWrapper(MockTextOperation()), MockIntOperation()),
        ],
    )
    def test_equality_check_returns_not_implemented(self, operations: tuple):
        """Tests if equality check returns NotImplemented for non comparable types."""
        result = operations[0].__eq__(operations[1])
        assert result is NotImplemented


@pytest.mark.operation
class TestSuppress:
    """Unit test suite for Suppress operation wrapper."""

    def test_execute_returns_none_if_operation_failed(self):
        """
        Tests if execute method returns None if operation failed
        and raised FailedOperationException.
        """
        wrapper = Suppress(MockIntOperation())
        result = wrapper.execute("text")
        assert result is None

    def test_execute_raises_error_if_nto_caused_by_category_exception(self):
        """
        Tests if execute method raises FailedOperationExecution if operation failed
        and raised exception not caused by category exception.
        """
        wrapper = Suppress(MockIntOperation(), category=AttributeError)

        with pytest.raises(FailedOperationExecution):
            wrapper.execute("text")

    def test_execute_raises_error_if_not_caused_by_category_tuple(self):
        """
        Tests if execute method raises FailedOperationExecution if operation failed
        and raised exception not caused by any category of exceptions
        specified in the tuple.
        """
        wrapper = Suppress(MockIntOperation(), category=(AttributeError, TypeError))

        with pytest.raises(FailedOperationExecution):
            wrapper.execute("text")

    def test_execute_returns_none_if_operation_failed_with_exception_category(self):
        """
        Tests if execute method returns None if operation failed and raised
        exception specified in the category.
        """
        wrapper = Suppress(MockIntOperation(), category=ValueError)
        result = wrapper.execute("text")
        assert result is None

    def test_execute_returns_none_if_subclass_of_exception_category_was_cause(self):
        """
        Tests if execute method returns None if operation failed and raised
        any subclass of the exception specified in the category.
        """

        class MockError(ValueError): ...

        class MockFailsOperation(BaseMockOperation):

            def _execute(self, arg: str) -> int:
                raise MockError

        wrapper = Suppress(MockFailsOperation(), category=ValueError)
        result = wrapper.execute("text")
        assert result is None

    def test_execute_returns_none_if_operation_failed_with_category_tuple(self):
        """
        Tests if execute method returns None if operation failed and raised
        any category of exceptions specified in the tuple.
        """
        wrapper = Suppress(MockIntOperation(), category=(AttributeError, ValueError))
        result = wrapper.execute("text")
        assert result is None

    def test_execute_returns_values_successfully_returned_by_operation(self):
        """Tests if execute method returns values successfully returned by operation."""
        wrapper = Suppress(MockIntOperation())
        result = wrapper.execute("12")
        assert result == 12


@pytest.mark.operation
class TestSkipNone:
    """Unit test suite for SkipNone operation wrapper."""

    def test_execute_returns_none_if_operation_failed(self):
        """
        Tests if execute method returns None if operation failed
        and raised FailedOperationException.
        """
        wrapper = SkipNone(MockIntOperation())
        result = wrapper.execute(None)
        assert result is None

    def test_execute_returns_values_successfully_returned_by_operation(self):
        """
        Tests if execute method executes wrapped operation and
        returns values successfully returned by operation.
        """
        wrapper = SkipNone(MockIntOperation())
        result = wrapper.execute("12")
        assert result == 12

    def test_execute_raises_error_if_operation_failed(self):
        """
        Tests if execute method raises FailedOperationExecution if operation failed.
        It propagates any exception raised by the wrapped operation.
        """
        wrapper = SkipNone(MockIntOperation())

        with pytest.raises(FailedOperationExecution):
            wrapper.execute("text")
