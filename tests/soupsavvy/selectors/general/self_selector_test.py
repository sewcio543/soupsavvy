"""Testing module for SelfSelector class."""

from itertools import product

import pytest

from soupsavvy.selectors.general import SelfSelector
from tests.soupsavvy.conftest import MockLinkSelector, ToElement, strip

SELECTOR = SelfSelector()
TEXT = """
    <div href="github"><a>Hello</a></div>
    <a class="widget">1</a>
"""
EXPECTED = strip("""<div href="github"><a>Hello</a></div>""")


@pytest.mark.selector
class TestSelfSelector:
    """Class for SelfSelector unit test suite."""

    @pytest.mark.parametrize(
        argnames="strict, recursive",
        argvalues=list(product([True, False], [True, False])),
    )
    def test_find_returns_first_tag_itself(
        self, to_element: ToElement, strict: bool, recursive: bool
    ):
        """
        Tests if find method always returns element itself irrespective of
        any other parameters, testing for all strict and recursive values.
        """
        BS = to_element(TEXT).find_all("div")[0]
        result = SELECTOR.find(BS, strict=strict, recursive=recursive)
        assert strip(str(result)) == EXPECTED

    @pytest.mark.parametrize(
        argnames="limit, recursive",
        argvalues=list(product([None, 2], [True, False])),
    )
    def test_find_all_returns_all_matching_elements(
        self, to_element: ToElement, limit, recursive: bool
    ):
        """
        Tests if find_all method always returns a single element list with
        element itself irrespective of any other parameters,
        testing for all recursive values with and without limit.
        """
        BS = to_element(TEXT).find_all("div")[0]
        result = SELECTOR.find_all(BS, limit=limit, recursive=recursive)
        assert list(map(lambda x: strip(str(x)), result)) == [EXPECTED]

    @pytest.mark.parametrize(
        argnames="selectors",
        argvalues=[
            # the same type
            (SelfSelector(), SelfSelector()),
        ],
    )
    def test_two_tag_selectors_are_equal(self, selectors: tuple):
        """Tests if selector is equal to SelfSelector."""
        assert (selectors[0] == selectors[1]) is True

    @pytest.mark.parametrize(
        argnames="selectors",
        argvalues=[
            # different types
            (SelfSelector(), MockLinkSelector()),
        ],
    )
    def test_two_tag_selectors_are_not_equal(self, selectors: tuple):
        """Tests if selector is not equal to SelfSelector."""
        assert (selectors[0] == selectors[1]) is False
