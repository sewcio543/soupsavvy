"""
Module with unit tests that cover soupsavvy.operators module functionality.
It contains functions used to combine selectors and create composite ones.
"""

import pytest

from soupsavvy import operators
from soupsavvy.selectors.logical import (
    AndSelector,
    NotSelector,
    SelectorList,
    XORSelector,
)
from soupsavvy.selectors.relative import HasSelector
from tests.soupsavvy.conftest import MockSelector


@pytest.mark.css
@pytest.mark.selector
class TestOperators:
    """Class with unit tests suite for operators module."""

    @pytest.mark.parametrize(argnames="count", argvalues=[2, 3], ids=["two", "three"])
    def test_is_returns_selector_list_with_specified_steps(self, count: int):
        """Tests if is_ function returns SelectorList with specified steps."""
        selectors = [MockSelector() for _ in range(count)]
        result = operators.is_(*selectors)
        assert isinstance(result, SelectorList)
        assert result.selectors == selectors

    @pytest.mark.parametrize(argnames="count", argvalues=[2, 3], ids=["two", "three"])
    def test_where_returns_selector_list_with_specified_steps(self, count: int):
        """
        Tests if where function returns SelectorList with specified steps.
        It is an alias for is_ function.
        """
        selectors = [MockSelector() for _ in range(count)]
        result = operators.where(*selectors)
        assert isinstance(result, SelectorList)
        assert result.selectors == selectors

    @pytest.mark.parametrize(argnames="count", argvalues=[2, 3], ids=["two", "three"])
    def test_or_returns_selector_list_with_specified_steps(self, count: int):
        """
        Tests if or_ function returns SelectorList with specified steps.
        It is an alias for is_ function.
        """
        selectors = [MockSelector() for _ in range(count)]
        result = operators.or_(*selectors)
        assert isinstance(result, SelectorList)
        assert result.selectors == selectors

    @pytest.mark.parametrize(argnames="count", argvalues=[1, 3], ids=["one", "three"])
    def test_not_returns_not_selector_with_specified_steps(self, count: int):
        """
        Tests if not_ function returns NotSelector with specified steps.
        On the contrary to other api functions, it can take only one selector
        as an argument.
        """
        selectors = [MockSelector() for _ in range(count)]
        result = operators.not_(*selectors)
        assert isinstance(result, NotSelector)
        assert result.selectors == selectors

    @pytest.mark.parametrize(argnames="count", argvalues=[2, 3], ids=["two", "three"])
    def test_and_returns_and_selector_with_specified_steps(self, count: int):
        """Tests if and_ function returns AndSelector with specified steps."""
        selectors = [MockSelector() for _ in range(count)]
        result = operators.and_(*selectors)
        assert isinstance(result, AndSelector)
        assert result.selectors == selectors

    @pytest.mark.parametrize(argnames="count", argvalues=[2, 3], ids=["one", "three"])
    def test_has_returns_has_selector_with_specified_steps(self, count: int):
        """Tests if has function returns HasSelector with specified steps."""
        selectors = [MockSelector() for _ in range(count)]
        result = operators.has(*selectors)
        assert isinstance(result, HasSelector)
        assert result.selectors == selectors

    @pytest.mark.parametrize(argnames="count", argvalues=[2, 3], ids=["two", "three"])
    def test_xor_returns_xor_selector_with_specified_steps(self, count: int):
        """Tests if xor function returns XORSelector with specified steps."""
        selectors = [MockSelector() for _ in range(count)]
        result = operators.xor(*selectors)
        assert isinstance(result, XORSelector)
        assert result.selectors == selectors
