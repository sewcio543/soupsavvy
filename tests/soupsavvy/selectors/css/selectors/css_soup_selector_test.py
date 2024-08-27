"""Module for testing CSSSoupSelector base class."""

import pytest
from bs4 import Tag

from soupsavvy.selectors.css.selectors import CSSSoupSelector
from tests.soupsavvy.selectors.conftest import MockSelector


@pytest.mark.selector
@pytest.mark.css
class TestCSSSoupSelectorEquality:
    """
    Class for testing CSSSoupSelector base class __eq__ method.
    """

    class MockCSSSoupSelector(CSSSoupSelector):
        """
        Mock class for testing equality of CSSSoupSelector,
        if right operand needs to be instance of CSSSoupSelector and selector
        property must be equal.
        """

        def __init__(self, selector: str):
            self._selector = selector

        @property
        def css(self) -> str:
            return self._selector

    class MockCSSSoupSelectorEqual(CSSSoupSelector):
        """
        Mock class for testing equality of CSSSoupSelector,
        if right and left operands are instances of CSSSoupSelector,
        but they are of different type, when their property selector is equal,
        two objects are equal.
        """

        def __init__(self, selector: str):
            self._selector = selector

        @property
        def css(self) -> str:
            return self._selector

    class MockNotCSSSoupSelector(MockSelector):
        """
        Mock class for testing equality of CSSSoupSelector,
        if right operand has selector property that is equal to selector property
        of left operand, but is not instance of CSSSoupSelector,
        two objects are not equal.
        """

        def __init__(self, selector: str):
            self._selector = selector

        @property
        def selector(self) -> str:
            return self._selector

        def find_all(self, tag: Tag, recursive: bool = True, limit=None) -> list[Tag]:
            return []

    @pytest.mark.parametrize(
        argnames="selectors",
        argvalues=[
            # same selectors
            (
                MockCSSSoupSelector("div"),
                MockCSSSoupSelector("div"),
            ),
            # both instances of CSSSoupSelector, but different types with equal selector
            (
                MockCSSSoupSelector("div"),
                MockCSSSoupSelectorEqual("div"),
            ),
        ],
    )
    def test_two_selectors_are_equal(
        self, selectors: tuple[CSSSoupSelector, CSSSoupSelector]
    ):
        """Tests if two multiple soup selectors are equal."""
        assert (selectors[0] == selectors[1]) is True

    @pytest.mark.parametrize(
        argnames="selectors",
        argvalues=[
            # different selectors
            (
                MockCSSSoupSelector("div"),
                MockCSSSoupSelector("span"),
            ),
            # not instances of CSSSoupSelector
            (
                MockCSSSoupSelector("div"),
                MockNotCSSSoupSelector("div"),
            ),
            # both instances of CSSSoupSelector, but different selectors
            (
                MockCSSSoupSelector("div"),
                MockCSSSoupSelectorEqual("span"),
            ),
        ],
    )
    def test_two_selectors_are_not_equal(
        self, selectors: tuple[CSSSoupSelector, CSSSoupSelector]
    ):
        """Tests if two multiple soup selectors are not equal."""
        assert (selectors[0] == selectors[1]) is False
