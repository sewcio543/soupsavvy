"""
Testing module for testing basic functionality of SelectableSoup interface.
Tests cover implementation of dunder method that are shared among all soupsavvy
selectors. There are syntactical sugar methods for creating complex selectors.
"""

import operator
from typing import Any, Callable, Type

import pytest

from soupsavvy.tags.base import IterableSoup
from soupsavvy.tags.combinators import (
    ChildCombinator,
    DescendantCombinator,
    NextSiblingCombinator,
    SelectorList,
    SubsequentSiblingCombinator,
)
from soupsavvy.tags.components import AndSelector, NotSelector
from soupsavvy.tags.exceptions import NotSelectableSoupException
from tests.soupsavvy.tags.conftest import MockSelector


@pytest.mark.soup
class BaseOperatorTest:
    """
    Class with base test cases covering functionality of how standard operators
    should work with SelectableSoup objects.
    """

    TYPE: Type[IterableSoup]
    OPERATOR: Callable[[Any, Any], Any]

    def test_operator_returns_expected_type_with_steps(self):
        """
        Tests if operator returns instance of expected type with operands as steps.
        """
        selector1 = MockSelector()
        selector2 = MockSelector()

        result = self.OPERATOR(selector1, selector2)

        assert isinstance(result, self.TYPE)
        assert result.steps == [selector1, selector2]

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

        assert result.steps == [selector1, selector2, selector3]

    def test_operator_raises_exception_if_not_selectable_soup(self):
        """
        Tests if operator raises NotSelectableSoupException if right
        operand is not SelectableSoup.
        """
        selector = MockSelector()

        with pytest.raises(NotSelectableSoupException):
            self.OPERATOR(selector, "string")


class TestMULOperator(BaseOperatorTest):
    """
    Class for testing MUL operator for SelectableSoup interface.
    __mul__ operator applied correctly creates DescendantCombinator instance.

    Example
    -------
    >>> MockSelector() * MockSelector()
    """

    TYPE = SubsequentSiblingCombinator
    OPERATOR = operator.mul


class TestADDOperator(BaseOperatorTest):
    """
    Class for testing ADD operator for SelectableSoup interface.
    __add__ operator applied correctly creates NextSiblingCombinator instance.

    Example
    -------
    >>> MockSelector() + MockSelector()
    """

    TYPE = NextSiblingCombinator
    OPERATOR = operator.add


class TestANDOperator(BaseOperatorTest):
    """
    Class for testing bitwise AND operator for SelectableSoup interface.
    __and__ operator applied correctly creates AndSelector instance.

    Example
    -------
    >>> MockSelector() & MockSelector()
    """

    TYPE = AndSelector
    OPERATOR = operator.and_


class TestOROperator(BaseOperatorTest):
    """
    Class for testing bitwise OR operator for SelectableSoup interface.
    __or__ operator applied correctly creates SelectorList instance.

    Example
    -------
    >>> MockSelector() | MockSelector()
    """

    TYPE = SelectorList
    OPERATOR = operator.or_


class TestGTOperator(BaseOperatorTest):
    """
    Class for testing GT operator for SelectableSoup interface.
    __gt__ operator applied correctly creates ChildCombinator instance.

    Example
    -------
    >>> MockSelector() > MockSelector()
    """

    TYPE = ChildCombinator
    OPERATOR = operator.gt


class TestRSHIFTOperator(BaseOperatorTest):
    """
    Class for testing RSHIFT operator for SelectableSoup interface.
    __rshift__ operator applied correctly creates DescendantCombinator instance.

    Example
    -------
    >>> MockSelector() >> MockSelector()
    """

    TYPE = DescendantCombinator
    OPERATOR = operator.rshift


@pytest.mark.soup
class TestNOTOperator:
    """
    Class for testing bitwise NOT operator for SelectableSoup interface.
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
        assert result.steps == [selector]

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
        assert result.steps == [selector1, selector2]
