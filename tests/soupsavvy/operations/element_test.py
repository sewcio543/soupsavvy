"""
Module with unit tests for operations.element module
with Operations specific to IElement interface.
"""

import pytest

from soupsavvy.exceptions import FailedOperationExecution, NotOperationException
from soupsavvy.operations.element import Href, Parent, Text
from soupsavvy.operations.general import OperationPipeline
from soupsavvy.selectors.logical import SelectorList
from tests.soupsavvy.conftest import (
    MockIntOperation,
    MockLinkSelector,
    ToElement,
    strip,
)


@pytest.mark.operation
class TestText:
    """Class with unit test suite for Text operation."""

    def test_raises_error_when_input_does_not_have_text_attribute(self):
        """
        Tests if execute method raises FailedOperationExecution
        if input does not have text attribute.
        """
        text = """
            <div href="github">Hello world</div>
        """
        operation = Text()

        with pytest.raises(FailedOperationExecution):
            operation.execute(text)

    def test_returns_empty_string_if_no_text_node(self, to_element: ToElement):
        """
        Tests if execute method returns empty string
        if no text node in BeautifulSoup Tag.
        """
        text = """
            <div href="github"></div>
        """
        bs = to_element(text).find_all("div")[0]
        operation = Text()
        result = operation.execute(bs)
        assert result == ""

    def test_returns_text_of_the_element_with_only_text_node(
        self, to_element: ToElement
    ):
        """Tests if execute method returns text of the element with only text node."""
        text = """
            <div href="github">Hello</div>
        """
        bs = to_element(text).find_all("div")[0]
        operation = Text()
        result = operation.execute(bs)
        assert result == "Hello"

    def test_returns_concatenated_text_of_multiple_nodes(self, to_element: ToElement):
        """
        Tests if execute method returns concatenated text of multiple text nodes
        that are children of element.
        """
        text = """
            <div href="github">He<a>ll</a>o<p>world</p></div>
        """
        bs = to_element(text).find_all("div")[0]
        operation = Text()
        result = operation.execute(bs)
        assert result.replace("\n", "") == "Helloworld"

    @pytest.mark.parametrize(
        argnames="operations",
        argvalues=[(Text(), Text())],
    )
    def test_eq_returns_true_if_same_operation(self, operations: tuple):
        """Tests if __eq__ method returns True if objects are equal."""
        operation1, operation2 = operations
        assert (operation1 == operation2) is True

    @pytest.mark.parametrize(
        argnames="operations",
        argvalues=[(Text(), MockIntOperation())],
    )
    def test_eq_returns_false_if_different_operation(self, operations: tuple):
        """Tests if __eq__ method returns False if objects are not equal."""
        operation1, operation2 = operations
        assert (operation1 == operation2) is False


@pytest.mark.operation
class TestHref:
    """Class with unit test suite for Href operation."""

    def test_raises_error_when_input_not_element(self):
        """
        Tests if execute method raises FailedOperationExecution
        if input is not IElement.
        """
        text = """
            <div href="github">Hello world</div>
        """
        operation = Href()

        with pytest.raises(FailedOperationExecution):
            operation.execute(text)

    def test_returns_none_if_no_href_in_element(self, to_element: ToElement):
        """
        Tests if execute method returns None if no href attribute in BeautifulSoup Tag.
        """
        text = """
            <div class="github"></div>
        """
        bs = to_element(text).find_all("div")[0]
        operation = Href()
        result = operation.execute(bs)
        assert result is None

    def test_returns_href_of_tag(self, to_element: ToElement):
        """
        Tests if execute method returns href attribute of a BeautifulSoup Tag
        if present in the element.
        """
        text = """
            <div href="github" class="menu">Hello world/div>
        """
        bs = to_element(text).find_all("div")[0]
        operation = Href()
        result = operation.execute(bs)
        assert result == "github"

    @pytest.mark.parametrize(
        argnames="operations",
        argvalues=[(Href(), Href())],
    )
    def test_eq_returns_true_if_same_operation(self, operations: tuple):
        """Tests if __eq__ method returns True if objects are equal."""
        operation1, operation2 = operations
        assert (operation1 == operation2) is True

    @pytest.mark.parametrize(
        argnames="operations",
        argvalues=[
            (Href(), MockIntOperation()),
            (Href(), MockLinkSelector()),
        ],
    )
    def test_eq_returns_false_if_different_operation(self, operations: tuple):
        """Tests if __eq__ method returns False if objects are not equal."""
        operation1, operation2 = operations
        assert (operation1 == operation2) is False


@pytest.mark.operation
class TestParent:
    """Class with unit test suite for Parent operation."""

    def test_raises_error_when_input_not_element(self):
        """
        Tests if execute method raises FailedOperationExecution
        if input is not IElement.
        """
        text = """
            <div>
                <div href="github"><a>Hello</a></div>
            </div>
            <span>Hello</span>
        """
        operation = Parent()

        with pytest.raises(FailedOperationExecution):
            operation.execute(text)

    def test_returns_none_if_no_parent(self, to_element: ToElement):
        """
        Tests if execute method returns None if no parent provided element
        does not have parent. It must be `html` root element.
        """
        text = """
            <div>
                <div href="github"><a>Hello</a></div>
            </div>
            <span>Hello</span>
        """
        bs = to_element(text)

        while bs.parent:
            bs = bs.parent

        operation = Parent()
        result = operation.execute(bs)
        assert result is None

    def test_returns_parent_of_tag(self, to_element: ToElement):
        """
        Tests if execute method returns parent of provided BeautifulSoup Tag.
        """
        text = """
            <div>
                <div href="github"><a>Hello</a></div>
            </div>
            <span>Hello</span>
        """
        bs = to_element(text).find_all("a")[0]
        operation = Parent()
        result = operation.execute(bs)
        assert strip(str(result)) == strip('<div href="github"><a>Hello</a></div>')

    def test_returns_parent_with_find_method(self, to_element: ToElement):
        """
        Tests if find method returns parent of a BeautifulSoup Tag, it calls
        execute method. This is for done for convenience and compatibility with
        TagSearcher interface.
        """
        text = """
            <div>
                <div href="github"><a>Hello</a></div>
            </div>
            <span>Hello</span>
        """
        bs = to_element(text).find_all("a")[0]
        operation = Parent()
        result = operation.find(bs)  # type: ignore
        assert strip(str(result)) == strip('<div href="github"><a>Hello</a></div>')

    def test_returns_list_with_single_element_with_find_all_method(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find_all method returns parent of a BeautifulSoup Tag wrapped
        in single element list. This is for done for compatibility with
        TagSearcher interface.
        """
        text = """
            <div>
                <div href="github"><a>Hello</a></div>
            </div>
            <span>Hello</span>
        """
        bs = to_element(text).find_all("a")[0]
        operation = Parent()
        result = operation.find_all(bs)  # type: ignore
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip('<div href="github"><a>Hello</a></div>')
        ]

    def test_raises_error_when_find_methods_gets_invalid_input(self):
        """
        Tests if find and find_all methods raise FailedOperationExecution
        if input is not IElement.
        """
        operation = Parent()

        with pytest.raises(FailedOperationExecution):
            operation.find("string")  # type: ignore

        with pytest.raises(FailedOperationExecution):
            operation.find_all("string")  # type: ignore

    @pytest.mark.parametrize(
        argnames="operations",
        argvalues=[(Parent(), Parent())],
    )
    def test_eq_returns_true_if_same_operation(self, operations: tuple):
        """Tests if __eq__ method returns True if objects are equal."""
        operation1, operation2 = operations
        assert (operation1 == operation2) is True

    @pytest.mark.parametrize(
        argnames="operations",
        argvalues=[
            (Parent(), MockIntOperation()),
            (Parent(), MockLinkSelector()),
        ],
    )
    def test_eq_returns_false_if_different_operation(self, operations: tuple):
        """Tests if __eq__ method returns False if objects are not equal."""
        operation1, operation2 = operations
        assert (operation1 == operation2) is False

    def test_piping_with_selector_returns_selector_list(self):
        """Tests if piping operation with selector returns SelectorList."""
        parent = Parent()
        selector = MockLinkSelector()
        result = parent | selector
        assert result == SelectorList(parent, selector)

    def test_piping_with_operator_returns_operation_pipeline(self):
        """Tests if piping operation with another operation returns OperationPipeline."""
        parent = Parent()
        operation = MockIntOperation()
        result = parent | operation
        assert result == OperationPipeline(parent, operation)

    def test_piping_with_invalid_type_raises_error(self):
        """
        Tests if piping operation with invalid type raises error.
        In this case, it defaults to BaseOperation implementation,
        which raises NotOperationException
        """
        parent = Parent()

        with pytest.raises(NotOperationException):
            parent | "string"  # type: ignore
