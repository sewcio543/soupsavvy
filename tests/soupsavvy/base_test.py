"""
Testing module for testing basic functionality of `soupsavvy` base classes
in `base` module. It contains operations and selector related tests.
"""

import operator
from collections.abc import Callable
from itertools import product
from typing import Any, Type

import pytest

from soupsavvy.base import (
    CompositeSoupSelector,
    OperationSearcherMixin,
    check_operation,
    check_selector,
)
from soupsavvy.exceptions import (
    BreakOperationException,
    FailedOperationExecution,
    NotOperationException,
    NotSoupSelectorException,
)
from soupsavvy.interfaces import IElement, T
from soupsavvy.operations.general import OperationPipeline
from soupsavvy.operations.selection_pipeline import SelectionPipeline
from soupsavvy.selectors.combinators import (
    AncestorCombinator,
    ChildCombinator,
    DescendantCombinator,
    NextSiblingCombinator,
    ParentCombinator,
    SubsequentSiblingCombinator,
)
from soupsavvy.selectors.logical import (
    AndSelector,
    NotSelector,
    SelectorList,
    XORSelector,
)
from tests.soupsavvy.conftest import (
    MockBreakOperation,
    MockClassMenuSelector,
    MockDivSelector,
    MockIntOperation,
    MockLinkSelector,
    MockSelector,
    MockTextOperation,
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


class TestLSHIFTOperator(BaseOperatorTest):
    """
    Class for testing LSHIFT operator for SoupSelector interface.
    __lshift__ operator applied correctly creates AncestorCombinator instance.

    Example
    -------
    >>> MockSelector() << MockSelector()
    """

    TYPE = AncestorCombinator
    OPERATOR = operator.lshift


class TestLTOperator(BaseOperatorTest):
    """
    Class for testing LT operator for SoupSelector interface.
    __lt__ operator applied correctly creates ParentCombinator instance.

    Example
    -------
    >>> MockSelector() < MockSelector()
    """

    TYPE = ParentCombinator
    OPERATOR = operator.lt


class TestXOROperator(BaseOperatorTest):
    """
    Class for testing XOR operator for SoupSelector interface.
    __xor__ operator applied correctly creates ParentCombinator instance.

    Example
    -------
    >>> MockSelector() ^ MockSelector()
    """

    TYPE = XORSelector
    OPERATOR = operator.xor


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
class TestCompositeSoupSelector:
    """
    Class for testing CompositeSoupSelector interface.
    It's a base class for testing multiple selectors that are combined
    with different operators.
    """

    class BaseCompositeSoupSelectorMock(CompositeSoupSelector):
        """Base mock class for testing CompositeSoupSelector interface."""

        def __init__(self, *selectors):
            super().__init__(list(selectors))

        def find_all(self, tag: T, recursive: bool = True, limit=None) -> list[T]:
            return []

    class MockUnordered(BaseCompositeSoupSelectorMock):
        """
        Mock class for testing CompositeSoupSelector interface for cases
        when order of selectors is not relevant in context of results.
        """

        COMMUTATIVE = True

    class MockOrdered(BaseCompositeSoupSelectorMock):
        """
        Mock class for testing CompositeSoupSelector interface for cases
        when order of selectors is relevant in context of results.
        """

        COMMUTATIVE = False

    class MockNotEqual(MockOrdered):
        """
        Mock class for testing equality of CompositeSoupSelector,
        if right operand is instance of CompositeSoupSelector and have the same
        type as left operand, they are equal.
        """

    @pytest.mark.parametrize(
        argnames="selectors",
        argvalues=[
            # ordered with two equal steps
            (
                MockOrdered(MockLinkSelector(), MockDivSelector()),
                MockOrdered(MockLinkSelector(), MockDivSelector()),
            ),
            # ordered without any steps
            (
                MockOrdered(),
                MockOrdered(),
            ),
            # ordered with one equal step
            (
                MockOrdered(MockDivSelector()),
                MockOrdered(MockDivSelector()),
            ),
            # unordered with one equal step
            (
                MockUnordered(MockDivSelector()),
                MockUnordered(MockDivSelector()),
            ),
            # unordered with two equal steps in different order
            (
                MockUnordered(MockDivSelector(), MockLinkSelector()),
                MockUnordered(MockLinkSelector(), MockDivSelector()),
            ),
            # unordered with two equal steps in the same order
            (
                MockUnordered(MockDivSelector(), MockLinkSelector()),
                MockUnordered(MockDivSelector(), MockLinkSelector()),
            ),
            # unordered with three equal steps in different order
            (
                MockUnordered(
                    MockDivSelector(), MockClassMenuSelector(), MockLinkSelector()
                ),
                MockUnordered(
                    MockLinkSelector(), MockDivSelector(), MockClassMenuSelector()
                ),
            ),
            # unordered with more selectors that make intersection - left more
            (
                MockUnordered(
                    MockDivSelector(),
                    MockClassMenuSelector(),
                    MockDivSelector(),
                    MockClassMenuSelector(),
                ),
                MockUnordered(MockDivSelector(), MockClassMenuSelector()),
            ),
            # unordered with more selectors that make intersection - right more
            (
                MockUnordered(MockDivSelector(), MockClassMenuSelector()),
                MockUnordered(
                    MockDivSelector(),
                    MockClassMenuSelector(),
                    MockDivSelector(),
                    MockClassMenuSelector(),
                ),
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
            # ordered with equal steps but in different order
            (
                MockOrdered(MockLinkSelector(), MockDivSelector()),
                MockOrdered(MockDivSelector(), MockLinkSelector()),
            ),
            # ordered with one equal step and one step different
            (
                MockOrdered(MockDivSelector(), MockLinkSelector()),
                MockOrdered(MockDivSelector(), MockDivSelector()),
            ),
            # ordered with different number of steps
            (
                MockOrdered(
                    MockClassMenuSelector(), MockLinkSelector(), MockDivSelector()
                ),
                MockOrdered(MockClassMenuSelector(), MockLinkSelector()),
            ),
            # ordered with one different step
            (
                MockOrdered(MockDivSelector()),
                MockOrdered(MockLinkSelector()),
            ),
            # ordered not instance of CompositeSoupSelector
            (
                MockOrdered(MockDivSelector()),
                MockLinkSelector(),
            ),
            # ordered not the same type as left operand
            (
                MockOrdered(MockDivSelector()),
                MockNotEqual(MockDivSelector()),
            ),
            # unordered with one different step
            (
                MockUnordered(MockDivSelector()),
                MockNotEqual(MockLinkSelector()),
            ),
            # ordered with different number of steps
            (
                MockUnordered(
                    MockClassMenuSelector(), MockLinkSelector(), MockDivSelector()
                ),
                MockUnordered(MockClassMenuSelector(), MockLinkSelector()),
            ),
            # unordered with one equal step and one different step
            (
                MockUnordered(MockDivSelector(), MockLinkSelector()),
                MockUnordered(MockDivSelector(), MockDivSelector()),
            ),
        ],
    )
    def test_two_selectors_are_not_equal(
        self, selectors: tuple[MockSelector, MockSelector]
    ):
        """Tests if two multiple soup selectors are not equal."""
        assert (selectors[0] == selectors[1]) is False


@pytest.mark.selector
class TestCheckSelector:
    """
    Class for testing check_selector function.
    Function is used to ensure that object is instance of SoupSelector.
    """

    def test_passes_check_and_returns_the_same_object(self):
        """
        Tests if check_selector returns the same object
        if it is instance of SoupSelector.
        """
        selector = MockSelector()
        result = check_selector(selector)
        assert result is selector

    @pytest.mark.parametrize(
        argnames="param",
        argvalues=["selector", str.lower, MockTextOperation()],
        ids=["str", "function", "operation"],
    )
    def test_raises_exception_when_not_selector(self, param):
        """
        Tests if check_selector raises NotSoupSelectorException if object is not
        instance of SoupSelector.
        """
        with pytest.raises(NotSoupSelectorException):
            check_selector("selector")

    def test_raises_exception_with_custom_message_when_specified(self):
        """
        Tests if check_selector raises NotSoupSelectorException with custom message
        if object is not instance of SoupSelector and message is specified.
        """
        message = "Custom message"

        with pytest.raises(NotSoupSelectorException, match=message):
            check_selector("selector", message=message)


@pytest.mark.selector
def test_or_return_selection_pipeline_if_operation_passed():
    """
    Tests if using or operator with on SoupSelector and BaseOperation
    returns SelectionPipeline instance with correct selector and operation.
    """
    selector = MockSelector()
    operation = MockTextOperation()

    result = selector | operation

    assert isinstance(result, SelectionPipeline)
    assert result.selector is selector
    assert result.operation is operation


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

    def test_break_exception_is_propagated_in_execute(self):
        """
        Tests if BreakOperationException is propagated in execute method.
        If it was raised during _execute method, it should be propagated.
        """
        operation = MockBreakOperation(MockIntOperation())

        with pytest.raises(BreakOperationException) as info:
            operation.execute("10")
            assert info.value.result == 10

    def test_execute_raises_failed_operation_if_error_in_operation(self):
        """
        Tests if execute method raises FailedOperationExecution if operation failed
        and raised any error during execution, that inherits from Exception
        and is not BreakOperationException, which takes precedence.
        """
        operation = MockIntOperation()

        with pytest.raises(FailedOperationExecution):
            operation.execute("abc")


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

    def _execute(self, arg: IElement):
        if not isinstance(arg, IElement):
            raise TypeError

        return arg.name

    def __eq__(self, x: Any) -> bool:
        return isinstance(x, MockNameOperation)


div = to_bs("""<div></div>""").find_all("div")[0]
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
