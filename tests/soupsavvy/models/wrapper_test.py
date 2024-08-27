"""Module with unit tests for wrappers in soupsavvy.models module."""

from typing import Any, Type

import pytest
from bs4 import Tag

from soupsavvy.exceptions import (
    FailedOperationExecution,
    NotOperationException,
    NotTagSearcherException,
    RequiredConstraintException,
    TagNotFoundException,
)
from soupsavvy.models.wrappers import (
    All,
    Default,
    FieldWrapper,
    OperationWrapper,
    Required,
    SkipNone,
    Suppress,
)
from soupsavvy.operations.selection_pipeline import SelectionPipeline
from tests.soupsavvy.operations.conftest import MockIntOperation, MockTextOperation
from tests.soupsavvy.selectors.conftest import (
    MockDivSelector,
    MockLinkSelector,
    find_body_element,
    strip,
    to_bs,
)

DEFAULT = "default"


class MockFieldWrapper(FieldWrapper):
    """Mock class for testing FieldWrapper interface."""

    def find(self, tag: Tag, strict: bool = False, recursive: bool = True): ...


class MockFieldWrapper2(FieldWrapper):
    """Mock class for testing FieldWrapper interface."""

    def find(self, tag: Tag, strict: bool = False, recursive: bool = True): ...


@pytest.mark.selector
class TestFieldWrapper:
    """Class for testing FieldWrapper interface."""

    @pytest.mark.parametrize(
        argnames="selectors",
        argvalues=[
            # wrapped selectors are equal
            (
                MockFieldWrapper(MockLinkSelector()),
                MockFieldWrapper(MockLinkSelector()),
            ),
        ],
    )
    def test_two_tag_selectors_are_equal(self, selectors: tuple):
        """Tests if selectors are equal."""
        assert (selectors[0] == selectors[1]) is True

    @pytest.mark.parametrize(
        argnames="selectors",
        argvalues=[
            # wrapped selectors are not equal
            (MockFieldWrapper(MockLinkSelector()), MockFieldWrapper(MockDivSelector())),
            # different higher order field wrapper
            (
                MockFieldWrapper(MockLinkSelector()),
                MockFieldWrapper2(MockLinkSelector()),
            ),
            # not tag searcher
            (MockFieldWrapper(MockLinkSelector()), MockTextOperation()),
        ],
    )
    def test_two_tag_selectors_are_not_equal(self, selectors: tuple):
        """Tests if selector are not equal."""
        assert (selectors[0] == selectors[1]) is False

    def test_or_operator_raises_exception_if_not_operation(self):
        """
        Tests if `|` operator raises NotOperationException
        if not used with instance of BaseOperation.
        """
        with pytest.raises(NotOperationException):
            MockFieldWrapper(MockDivSelector()) | MockLinkSelector()  # type: ignore

    def test_or_operator_returns_selection_pipeline_on_operation(self):
        """
        Tests if `|` operator raises returns SelectionPipeline
        with correct selector and operation when used on FieldWrapper and BaseOperation.
        """
        wrapper = MockFieldWrapper(MockLinkSelector())
        operation = MockIntOperation()
        result = wrapper | operation

        assert isinstance(result, SelectionPipeline)
        assert result.selector == wrapper
        assert result.operation == operation


@pytest.mark.selector
class BaseFieldWrapperTest:
    wrapper: Type[FieldWrapper]
    params: dict = {}

    def test_raises_error_if_invalid_selector_passed(self):
        """
        Tests if raises NotTagSearcherException if invalid selector is passed.
        It expects instance of TagSearcher.
        """
        with pytest.raises(NotTagSearcherException):
            self.wrapper(MockTextOperation(), **self.params)  # type: ignore

    def test_find_all_return_all_elements_matched_by_selector(self):
        """Tests if find_all method returns all elements matched by selector."""
        text = """
            <div href="github"></div>
            <a>1</a>
            <h1><a>2</a></h1>
            <span>
                <h1>Hello</h1>
            </span>
            <a><p>3</p></a>
        """
        bs = to_bs(text)
        selector = self.wrapper(MockLinkSelector(), **self.params)
        result = selector.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a>1</a>"""),
            strip("""<a>2</a>"""),
            strip("""<a><p>3</p></a>"""),
        ]

    def test_find_all_returns_empty_list_if_no_matches(self):
        """
        Tests if find_all returns empty list if no element matches the selector.
        """
        text = """
            <div href="github"></div>
            <span class="widget"></span>
            <div><p>Hello</p></div>
        """
        bs = to_bs(text)
        selector = self.wrapper(MockLinkSelector(), **self.params)
        result = selector.find_all(bs)
        assert result == []

    def test_find_all_returns_list_of_matching_elements_with_recursive_false(self):
        """
        Tests if find_all method returns list of matching elements
        when recursive is False.
        """
        text = """
            <a>1</a>
            <div href="github"></div>
            <h1><a>Not child</a></h1>
            <a><p>2</p></a>
            <span>
                <h1>Hello</h1>
            </span>
            <a>3</a>
        """
        bs = find_body_element(to_bs(text))
        selector = self.wrapper(MockLinkSelector(), **self.params)
        result = selector.find_all(bs, recursive=False)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a>1</a>"""),
            strip("""<a><p>2</p></a>"""),
            strip("""<a>3</a>"""),
        ]

    def test_find_all_returns_empty_list_if_no_matches_with_recursive_false(self):
        """
        Tests if find_all method returns an empty list
        if no element matches the selector with recursive set to False.
        """
        text = """
            <div href="github"></div>
            <h1><a>Not child</a></h1>
            <span>
                <h1>Hello</h1>
                <a>Not child</a>
            </span>
        """
        bs = find_body_element(to_bs(text))
        selector = self.wrapper(MockLinkSelector(), **self.params)
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <div href="github"></div>
            <a>1</a>
            <h1><a>2</a></h1>
            <span>
                <h1>Hello</h1>
            </span>
            <a><p>3</p></a>
        """
        bs = to_bs(text)
        selector = self.wrapper(MockLinkSelector(), **self.params)
        result = selector.find_all(bs, limit=2)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a>1</a>"""),
            strip("""<a>2</a>"""),
        ]

    def test_find_all_returns_only_x_elements_when_limit_is_set_and_recursive_false(
        self,
    ):
        """
        Tests if find_all returns only x elements when limit is set and recursive
        is False. In this case only 2 first in order children matching
        the selector are returned.
        """
        text = """
            <a>1</a>
            <div href="github"></div>
            <h1><a>Not child</a></h1>
            <a><p>2</p></a>
            <span>
                <h1>Hello</h1>
            </span>
            <a>3</a>
        """
        bs = find_body_element(to_bs(text))
        selector = self.wrapper(MockLinkSelector(), **self.params)
        result = selector.find_all(bs, recursive=False, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a>1</a>"""),
            strip("""<a><p>2</p></a>"""),
        ]


class TestAll(BaseFieldWrapperTest):
    """Unit test suite for All wrapper."""

    wrapper = All

    def test_find_returns_all_elements_matched_by_selector(self):
        """Tests if find method returns all elements matched by selector."""
        text = """
            <div href="github"></div>
            <a>1</a>
            <h1><a>2</a></h1>
            <span>
                <h1>Hello</h1>
            </span>
            <a><p>3</p></a>
        """
        bs = to_bs(text)
        selector = All(MockLinkSelector())
        result = selector.find(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a>1</a>"""),
            strip("""<a>2</a>"""),
            strip("""<a><p>3</p></a>"""),
        ]

    @pytest.mark.parametrize(argnames="strict", argvalues=[True, False])
    def test_find_returns_empty_list_if_no_matches(self, strict: bool):
        """
        Tests if find returns an empty list if no element matches the selector.
        This behavior is the same for both strict and non-strict mode.
        """
        text = """
            <div href="github"></div>
            <span class="widget"></span>
            <div><p>Hello</p></div>
        """
        bs = to_bs(text)
        selector = All(MockLinkSelector())
        result = selector.find(bs, strict=strict)
        assert result == []

    def test_find_returns_list_of_matching_elements_with_recursive_false(self):
        """
        Tests if find method returns list of matching elements when recursive is False.
        """
        text = """
            <a>1</a>
            <div href="github"></div>
            <h1><a>Not child</a></h1>
            <a><p>2</p></a>
            <span>
                <h1>Hello</h1>
            </span>
            <a>3</a>
        """
        bs = find_body_element(to_bs(text))
        selector = All(MockLinkSelector())
        result = selector.find(bs, recursive=False)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a>1</a>"""),
            strip("""<a><p>2</p></a>"""),
            strip("""<a>3</a>"""),
        ]

    @pytest.mark.parametrize(argnames="strict", argvalues=[True, False])
    def test_find_returns_empty_list_if_no_matches_with_recursive_false(
        self, strict: bool
    ):
        """
        Tests if find method returns an empty list if no element matches the selector
        with recursive set to False. This behavior is the same for both strict and
        non-strict mode.
        """
        text = """
            <div href="github"></div>
            <h1><a>Not child</a></h1>
            <span>
                <h1>Hello</h1>
                <a>Not child</a>
            </span>
        """
        bs = find_body_element(to_bs(text))
        selector = All(MockLinkSelector())
        result = selector.find(bs, strict=strict, recursive=False)
        assert result == []


class TestRequired(BaseFieldWrapperTest):
    """Unit test suite for Required wrapper."""

    wrapper = Required

    def test_find_first_element_matched_by_selector(self):
        """Tests if find method returns first element matched by selector."""
        text = """
            <div href="github"></div>
            <span>
                <h1>Hello</h1>
            </span>
            <a>1</a>
            <h1><a>2</a></h1>
            <a><p>3</p></a>
        """
        bs = to_bs(text)
        selector = Required(MockLinkSelector())
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<a>1</a>""")

    def test_find_raises_error_if_no_matches_in_not_strict_mode(self):
        """
        Tests if find raises RequiredConstraintException if no element
        matches the selector in non-strict mode.
        """
        text = """
            <div href="github"></div>
            <span class="widget"></span>
            <div><p>Hello</p></div>
        """
        bs = to_bs(text)
        selector = Required(MockLinkSelector())

        with pytest.raises(RequiredConstraintException):
            selector.find(bs)

    def test_find_propagates_error_if_no_matches_in_strict_mode(self):
        """
        Tests if find propagates TagNotFoundException if no element
        matches the selector in strict mode.
        """
        text = """
            <div href="github"></div>
            <span class="widget"></span>
            <div><p>Hello</p></div>
        """
        bs = to_bs(text)
        selector = Required(MockLinkSelector())

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_returns_first_matching_element_with_recursive_false(self):
        """
        Tests if find method returns first matching element if recursive is False.
        """
        text = """
            <h1><a>Not child</a></h1>
            <span>
                <h1>Hello</h1>
                <a>Not child</a>
            </span>
            <a>1</a>
            <div href="github"></div>
            <a>2</a>
        """
        bs = find_body_element(to_bs(text))
        selector = Required(MockLinkSelector())
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<a>1</a>""")

    def test_find_raises_error_if_no_matches_with_recursive_false_and_not_strict_mode(
        self,
    ):
        """
        Tests if find method raises RequiredConstraintException if no element
        matches the selector and recursive is False in non-strict mode.
        """
        text = """
            <div href="github"></div>
            <h1><a>Not child</a></h1>
            <span>
                <h1>Hello</h1>
                <a>Not child</a>
            </span>
        """
        bs = find_body_element(to_bs(text))
        selector = Required(MockLinkSelector())

        with pytest.raises(RequiredConstraintException):
            selector.find(bs, recursive=False)

    def test_find_propagates_error_if_no_matches_with_recursive_false_and_strict_mode(
        self,
    ):
        """
        Tests if find method propagates TagNotFoundException if no element
        matches the selector and recursive is False in strict mode.
        """
        text = """
            <div href="github"></div>
            <h1><a>Not child</a></h1>
            <span>
                <h1>Hello</h1>
                <a>Not child</a>
            </span>
        """
        bs = find_body_element(to_bs(text))
        selector = Required(MockLinkSelector())

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True, recursive=False)


class TestDefault(BaseFieldWrapperTest):
    """Unit test suite for Default wrapper."""

    wrapper = Default
    params = {"default": DEFAULT}

    def test_find_first_element_matched_by_selector(self):
        """Tests if find method returns first element matched by selector."""
        text = """
            <div href="github"></div>
            <span>
                <h1>Hello</h1>
            </span>
            <a>1</a>
            <h1><a>2</a></h1>
            <a><p>3</p></a>
        """
        bs = to_bs(text)
        selector = Default(MockLinkSelector(), default=DEFAULT)
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<a>1</a>""")

    def test_find_returns_default_if_no_match_in_no_strict_mode(self):
        """
        Tests if find method returns default value if no element matches the selector
        and strict mode is False.
        """
        text = """
            <div href="github"></div>
            <span class="widget"></span>
            <div><p>Hello</p></div>
        """
        bs = to_bs(text)
        selector = Default(MockLinkSelector(), default=DEFAULT)
        result = selector.find(bs)
        assert result == DEFAULT

    def test_find_propagates_error_if_no_match_in_strict_mode(self):
        """
        Tests if find method propagates TagNotFoundException if no element
        matches the selector and strict mode is True. Default propagates
        any exception raised by the wrapped selector.
        """
        text = """
            <div href="github"></div>
            <span class="widget"></span>
            <div><p>Hello</p></div>
        """
        bs = to_bs(text)
        selector = Default(MockLinkSelector(), default=DEFAULT)

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_returns_first_matching_element_with_recursive_false(self):
        """
        Tests if find method returns first matching element if recursive is False.
        """
        text = """
            <h1><a>Not child</a></h1>
            <span>
                <h1>Hello</h1>
                <a>Not child</a>
            </span>
            <a>1</a>
            <div href="github"></div>
            <a>2</a>
        """
        bs = find_body_element(to_bs(text))
        selector = Default(MockLinkSelector(), default=DEFAULT)
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<a>1</a>""")

    def test_find_returns_default_if_no_matches_with_recursive_false_and_not_strict(
        self,
    ):
        """
        Tests if find method returns default value if no element matches the selector
        and recursive is False in non-strict mode.
        """
        text = """
            <div href="github"></div>
            <h1><a>Not child</a></h1>
            <span>
                <h1>Hello</h1>
                <a>Not child</a>
            </span>
        """
        bs = find_body_element(to_bs(text))
        selector = Default(MockLinkSelector(), default=DEFAULT)
        result = selector.find(bs, strict=False, recursive=False)
        assert result == DEFAULT

    def test_find_propagates_error_if_no_matches_with_recursive_false_and_strict(self):
        """
        Tests if find method propagates TagNotFoundException if no element
        matches the selector and recursive is False. Default propagates
        any exception raised by the wrapped selector.
        """
        text = """
            <div href="github"></div>
            <h1><a>Not child</a></h1>
            <span>
                <h1>Hello</h1>
                <a>Not child</a>
            </span>
        """
        bs = find_body_element(to_bs(text))
        selector = Default(MockLinkSelector(), default=DEFAULT)

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True, recursive=False)


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
            OperationWrapper(MockLinkSelector())  # type: ignore

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
