"""
Testing module for testing basic functionality of SoupSelector interface.
Tests cover implementation of dunder method that are shared among all soupsavvy
selectors. There are syntactical sugar methods for creating complex selectors.
"""

import operator
from typing import Any, Callable, Type

import pytest
from bs4 import Tag

from soupsavvy.exceptions import NavigableStringException, NotSoupSelectorException
from soupsavvy.selectors.base import CompositeSoupSelector
from soupsavvy.selectors.combinators import (
    ChildCombinator,
    DescendantCombinator,
    NextSiblingCombinator,
    SelectorList,
    SubsequentSiblingCombinator,
)
from soupsavvy.selectors.components import AndSelector, NotSelector
from tests.soupsavvy.selectors.conftest import (
    MockDivSelector,
    MockLinkSelector,
    MockSelector,
    to_bs,
)


@pytest.mark.selector
class BaseOperatorTest:
    """
    Class with base test cases covering functionality of how standard operators
    should work with SoupSelector objects.
    """

    TYPE: Type[CompositeSoupSelector]
    OPERATOR: Callable[[Any, Any], Any]

    def test_operator_returns_expected_type_with_steps(self):
        """
        Tests if operator returns instance of expected type with operands as steps.
        """
        selector1 = MockSelector()
        selector2 = MockSelector()

        result = self.OPERATOR(selector1, selector2)

        assert isinstance(result, self.TYPE)
        assert result.selectors == [selector1, selector2]

    def test_operator_returns_expected_type_with_updated_tags(self):
        """
        Tests if operator returns instance of expected type with updated tags
        if left operand is of target type of the operator.

        It does not make sense to nest selectors of the same type, so
        the new instance should be created with updated list of selectors.
        """
        selector1 = MockSelector()
        selector2 = MockSelector()
        selector3 = MockSelector()
        combined = self.TYPE(selector1, selector2)  # type: ignore

        result = self.OPERATOR(combined, selector3)

        assert isinstance(result, self.TYPE)
        assert id(result) != id(combined)

        assert result.selectors == [selector1, selector2, selector3]

    def test_operator_raises_exception_if_not_soup_selector(self):
        """
        Tests if operator raises NotSoupSelectorException if right
        operand is not SoupSelector.
        """
        selector = MockSelector()

        with pytest.raises(NotSoupSelectorException):
            self.OPERATOR(selector, "string")


class TestMULOperator(BaseOperatorTest):
    """
    Class for testing MUL operator for SoupSelector interface.
    __mul__ operator applied correctly creates DescendantCombinator instance.

    Example
    -------
    >>> MockSelector() * MockSelector()
    """

    TYPE = SubsequentSiblingCombinator
    OPERATOR = operator.mul


class TestADDOperator(BaseOperatorTest):
    """
    Class for testing ADD operator for SoupSelector interface.
    __add__ operator applied correctly creates NextSiblingCombinator instance.

    Example
    -------
    >>> MockSelector() + MockSelector()
    """

    TYPE = NextSiblingCombinator
    OPERATOR = operator.add


class TestANDOperator(BaseOperatorTest):
    """
    Class for testing bitwise AND operator for SoupSelector interface.
    __and__ operator applied correctly creates AndSelector instance.

    Example
    -------
    >>> MockSelector() & MockSelector()
    """

    TYPE = AndSelector
    OPERATOR = operator.and_


class TestOROperator(BaseOperatorTest):
    """
    Class for testing bitwise OR operator for SoupSelector interface.
    __or__ operator applied correctly creates SelectorList instance.

    Example
    -------
    >>> MockSelector() | MockSelector()
    """

    TYPE = SelectorList
    OPERATOR = operator.or_


class TestGTOperator(BaseOperatorTest):
    """
    Class for testing GT operator for SoupSelector interface.
    __gt__ operator applied correctly creates ChildCombinator instance.

    Example
    -------
    >>> MockSelector() > MockSelector()
    """

    TYPE = ChildCombinator
    OPERATOR = operator.gt


class TestRSHIFTOperator(BaseOperatorTest):
    """
    Class for testing RSHIFT operator for SoupSelector interface.
    __rshift__ operator applied correctly creates DescendantCombinator instance.

    Example
    -------
    >>> MockSelector() >> MockSelector()
    """

    TYPE = DescendantCombinator
    OPERATOR = operator.rshift


@pytest.mark.selector
class TestNOTOperator:
    """
    Class for testing bitwise NOT operator for SoupSelector interface.
    It's a special operator, that is applied on a single selector and returns
    its negation.

    Example
    -------
    >>> ~MockSelector()
    """

    def test_bitwise_not_operator_returns_not_selector(self):
        """
        Tests if bitwise NOT operator (__invert__) returns NotSelector instance
        with operand as single selector.
        """
        selector = MockSelector()
        result = ~selector
        assert isinstance(result, NotSelector)
        assert result.selectors == [selector]

    def test_bitwise_not_operator_on_single_not_selector_returns_selector(self):
        """
        Tests if bitwise NOT operator (__invert__) returns the original tag
        when applied to NotSelector instance with single selector.

        It does not make sense to create NotSelector(NotSelector(...)), even
        though it would result in the same selector, nesting negation is redundant.
        """
        selector = MockSelector()
        combined = NotSelector(selector)
        result = ~combined
        assert result == selector

    def test_bitwise_not_operator_on_multiple_not_selector_returns_selector_list(self):
        """
        Tests if bitwise NOT operator (__invert__) returns the SelectorList
        instance with the same selectors when applied to NotSelector instance
        with multiple selectors.

        If NotSelector matches tag if it doesn't match at least one of the selectors,
        so negation would be to match at least one of the selectors, which is
        how SelectorList works.
        """
        selector1 = MockSelector()
        selector2 = MockSelector()
        combined = NotSelector(selector1, selector2)

        result = ~combined

        assert isinstance(result, SelectorList)
        assert result.selectors == [selector1, selector2]


@pytest.mark.selector
@pytest.mark.edge_case
def test_exception_is_raised_when_navigable_string_is_a_result():
    """
    Tests if NavigableStringException is raised when bs4.find returns NavigableString.
    Child classes of SoupSelector should always always prevent that,
    thus this is a hypothetical case that is covered anyway to ensure that it does
    not break code downstream.
    """
    from bs4 import NavigableString

    class NavigableStringSelector(MockSelector):
        """
        Mock selector that returns NavigableString in find method
        to force NavigableStringException in SoupSelector base class.
        """

        def find_all(self, tag: Tag, recursive: bool = True, limit=None) -> list[Tag]:
            return []

        def _find(self, tag: Tag, recursive: bool = True):
            return NavigableString("Hello World")

    markup = """<div class="widget">Hello World</div>"""
    bs = to_bs(markup)
    tag = NavigableStringSelector()

    with pytest.raises(NavigableStringException):
        tag.find(bs, strict=True)


class TestMultipleSoupSelector:
    """
    Class for testing MultipleSoupSelector interface.
    It's a base class for testing multiple selectors that are combined
    with different operators.
    """

    class MockMultipleSoupSelector(CompositeSoupSelector):
        """Mock class for testing MultipleSoupSelector interface."""

        def __init__(self, *selectors):
            super().__init__(list(selectors))

        def find_all(self, tag: Tag, recursive: bool = True, limit=None) -> list[Tag]:
            return []

    class MockMultipleSoupSelectorNotEqual(MockMultipleSoupSelector):
        """
        Mock class for testing equality of MultipleSoupSelector,
        if right operand is instance of MultipleSoupSelector and have the same
        type as left operand, they are equal.
        """

    @pytest.mark.parametrize(
        argnames="selectors",
        argvalues=[
            # with two equal steps
            (
                MockMultipleSoupSelector(MockLinkSelector(), MockDivSelector()),
                MockMultipleSoupSelector(MockLinkSelector(), MockDivSelector()),
            ),
            # without any steps
            (
                MockMultipleSoupSelector(),
                MockMultipleSoupSelector(),
            ),
            # with one equal step
            (
                MockMultipleSoupSelector(MockDivSelector()),
                MockMultipleSoupSelector(MockDivSelector()),
            ),
        ],
    )
    def test_two_selectors_are_equal(
        self, selectors: tuple[MockSelector, MockSelector]
    ):
        """Tests if two multiple soup selectors are equal."""
        assert (selectors[0] == selectors[1]) is True

    @pytest.mark.parametrize(
        argnames="selectors",
        argvalues=[
            # with equal steps but in different order
            (
                MockMultipleSoupSelector(MockLinkSelector(), MockDivSelector()),
                MockMultipleSoupSelector(MockDivSelector(), MockLinkSelector()),
            ),
            # without one equal step and one step different
            (
                MockMultipleSoupSelector(MockDivSelector(), MockLinkSelector()),
                MockMultipleSoupSelector(MockDivSelector(), MockDivSelector()),
            ),
            # with one different step
            (
                MockMultipleSoupSelector(MockDivSelector()),
                MockMultipleSoupSelector(MockLinkSelector()),
            ),
            # not instance of MultipleSoupSelector
            (
                MockMultipleSoupSelector(MockDivSelector()),
                MockLinkSelector(),
            ),
            # not the same type as left operand
            (
                MockMultipleSoupSelector(MockDivSelector()),
                MockMultipleSoupSelectorNotEqual(MockDivSelector()),
            ),
        ],
    )
    def test_two_selectors_are_not_equal(
        self, selectors: tuple[MockSelector, MockSelector]
    ):
        """Tests if two multiple soup selectors are not equal."""
        assert (selectors[0] == selectors[1]) is False
