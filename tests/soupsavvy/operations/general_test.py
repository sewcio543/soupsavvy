"""Testing module for general operations."""

from dataclasses import dataclass
from typing import Any, Callable

import pytest

from soupsavvy.exceptions import FailedOperationExecution, InvalidOperationFunction
from soupsavvy.operations.general import Attribute, Operation, Text
from tests.soupsavvy.selectors.conftest import strip, to_bs


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


# invalid operations
def mandatory_keyword_param(*, arg1=1, arg2): ...


def multiple_mandatory_positional(arg, /, arg2, arg3=1): ...


class MockInvalidCallable:
    """
    Mock class for testing invalid operation functions.
    Both instance and `hello` class method are invalid operation functions.
    """

    def __call__(self, arg1, arg2): ...

    def hello(self, arg1):
        """Valid if called by instance, invalid if called by class."""


# valid operations
def one_mandatory(arg1, arg2=1): ...


def one_default(arg1=1): ...


def one_mandatory_positional(arg1, /, arg2=1): ...


def default_keywords(arg1, *, arg2=1, arg3=10): ...


class MockValidCallable:
    """
    Mock class for testing valid operation functions.
    All: instance, `hello` class method and `hi` instance method
    are valid operation functions.
    """

    def __call__(self, arg1): ...

    def hello(self, arg2=3):
        """Valid if called by instance, invalid if called by class."""

    def hi(self, arg1, arg2=2):
        """Valid if called by instance, invalid if called by class."""


class TestOperation:
    """Class with unit test suite for Operation class."""

    @pytest.mark.parametrize(
        argnames="param",
        argvalues=[
            "func",
            lambda x, y: x + y,
            lambda: 10,
            mandatory_keyword_param,
            multiple_mandatory_positional,
            MockInvalidCallable(),
            MockInvalidCallable.hello,
        ],
        ids=[
            "not_callable",
            "multiple_mandatory_args",
            "no_args",
            "mandatory_keyword_params",
            "multiple_mandatory_positional",
            "callable_instance",
            "class_method",
        ],
    )
    def test_raises_error_on_init_if_invalid_operation_function(self, param):
        """
        Tests if Operation init raises InvalidOperationFunction
        if invalid operation function. Invalid operation can have:
        * no arguments
        * multiple mandatory arguments
        * mandatory keyword-only arguments
        """
        with pytest.raises(InvalidOperationFunction):
            Operation(param)

    @pytest.mark.parametrize(
        argnames="param",
        argvalues=[
            lambda x: x,
            one_mandatory,
            one_default,
            one_mandatory_positional,
            default_keywords,
            MockValidCallable(),
            MockValidCallable.hello,
            MockValidCallable().hi,
        ],
        ids=[
            "only_one_arg",
            "one_mandatory",
            "one_default",
            "one_mandatory_positional",
            "default_keywords",
            "callable_instance",
            "class_method",
            "instance_method",
        ],
    )
    def test_assign_function_if_valid(self, param):
        """
        Tests if Operation init assigns provided function as operation and initializes
        without errors if valid operation function. Valid operation have:
        * at most one mandatory argument
        * at least one argument
        * no keyword-only arguments without default
        """
        operation = Operation(param)
        assert operation.operation is param

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
        """Tests if execute method raises FailedOperationExecution if operation fails."""
        operation = Operation(mock_operation_func)

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
            (Operation(lambda x: x), Text()),
        ],
    )
    def test_eq_returns_false_if_different_operation(self, operations: tuple):
        """Tests if __eq__ method returns False if functions are not the same."""
        operation1, operation2 = operations
        assert (operation1 == operation2) is False


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
            (Text(), Attribute("href")),
        ],
    )
    def test_eq_returns_false_if_different_operation(self, operations: tuple):
        """Tests if __eq__ method returns False if objects are not equal."""
        operation1, operation2 = operations
        assert (operation1 == operation2) is False


class TestAttribute:
    """Class with unit test suite for Attribute operation."""

    def test_raises_error_when_input_not_bs4_tag(self):
        """Tests if execute method raises FailedOperationExecution if input is not bs4 tag."""
        text = """
            <div href="github">Hello world</div>
        """
        operation = Attribute("href")

        with pytest.raises(FailedOperationExecution):
            operation.execute(text)

    def test_returns_empty_string_if_empty_attribute(self):
        """
        Tests if execute method returns empty string if given attribute is empty
        in BeautifulSoup Tag.
        """
        text = """
            <div href="">Hello world</div>
        """
        bs = to_bs(text).div
        operation = Attribute("href")
        result = operation.execute(bs)
        assert result == ""

    def test_returns_attribute_of_tag_as_string(self):
        """
        Tests if execute method returns attribute of a BeautifulSoup Tag as string,
        for any attribute type, except class if exists.
        """
        text = """
            <div id="123" href="github">Hello world</div>
        """
        bs = to_bs(text).div
        operation = Attribute("href")
        result = operation.execute(bs)
        assert result == "github"

    def test_returns_none_if_no_attribute(self):
        """
        Tests if execute method returns None if given attribute does not exist
        in BeautifulSoup Tag.
        """
        text = """
            <div id="123" class="github">Hello world</div>
        """
        bs = to_bs(text).div
        operation = Attribute("href")
        result = operation.execute(bs)
        assert result is None

    def test_returns_specified_default_if_no_attribute(self):
        """
        Tests if execute method returns specified default value if given attribute
        does not exist in BeautifulSoup Tag.
        """
        text = """
            <div id="123" class="github">Hello world</div>
        """
        bs = to_bs(text).div
        operation = Attribute("href", default="reddit")
        result = operation.execute(bs)
        assert result == "reddit"

    def test_returns_list_with_single_element_for_class_attribute(self):
        """
        Tests if execute method returns list with single element for class attribute
        if found in BeautifulSoup Tag.
        """
        text = """
            <div id="123" class="github">Hello world</div>
        """
        bs = to_bs(text).div
        operation = Attribute("class")
        result = operation.execute(bs)
        assert result == ["github"]

    def test_returns_list_with_multiple_element_for_class_attribute(self):
        """
        Tests if execute method returns list with multiple element for class attribute
        if found in BeautifulSoup Tag.
        """
        text = """
            <div id="123" class="github reddit tv_series">Hello world</div>
        """
        bs = to_bs(text).div
        operation = Attribute("class")
        result = operation.execute(bs)
        assert result == ["github", "reddit", "tv_series"]

    def test_returns_none_if_no_class_attribute(self):
        """
        Tests if execute method returns None if class attribute does not exist
        in BeautifulSoup Tag.
        """
        text = """
            <div id="123">Hello world</div>
        """
        bs = to_bs(text).div
        operation = Attribute("class")
        result = operation.execute(bs)
        assert result is None

    def test_returns_string_if_no_class_attribute_separated_by_spaces(self):
        """
        Tests if execute method returns string for any attribute that is not class
        if found in BeautifulSoup Tag and has value separated by spaces.
        """
        text = """
            <div id="123" name="github reddit tv_series">Hello world</div>
        """
        bs = to_bs(text).div
        operation = Attribute("name")
        result = operation.execute(bs)
        assert result == "github reddit tv_series"

    @pytest.mark.parametrize(
        argnames="operations",
        argvalues=[
            (Attribute("href"), Attribute("href")),
            (Attribute("href", default="github"), Attribute("href", default="github")),
        ],
    )
    def test_eq_returns_true_if_same_operation(self, operations: tuple):
        """Tests if __eq__ method returns True if objects are equal."""
        operation1, operation2 = operations
        assert (operation1 == operation2) is True

    @pytest.mark.parametrize(
        argnames="operations",
        argvalues=[
            (Attribute("href"), Attribute("class")),
            (Attribute("href", default="github"), Attribute("href", default="reddit")),
            (Attribute("href", default="github"), Attribute("class", default="github")),
            (Attribute("href"), Text()),
        ],
    )
    def test_eq_returns_false_if_different_operation(self, operations: tuple):
        """Tests if __eq__ method returns False if objects are not equal."""
        operation1, operation2 = operations
        assert (operation1 == operation2) is False
