"""Testing module for general operations."""

from itertools import product
from typing import Any

import pytest
from bs4 import Tag

from soupsavvy.exceptions import FailedOperationExecution, NotOperationException
from soupsavvy.operations.base import OperationSearcherMixin, check_operation
from soupsavvy.operations.general import OperationPipeline
from tests.soupsavvy.operations.conftest import MockIntOperation, MockTextOperation
from tests.soupsavvy.selectors.conftest import MockLinkSelector, to_bs


@pytest.mark.operation
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


@pytest.mark.operation
class TestCheckOperation:
    """
    Class for testing check_operation function.
    Ensures that provided object is a valid `soupsavvy` operation.
    """

    def test_passes_check_and_returns_the_same_object(self):
        """
        Tests if check_operator returns the same object
        if it is instance of BaseOperation.
        """
        operation = MockTextOperation()
        result = check_operation(operation)
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
            check_operation("selector")

    def test_raises_exception_with_custom_message_when_specified(self):
        """
        Tests if check_operator raises NotOperationException with custom message
        if object is not instance of BaseOperation and message is specified.
        """
        message = "Custom message"

        with pytest.raises(NotOperationException, match=message):
            check_operation("operation", message=message)


class MockNameOperation(OperationSearcherMixin):
    """
    Mock class for testing OperationSearcherMixin class.
    Extract name of provided tag from bs4.Tag object.
    """

    def _execute(self, arg: Tag):
        if not isinstance(arg, Tag):
            raise TypeError

        return arg.name

    def __eq__(self, x: Any) -> bool: ...


div: Tag = to_bs("""<div></div>""").div  # type: ignore
MOCK = MockNameOperation()


class TestOperationSearcherMixin:
    """Class for testing OperationSearcherMixin class."""

    @pytest.mark.parametrize(
        argnames="strict, recursive",
        argvalues=list(product([True, False], [True, False])),
    )
    def test_find_method_calls_execute_and_returns_its_result(
        self, strict: bool, recursive: bool
    ):
        """
        Tests if find method calls execute and returns its result.
        Result should be the same as from execute method.
        Other find parameters are ignored and operation
        is performed always in the same way.
        """
        assert (
            MOCK.find(div, strict=strict, recursive=recursive)
            == "div"
            == MOCK.execute(div)
        )

    @pytest.mark.parametrize(
        argnames="limit, recursive",
        argvalues=list(product([None, 2], [True, False])),
    )
    def test_find_all_returns_list_with_single_element_from_execute_call(
        self, limit, recursive: bool
    ):
        """
        Tests if find_all method returns list with single element
        that is result of execute call.
        Other find_all parameters are ignored and operation
        is performed always in the same way.
        """
        result = MOCK.find_all(div, recursive=recursive, limit=limit)
        assert result == ["div"]

    def test_find_methods_raise_exception_if_execute_failed(self):
        """
        Tests if find methods and execute method raise FailedOperationExecution
        if operation failed.
        """

        with pytest.raises(FailedOperationExecution):
            MOCK.execute("div")

        with pytest.raises(FailedOperationExecution):
            MOCK.find("div")  # type: ignore

        with pytest.raises(FailedOperationExecution):
            MOCK.find_all("div")  # type: ignore
