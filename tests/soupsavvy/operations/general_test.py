"""Testing module for general operations."""

from dataclasses import dataclass
from typing import Any, Callable

import pytest

from soupsavvy.exceptions import FailedOperationExecution, NotOperationException
from soupsavvy.operations.general import Operation, OperationPipeline, Text
from tests.soupsavvy.operations.conftest import MockIntOperation, MockTextOperation
from tests.soupsavvy.selectors.conftest import MockLinkSelector, to_bs


@dataclass
class OperationTestInput:
    """Dataclass for Operation test inputs."""

    operation: Callable
    arg: Any
    expected: Any


def mock_operation_func(arg: Any):
    """
    Mock operation function for testing. If arg is "+", returns True, otherwise False.
    If arg is None, raises ValueError.
    """
    if arg is None:
        raise ValueError("Argument cannot be None.")

    return arg == "+"


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

    def test_eq_returns_true_if_same_operation(self):
        """Tests if __eq__ method returns True if objects are equal."""
        assert (
            Operation(mock_operation_func) == Operation(mock_operation_func)
        ) is True

    @pytest.mark.parametrize(
        argnames="operations",
        argvalues=[
            (Operation(str.upper), Operation(str.lower)),
            (Operation(lambda x: x), Operation(lambda x: x)),
            (Operation(lambda x: x), MockIntOperation()),
        ],
    )
    def test_eq_returns_false_if_different_operation(self, operations: tuple):
        """Tests if __eq__ method returns False if functions are not the same."""
        operation1, operation2 = operations
        assert (operation1 == operation2) is False


@pytest.mark.operation
class TestText:
    """Class with unit test suite for Text operation."""

    def test_raises_error_when_input_not_bs4_tag(self):
        """Tests if execute method raises FailedOperationExecution if input is not bs4 tag."""
        text = """
            <div href="github">Hello world</div>
        """
        operation = Text()

        with pytest.raises(FailedOperationExecution):
            operation.execute(text)

    def test_returns_empty_string_if_no_text_node(self):
        """
        Tests if execute method returns empty string if no text node in BeautifulSoup Tag.
        """
        text = """
            <div href="github"></div>
        """
        bs = to_bs(text).div
        operation = Text()
        result = operation.execute(bs)
        assert result == ""

    def test_returns_text_of_tag(self):
        """
        Tests if execute method returns text of a BeautifulSoup Tag when single text node.
        By default text is not stripped.
        """
        text = """
            <div href="github"> Hello world\n</div>
        """
        bs = to_bs(text).div
        operation = Text()
        result = operation.execute(bs)
        assert result == " Hello world\n"

    def test_returns_concatenated_text_of_tag(self):
        """
        Tests if execute method returns concatenated text of a BeautifulSoup Tag,
        when multiple text nodes. Default separator is empty string.
        """
        text = """
            <div href="github"><a>Hello</a><a>world</a></div>
        """
        bs = to_bs(text).div
        operation = Text()
        result = operation.execute(bs)
        assert result == "Helloworld"

    def test_returns_concatenated_text_of_tag_with_separator(self):
        """
        Tests if execute method returns concatenated text of a BeautifulSoup Tag
        with specified separator when multiple text nodes.
        """
        text = """
            <div href="github"><a>Hello</a><a>world</a></div>
        """
        bs = to_bs(text).div
        operation = Text(separator="---")
        result = operation.execute(bs)
        assert result == "Hello---world"

    def test_returns_stripped_text_of_tag(self):
        """
        Tests if execute method returns stripped text of a BeautifulSoup Tag
        if strip is True and single text node.
        """
        text = """
            <div href="github">\n\nHello world </div>
        """
        bs = to_bs(text).div
        operation = Text(strip=True)
        result = operation.execute(bs)
        assert result == "Hello world"

    def test_returns_concatenated_and_stripped_text_of_tag(self):
        """
        Tests if execute method returns concatenated and stripped text
        of a BeautifulSoup Tag if strip is True and multiple text nodes.
        """
        text = """
            <div href="github">
                \nHell  \n
                <span>  o  \n\n</span>
                <a>world  </a>
            </div>
        """
        bs = to_bs(text).div
        operation = Text(strip=True)
        result = operation.execute(bs)
        assert result == "Helloworld"

    def test_returns_concatenated_with_separator_and_stripped_text_of_tag(self):
        """
        Tests if execute method returns concatenated and stripped text
        of a BeautifulSoup Tag when both separator and strip are specified.
        """
        text = """
            <div href="github">
                \nHello  \n
                <a>world  </a>
            </div>
        """
        bs = to_bs(text).div
        operation = Text(strip=True, separator=" ")
        result = operation.execute(bs)
        assert result == "Hello world"

    def test_returns_text_with_find_method(self):
        """
        Tests if find method returns text of a BeautifulSoup Tag, it calls
        execute method. This is for done for convenience and compatibility with
        TagSearcher interface.
        """
        text = """
            <div href="github">Hello world</div>
        """
        bs = to_bs(text).div
        operation = Text()
        result = operation.find(bs)  # type: ignore
        assert result == "Hello world"

    def test_returns_list_with_single_element_with_find_all_method(self):
        """
        Tests if find_all method returns text of a BeautifulSoup Tag wrapped
        in single element list. This is for done for compatibility with
        TagSearcher interface.
        """
        text = """
            <div href="github">Hello world</div>
        """
        bs = to_bs(text).div
        operation = Text()
        result = operation.find_all(bs)  # type: ignore
        assert result == ["Hello world"]

    def test_raises_error_when_find_methods_get_not_tag(self):
        """
        Tests if find and find_all methods raise FailedOperationExecution
        if input is not bs4 tag.
        """
        operation = Text()

        with pytest.raises(FailedOperationExecution):
            operation.find("string")  # type: ignore

        with pytest.raises(FailedOperationExecution):
            operation.find_all("string")  # type: ignore

    @pytest.mark.parametrize(
        argnames="operations",
        argvalues=[
            (Text(), Text()),
            (Text(strip=True), Text(strip=True)),
            (Text(separator="---"), Text(separator="---")),
            (Text(strip=True, separator="---"), Text(strip=True, separator="---")),
        ],
    )
    def test_eq_returns_true_if_same_operation(self, operations: tuple):
        """Tests if __eq__ method returns True if objects are equal."""
        operation1, operation2 = operations
        assert (operation1 == operation2) is True

    @pytest.mark.parametrize(
        argnames="operations",
        argvalues=[
            (Text(strip=False), Text(strip=True)),
            (Text(separator="."), Text(separator="---")),
            (Text(strip=True, separator="."), Text(strip=True, separator="-")),
            (Text(strip=True, separator="."), Text(strip=False, separator=".")),
            (Text(), MockIntOperation()),
        ],
    )
    def test_eq_returns_false_if_different_operation(self, operations: tuple):
        """Tests if __eq__ method returns False if objects are not equal."""
        operation1, operation2 = operations
        assert (operation1 == operation2) is False


class MockText(str):
    """Mock class that imitates bs4 Tag with text attribute."""

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
