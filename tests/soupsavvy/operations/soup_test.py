"""
Module with unit tests for operations.soup module
with Operations specific to BeautifulSoup tags.
"""

import pytest

from soupsavvy.exceptions import FailedOperationExecution, NotOperationException
from soupsavvy.operations.general import OperationPipeline
from soupsavvy.operations.soup import Href, Parent, Text
from soupsavvy.selectors.logical import SelectorList
from tests.soupsavvy.conftest import (
    MockIntOperation,
    MockLinkSelector,
    strip,
    to_element,
)


@pytest.mark.operation
class TestText:
    """Class with unit test suite for Text operation."""

    def test_raises_error_when_input_not_bs4_tag(self):
        """
        Tests if execute method raises FailedOperationExecution
        if input is not bs4 tag.
        """
        text = """
            <div href="github">Hello world</div>
        """
        operation = Text()

        with pytest.raises(FailedOperationExecution):
            operation.execute(text)

    def test_returns_empty_string_if_no_text_node(self):
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

    def test_returns_text_of_tag(self):
        """
        Tests if execute method returns text of a BeautifulSoup Tag
        when single text node. By default text is not stripped.
        """
        text = """
            <div href="github"> Hello world\n</div>
        """
        bs = to_element(text).find_all("div")[0]
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
        bs = to_element(text).find_all("div")[0]
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
        bs = to_element(text).find_all("div")[0]
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
        bs = to_element(text).find_all("div")[0]
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
        bs = to_element(text).find_all("div")[0]
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
        bs = to_element(text).find_all("div")[0]
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
            (Text(), MockIntOperation()),
        ],
    )
    def test_eq_returns_false_if_different_operation(self, operations: tuple):
        """Tests if __eq__ method returns False if objects are not equal."""
        operation1, operation2 = operations
        assert (operation1 == operation2) is False


@pytest.mark.operation
class TestHref:
    """Class with unit test suite for Href operation."""

    def test_raises_error_when_input_not_bs4_tag(self):
        """
        Tests if execute method raises FailedOperationExecution
        if input is not bs4 tag.
        """
        text = """
            <div href="github">Hello world</div>
        """
        operation = Href()

        with pytest.raises(FailedOperationExecution):
            operation.execute(text)

    def test_returns_none_if_no_href_in_element(self):
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

    def test_returns_href_of_tag(self):
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

    def test_raises_error_when_input_not_bs4_tag(self):
        """
        Tests if execute method raises FailedOperationExecution
        if input is not bs4 tag.
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

    def test_returns_none_if_no_href_in_element(self):
        """
        Tests if execute method returns None if no parent provided element
        does not have parent. It must be `html` tag.
        """
        text = """
            <div>
                <div href="github"><a>Hello</a></div>
            </div>
            <span>Hello</span>
        """
        bs = to_element(text)
        operation = Parent()
        result = operation.execute(bs)
        assert result is None

    def test_returns_parent_of_tag(self):
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

    def test_returns_parent_with_find_method(self):
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

    def test_returns_list_with_single_element_with_find_all_method(self):
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

    def test_raises_error_when_find_methods_get_not_tag(self):
        """
        Tests if find and find_all methods raise FailedOperationExecution
        if input is not bs4 tag.
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
