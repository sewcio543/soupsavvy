"""
Module with unit tests for relative module, that contains relative combinators components.
They have a define recursion behavior when finding tags in the soup, so this parameter
should behave in the same way whether it is set to True or False, hence parametrization
and asserting the same results for both cases.
"""

from abc import ABC, abstractmethod
from typing import Type

import pytest
from bs4 import Tag

from soupsavvy.exceptions import NotSoupSelectorException, TagNotFoundException
from soupsavvy.tags.relative import (
    Anchor,
    RelativeChild,
    RelativeDescendant,
    RelativeNextSibling,
    RelativeSelector,
    RelativeSubsequentSibling,
)
from tests.soupsavvy.tags.conftest import (
    MockDivSelector,
    MockLinkSelector,
    find_body_element,
    strip,
    to_bs,
)


@pytest.mark.soup
@pytest.mark.combinator
class BaseRelativeCombinatorTest(ABC):
    """
    Base suite of tests for RelativeSelector classes.
    Contains base cases that should be tested under assumption of input tag,
    that have or do not have matching elements.
    """

    # base type of RelativeSelector class used in class for testing
    base: Type[RelativeSelector]

    @pytest.fixture(scope="class")
    def selector(self) -> RelativeSelector:
        """
        Fixture that returns instance of RelativeSelector for testing purposes.
        Initializes 'base' (class attribute) class with MockLinkSelector instance.
        """
        return self.base(MockLinkSelector())

    @property
    @abstractmethod
    def match(self) -> Tag:
        """
        Returns the bs4.Tag that is passed into find methods as an anchor element.
        It should have 3 matching link elements for base selector of the class.

        Calling find_all method on this tag should return:

        Example
        -------
        >>> selector.find_all(self.match)
        [<a>1</a>, <a>2</a>, <a>3</a>]

        Calling find method on this tag should return:

        Example
        -------
        >>> selector.find(self.match)
        <a>1</a>
        """
        raise NotImplementedError(
            f"Property 'match' not implemented in {self.__class__.__name__}"
        )

    @property
    @abstractmethod
    def no_match(self) -> Tag:
        """
        Returns the bs4.Tag that is passed into find methods as an anchor element.
        It should have no matching link elements for base selector of the class.

        Calling find_all method on this tag should return:

        Example
        -------
        >>> selector.find_all(self.match)
        []

        Calling find method on this tag should return:

        Example
        -------
        >>> selector.find(self.no_match)
        None
        >>> selector.find(self.no_match, strict=True)
        TagNotFoundException
        """
        raise NotImplementedError(
            f"Property 'no_match' not implemented in {self.__class__.__name__}"
        )

    def test_raises_exception_when_invalid_input(self):
        """
        Tests if selector raises NotSoupSelectorException when invalid input is provided
        on object initialization. It only accepts SoupSelector instances.
        """
        with pytest.raises(NotSoupSelectorException):
            self.base("p")  # type: ignore

    @pytest.mark.parametrize(
        argnames="recursive",
        argvalues=[True, False],
        ids=["recursive", "not_recursive"],
    )
    def test_find_returns_first_matching_tag(
        self, selector: RelativeChild, recursive: bool
    ):
        """
        Tests if find method returns the first tag that matches selector relative to
        the anchor (tag passed as parameter to find method) element.
        """
        result = selector.find(self.match, recursive=recursive)
        assert strip(str(result)) == strip("""<a>1</a>""")

    @pytest.mark.parametrize(
        argnames="recursive",
        argvalues=[True, False],
        ids=["recursive", "not_recursive"],
    )
    def test_find_raises_exception_when_no_tags_match_in_strict_mode(
        self, selector: RelativeChild, recursive: bool
    ):
        """
        Tests if find method raises TagNotFoundException when no elements match the selector
        relative to the anchor element and strict is True.
        """

        with pytest.raises(TagNotFoundException):
            selector.find(self.no_match, strict=True, recursive=recursive)

    @pytest.mark.parametrize(
        argnames="recursive",
        argvalues=[True, False],
        ids=["recursive", "not_recursive"],
    )
    def test_find_returns_none_if_no_tags_match_in_not_strict_mode(
        self, selector: RelativeChild, recursive: bool
    ):
        """
        Tests if find method raises TagNotFoundException when no elements match the selector
        relative to the anchor element and strict is False.
        """
        result = selector.find(self.no_match, recursive=recursive)
        assert result is None

    @pytest.mark.parametrize(
        argnames="recursive",
        argvalues=[True, False],
        ids=["recursive", "not_recursive"],
    )
    def test_finds_all_tags_matching_selectors(
        self, selector: RelativeChild, recursive: bool
    ):
        """
        Tests if find_all method returns all elements that match the selector
        relative to the anchor element.
        """
        result = selector.find_all(self.match, recursive=recursive)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a>1</a>"""),
            strip("""<a>2</a>"""),
            strip("""<a>3</a>"""),
        ]

    @pytest.mark.parametrize(
        argnames="recursive",
        argvalues=[True, False],
        ids=["recursive", "not_recursive"],
    )
    def test_find_all_returns_empty_list_if_no_tag_matches(
        self, selector: RelativeChild, recursive: bool
    ):
        """
        Tests if find_all method returns an empty list when no tag is found
        that matches selector relative to the anchor element.
        """
        result = selector.find_all(self.no_match, recursive=recursive)
        assert result == []

    @pytest.mark.parametrize(
        argnames="recursive",
        argvalues=[True, False],
        ids=["recursive", "not_recursive"],
    )
    def test_find_all_returns_only_x_elements_when_limit_is_set(
        self, selector: RelativeChild, recursive: bool
    ):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        results = selector.find_all(self.match, limit=2, recursive=recursive)
        assert list(map(lambda x: strip(str(x)), results)) == [
            strip("""<a>1</a>"""),
            strip("""<a>2</a>"""),
        ]


@pytest.mark.soup
class TestRelativeChild(BaseRelativeCombinatorTest):
    """Class for RelativeChild unit test suite."""

    base = RelativeChild

    @property
    def match(self) -> Tag:
        text = """
            <div class="link">
                <a>Not child</a>
            </div>
            <a>1</a>
            <span>
                <a>Not a child</a>
            </span>
            <a>2</a>
            <a>3</a>
        """
        return find_body_element(to_bs(text))

    @property
    def no_match(self) -> Tag:
        text = """
            <div class="link">
                <a>Not child</a>
            </div>
            <span></span>
        """
        return find_body_element(to_bs(text))


class TestRelativeDescendant(BaseRelativeCombinatorTest):
    """Class for RelativeDescendant unit test suite."""

    base = RelativeDescendant

    @property
    def match(self) -> Tag:
        text = """
            <div class="link">
                <a>1</a>
            </div>
            <span>
                <a>2</a>
            </span>
            <a>3</a>
        """
        return find_body_element(to_bs(text))

    @property
    def no_match(self) -> Tag:
        text = """
            <div class="link">
                <p>Not a link</p>
            </div>
            <span></span>
        """
        return find_body_element(to_bs(text))


class TestRelativeSubsequentSibling(BaseRelativeCombinatorTest):
    """Class for RelativeSubsequentSibling unit test suite."""

    base = RelativeSubsequentSibling

    @property
    def match(self) -> Tag:
        text = """
            <a>Not next sibling</a>
            <div class="anchor"></div>
            <a>1</a>
            <span>
                <a>Not a sibling</a>
            </span>
            <a>2</a>
            <p>Not a link</p>
            <a>3</a>
        """
        return to_bs(text).div  # type: ignore

    @property
    def no_match(self) -> Tag:
        text = """
            <a>Not next sibling</a>
            <div class="anchor"></div>
            <span>
                <a>Not a sibling</a>
            </span>
            <p>Not a link</p>
        """
        return to_bs(text).div  # type: ignore


class TestRelativeNextSibling(BaseRelativeCombinatorTest):
    """
    Class for RelativeNextSibling unit test suite.
    Some of the test methods had to be overwritten, because of the different behavior
    of RelativeNextSibling in comparison to other RelativeSelector classes.

    Its find_all method should return at most one element in the list.
    """

    base = RelativeNextSibling

    @property
    def match(self) -> Tag:
        text = """
            <a>Not next sibling</a>
            <div class="anchor"></div>
            <a>1</a>
            <span>
                <a>Not a sibling</a>
            </span>
            <a>2</a>
            <p>Not a link</p>
            <a>3</a>
        """
        return to_bs(text).div  # type: ignore

    @property
    def no_match(self) -> Tag:
        text = """
            <a>Not next sibling</a>
            <div class="anchor"></div>
            <span>
                <a>Not a sibling</a>
            </span>
            <p>Not a link</p>
        """
        return to_bs(text).div  # type: ignore

    @pytest.mark.parametrize(
        argnames="recursive",
        argvalues=[True, False],
        ids=["recursive", "not_recursive"],
    )
    def test_finds_all_tags_matching_selectors(
        self, selector: RelativeChild, recursive: bool
    ):
        """
        Tests if find_all method returns all children of passed tag that match the selector,
        in case of RelativeNextSibling it should return only one element (next sibling).
        """
        result = selector.find_all(self.match, recursive=recursive)
        assert list(map(lambda x: strip(str(x)), result)) == [strip("""<a>1</a>""")]

    @pytest.mark.parametrize(
        argnames="recursive",
        argvalues=[True, False],
        ids=["recursive", "not_recursive"],
    )
    def test_find_all_returns_only_x_elements_when_limit_is_set(
        self, selector: RelativeChild, recursive: bool
    ):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned,
        but in case of RelativeNextSibling it should return only one element (next sibling).
        """
        results = selector.find_all(self.match, limit=2, recursive=recursive)
        assert list(map(lambda x: strip(str(x)), results)) == [strip("""<a>1</a>""")]


class TestAnchor:
    """
    Test suite for Anchor object which is an instance of _Anchor class and it's supposed
    to be used as a singleton. It's used as a sugar syntax for creating RelativeSelector
    objects for different combinators.

    It's sole responsibility is to implement dunder methods for creating RelativeSelector
    that follow those implemented in SoupSelector interface for combinator selectors:

    * gt operator for RelativeChild
    * rshift operator for RelativeDescendant
    * add operator for RelativeNextSibling
    * mul operator for RelativeSubsequentSibling
    """

    def test_anchoring_with_gt_operator_returns_relative_child(self):
        """
        Tests if using gt operator on Anchor instance returns RelativeChild instance
        with proper selector attribute.
        """
        base = MockLinkSelector()
        result = Anchor > base
        assert isinstance(result, RelativeChild)
        assert result.selector == base

    def test_anchoring_with_rshift_operator_returns_relative_descendant(self):
        """
        Tests if using rshift operator on Anchor instance returns RelativeDescendant instance
        with proper selector attribute.
        """
        base = MockLinkSelector()
        result = Anchor >> base
        assert isinstance(result, RelativeDescendant)
        assert result.selector == base

    def test_anchoring_with_add_operator_returns_relative_next_sibling(self):
        """
        Tests if using add operator on Anchor instance returns RelativeNextSibling instance
        with proper selector attribute.
        """
        base = MockLinkSelector()
        result = Anchor + base
        assert isinstance(result, RelativeNextSibling)
        assert result.selector == base

    def test_anchoring_with_mul_operator_returns_relative_subsequent_sibling(self):
        """
        Tests if using mul operator on Anchor instance returns
        RelativeSubsequentSibling instance with proper selector attribute.
        """
        base = MockLinkSelector()
        result = Anchor * base
        assert isinstance(result, RelativeSubsequentSibling)
        assert result.selector == base


class TestRelativeSelectorEquality:
    """
    Class for testing RelativeSelector base class __eq__ method.
    """

    class MockRelativeSelector(RelativeSelector):
        """
        Mock class for testing equality of RelativeSelector,
        if right operand is instance of RelativeSelector and has the same
        selector, they are equal.
        """

        def find_all(self, tag: Tag, recursive: bool = True, limit=None) -> list[Tag]:
            return []

    class MockRelativeSelectorNotEqual(RelativeSelector):
        """
        Mock class for testing equality of RelativeSelector,
        if right operand is instance of RelativeSelector but is of the
        different type, they are not equal.
        """

        def find_all(self, tag: Tag, recursive: bool = True, limit=None) -> list[Tag]:
            return []

    @pytest.mark.parametrize(
        argnames="selectors",
        argvalues=[
            # the same subclass of RelativeSelector and the same selector
            (
                MockRelativeSelector(MockLinkSelector()),
                MockRelativeSelector(MockLinkSelector()),
            ),
        ],
    )
    def test_two_selectors_are_equal(
        self, selectors: tuple[RelativeSelector, RelativeSelector]
    ):
        """Tests if two multiple soup selectors are equal."""
        assert (selectors[0] == selectors[1]) is True

    @pytest.mark.parametrize(
        argnames="selectors",
        argvalues=[
            # the same subclass of RelativeSelector but different selector
            (
                MockRelativeSelector(MockLinkSelector()),
                MockRelativeSelector(MockDivSelector()),
            ),
            # not instances of RelativeSelector
            (
                MockRelativeSelector(MockLinkSelector()),
                MockLinkSelector(),
            ),
            # the same selector but different subclass of RelativeSelector
            (
                MockRelativeSelector(MockLinkSelector()),
                MockRelativeSelectorNotEqual(MockLinkSelector()),
            ),
        ],
    )
    def test_two_selectors_are_not_equal(
        self, selectors: tuple[RelativeSelector, RelativeSelector]
    ):
        """Tests if two multiple soup selectors are not equal."""
        assert (selectors[0] == selectors[1]) is False
