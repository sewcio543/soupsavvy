"""Testing module for SelectionPipeline class."""

import pytest

from soupsavvy.exceptions import (
    NotOperationException,
    NotTagSearcherException,
    TagNotFoundException,
)
from soupsavvy.operations.general import OperationPipeline
from soupsavvy.operations.selection_pipeline import SelectionPipeline
from tests.soupsavvy.conftest import (
    MockDivSelector,
    MockIntOperation,
    MockLinkSelector,
    MockTextOperation,
    ToElement,
)


@pytest.mark.selector
@pytest.mark.operation
class TestSelectionPipeline:
    """Class for SelectionPipeline unit test suite."""

    def test_raises_error_when_invalid_selector(self):
        """
        Tests if raises NotTagSearcherException on init
        when invalid selector is passed.
        """
        with pytest.raises(NotTagSearcherException):
            SelectionPipeline(
                MockTextOperation(),  # type: ignore
                MockIntOperation(),
            )

    def test_find_returns_first_tag_matching_selector(self, to_element: ToElement):
        """Tests if find method returns first tag matching selector."""
        text = """
            <div href="github"></div>
            <h1 class="widget">1</h1>
            <a>1</a>
            <a>2</a>
        """
        bs = to_element(text)
        selector = SelectionPipeline(MockLinkSelector(), MockTextOperation())
        result = selector.find(bs)
        assert result == "1"

    def test_selector_can_be_any_tag_searcher(self, to_element: ToElement):
        """
        Tests if selector passed to SelectionPipeline can be any TagSearcher,
        not necessarily a selector. In this case, SelectionPipeline.
        """
        text = """
            <div href="github"></div>
            <h1 class="widget">1</h1>
            <a>1</a>
            <a>2</a>
        """
        bs = to_element(text)
        selector = SelectionPipeline(
            SelectionPipeline(MockLinkSelector(), MockTextOperation()),
            MockIntOperation(),
        )
        result = selector.find(bs)
        assert result == 1

    def test_find_returns_none_if_no_match_and_strict_false(
        self, to_element: ToElement
    ):
        """
        Tests if find returns None if no element matches the selector
        and strict is False.
        """
        text = """
            <div href="github"></div>
            <h1 class="widget">1</h1>
        """
        bs = to_element(text)
        selector = SelectionPipeline(
            MockLinkSelector(), MockTextOperation(skip_none=True)
        )
        result = selector.find(bs)
        assert result is None

    def test_find_raises_exception_if_no_match_and_strict_true(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find raises TagNotFoundException if no element matches the selector
        and strict is True.
        """
        text = """
            <div href="github"></div>
            <h1 class="widget">1</h1>
        """
        bs = to_element(text)
        selector = SelectionPipeline(MockLinkSelector(), MockTextOperation())

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_all_returns_empty_list_when_no_match(self, to_element: ToElement):
        """Tests if find returns an empty list if no element matches the selector."""
        text = """
            <div href="github"></div>
            <h1 class="widget">1</h1>
        """
        bs = to_element(text)
        selector = SelectionPipeline(MockLinkSelector(), MockTextOperation())
        result = selector.find_all(bs)
        assert result == []

    def test_find_all_returns_all_matching_elements(self, to_element: ToElement):
        """Tests if find_all returns a list of all matching elements."""
        text = """
            <div href="github"></div>
            <a>1</a>
            <h1 class="widget">1</h1>
            <a>2</a>
            <div><a>3</a></div>
            <a>Text Hello</a>
        """
        bs = to_element(text)
        selector = SelectionPipeline(MockLinkSelector(), MockTextOperation())
        result = selector.find_all(bs)
        assert result == ["1", "2", "3", "Text Hello"]

    def test_find_returns_first_matching_child_if_recursive_false(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        text = """
            <div href="github"></div>
            <div><a>Not child</a></div>
            <a>1</a>
            <h1 class="widget">1</h1>
            <a>2</a>
            <a>Text Hello</a>
        """
        bs = to_element(text)
        selector = SelectionPipeline(MockLinkSelector(), MockTextOperation())
        result = selector.find(bs, recursive=False)
        assert result == "1"

    def test_find_returns_none_if_recursive_false_and_no_matching_child(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div href="github"></div>
            <div><a>Not child</a></div>
            <h1 class="widget">1</h1>
        """
        bs = to_element(text)
        selector = SelectionPipeline(
            MockLinkSelector(), MockTextOperation(skip_none=True)
        )
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <div href="github"></div>
            <div><a>Not child</a></div>
            <h1 class="widget">1</h1>
        """
        bs = to_element(text)
        selector = SelectionPipeline(MockLinkSelector(), MockTextOperation())

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True, recursive=False)

    def test_find_all_returns_all_matching_children_when_recursive_false(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <div href="github"></div>
            <div><a>Not child</a></div>
            <a>1</a>
            <h1 class="widget">1</h1>
            <a>2</a>
            <a>Text Hello</a>
        """
        bs = to_element(text)
        selector = SelectionPipeline(MockLinkSelector(), MockTextOperation())
        result = selector.find_all(bs, recursive=False)
        assert result == ["1", "2", "Text Hello"]

    def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find_all returns an empty list if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div href="github"></div>
            <div><a>Not child</a></div>
            <h1 class="widget">1</h1>
        """
        bs = to_element(text)
        selector = SelectionPipeline(MockLinkSelector(), MockTextOperation())
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_only_x_elements_when_limit_is_set(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <div href="github"></div>
            <a>1</a>
            <h1 class="widget">1</h1>
            <a>2</a>
            <div><a>3</a></div>
            <a>Text Hello</a>
        """
        bs = to_element(text)
        selector = SelectionPipeline(MockLinkSelector(), MockTextOperation())
        result = selector.find_all(bs, limit=2)
        assert result == ["1", "2"]

    def test_find_all_returns_only_x_elements_when_limit_is_set_and_recursive_false(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find_all returns only x elements when limit is set and recursive
        is False. In this case only 2 first in order children matching
        the selector are returned.
        """
        text = """
            <div href="github"></div>
            <div><a>Not child</a></div>
            <a>1</a>
            <h1 class="widget">1</h1>
            <a>2</a>
            <a>Text Hello</a>
        """
        bs = to_element(text)
        selector = SelectionPipeline(MockLinkSelector(), MockTextOperation())
        result = selector.find_all(bs, recursive=False, limit=2)
        assert result == ["1", "2"]

    @pytest.mark.parametrize(
        argnames="selectors",
        argvalues=[
            # both selectors and operations are the same
            (
                SelectionPipeline(MockLinkSelector(), MockTextOperation()),
                SelectionPipeline(MockLinkSelector(), MockTextOperation()),
            ),
        ],
    )
    def test_two_selectors_are_equal(self, selectors: tuple):
        """Tests if two instances of SelectionPipeline are equal."""
        assert (selectors[0] == selectors[1]) is True

    @pytest.mark.parametrize(
        argnames="selectors",
        argvalues=[
            # different operations
            (
                SelectionPipeline(MockLinkSelector(), MockTextOperation()),
                SelectionPipeline(MockLinkSelector(), MockIntOperation()),
            ),
            # different selectors
            (
                SelectionPipeline(MockDivSelector(), MockTextOperation()),
                SelectionPipeline(MockLinkSelector(), MockTextOperation()),
            ),
            # not SelectionPipeline
            (
                SelectionPipeline(MockDivSelector(), MockTextOperation()),
                MockDivSelector(),
            ),
        ],
    )
    def test_two_selectors_are_not_equal(self, selectors: tuple):
        """Tests if two instances of SelectionPipeline are not equal."""
        assert (selectors[0] == selectors[1]) is False

    def test_or_operator_pipes_operations(self):
        """
        Tests if | operator add next operation to the selection pipeline.
        Selector is not changed, but operation is piped.
        """
        selector = SelectionPipeline(MockLinkSelector(), MockTextOperation())
        next_operation = MockIntOperation()
        result = selector | next_operation

        assert isinstance(result, SelectionPipeline)
        assert result.selector == selector.selector
        assert result.operation == OperationPipeline(selector.operation, next_operation)

    def test_or_operator_raises_error_if_not_operation(self):
        """
        Tests if | operator raises NotOperationException if not used with BaseOperation.
        """
        selector = SelectionPipeline(MockLinkSelector(), MockTextOperation())
        next_operation = MockLinkSelector()

        with pytest.raises(NotOperationException):
            selector | next_operation
