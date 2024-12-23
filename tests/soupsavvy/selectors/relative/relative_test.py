"""
Module with unit tests for relative module, that contains relative combinators components.
They have a define recursion behavior when finding tags in the soup, so this parameter
should behave in the same way whether it is set to True or False, hence parametrization
and asserting the same result for both cases.
"""

from abc import ABC
from typing import Type

import pytest

from soupsavvy.exceptions import NotSoupSelectorException, TagNotFoundException
from soupsavvy.interfaces import IElement
from soupsavvy.selectors.relative import (
    Anchor,
    RelativeAncestor,
    RelativeChild,
    RelativeDescendant,
    RelativeNextSibling,
    RelativeParent,
    RelativeSelector,
    RelativeSubsequentSibling,
)
from tests.soupsavvy.conftest import MockDivSelector, MockLinkSelector, ToElement, strip


@pytest.mark.selector
class BaseRelativeCombinatorTest(ABC):
    """
    Base suite of tests for RelativeSelector classes.
    Contains base cases that should be tested under assumption of input element,
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

    @pytest.fixture
    def match(self, to_element: ToElement) -> IElement:
        """
        Returns `IElement` that is passed into find methods as an anchor element.
        It should have 3 matching link elements for base selector of the class.

        Calling find_all method on this element should return:

        Example
        -------
        >>> selector.find_all(self.match)
        [<a>1</a>, <a>2</a>, <a>3</a>]

        Calling find method on this element should return:

        Example
        -------
        >>> selector.find(self.match)
        <a>1</a>
        """
        raise NotImplementedError(
            f"Property 'match' not implemented in {self.__class__.__name__}"
        )

    @pytest.fixture
    def no_match(self, to_element: ToElement) -> IElement:
        """
        Returns `IElement` that is passed into find methods as an anchor element.
        It should have no matching link elements for base selector of the class.

        Calling find_all method on this element should return:

        Example
        -------
        >>> selector.find_all(self.match)
        []

        Calling find method on this element should return:

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
    def test_find_returns_first_matching_element(
        self, selector: RelativeChild, recursive: bool, match: IElement
    ):
        """
        Tests if find method returns the first element,
        that matches selector relative to the anchor
        (element passed as parameter to find method) element.
        """
        result = selector.find(match, recursive=recursive)
        assert strip(str(result)) == strip("""<a>1</a>""")

    @pytest.mark.parametrize(
        argnames="recursive",
        argvalues=[True, False],
        ids=["recursive", "not_recursive"],
    )
    def test_find_raises_exception_when_no_element_match_in_strict_mode(
        self, selector: RelativeChild, recursive: bool, no_match: IElement
    ):
        """
        Tests if find method raises TagNotFoundException when no elements match the selector
        relative to the anchor element and strict is True.
        """

        with pytest.raises(TagNotFoundException):
            selector.find(no_match, strict=True, recursive=recursive)

    @pytest.mark.parametrize(
        argnames="recursive",
        argvalues=[True, False],
        ids=["recursive", "not_recursive"],
    )
    def test_find_returns_none_if_no_elements_match_in_not_strict_mode(
        self, selector: RelativeChild, recursive: bool, no_match: IElement
    ):
        """
        Tests if find method raises TagNotFoundException when no elements match the selector
        relative to the anchor element and strict is False.
        """
        result = selector.find(no_match, recursive=recursive)
        assert result is None

    @pytest.mark.parametrize(
        argnames="recursive",
        argvalues=[True, False],
        ids=["recursive", "not_recursive"],
    )
    def test_finds_all_elements_matching_selectors(
        self, selector: RelativeChild, recursive: bool, match: IElement
    ):
        """
        Tests if find_all method returns all elements that match the selector
        relative to the anchor element.
        """
        result = selector.find_all(match, recursive=recursive)
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
    def test_find_all_returns_empty_list_if_no_element_matches(
        self, selector: RelativeChild, recursive: bool, no_match: IElement
    ):
        """
        Tests if find_all method returns an empty list when no element is found
        that matches selector relative to the anchor element.
        """
        result = selector.find_all(no_match, recursive=recursive)
        assert result == []

    @pytest.mark.parametrize(
        argnames="recursive",
        argvalues=[True, False],
        ids=["recursive", "not_recursive"],
    )
    def test_find_all_returns_only_x_elements_when_limit_is_set(
        self, selector: RelativeChild, recursive: bool, match: IElement
    ):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        result = selector.find_all(match, limit=2, recursive=recursive)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a>1</a>"""),
            strip("""<a>2</a>"""),
        ]


class TestRelativeChild(BaseRelativeCombinatorTest):
    """Class for RelativeChild unit test suite."""

    base = RelativeChild

    @pytest.fixture
    def match(self, to_element: ToElement) -> IElement:
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
        return to_element(text)

    @pytest.fixture
    def no_match(self, to_element: ToElement) -> IElement:
        text = """
            <div class="link">
                <a>Not child</a>
            </div>
            <span></span>
        """
        return to_element(text)


class TestRelativeDescendant(BaseRelativeCombinatorTest):
    """Class for RelativeDescendant unit test suite."""

    base = RelativeDescendant

    @pytest.fixture
    def match(self, to_element: ToElement) -> IElement:
        text = """
            <div class="link">
                <a>1</a>
            </div>
            <span>
                <a>2</a>
            </span>
            <a>3</a>
        """
        return to_element(text)

    @pytest.fixture
    def no_match(self, to_element: ToElement) -> IElement:
        text = """
            <div class="link">
                <p>Not a link</p>
            </div>
            <span></span>
        """
        return to_element(text)


class TestRelativeSubsequentSibling(BaseRelativeCombinatorTest):
    """Class for RelativeSubsequentSibling unit test suite."""

    base = RelativeSubsequentSibling

    @pytest.fixture
    def match(self, to_element: ToElement) -> IElement:
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
        return to_element(text).find_all("div")[0]

    @pytest.fixture
    def no_match(self, to_element: ToElement) -> IElement:
        text = """
            <a>Not next sibling</a>
            <div class="anchor"></div>
            <span>
                <a>Not a sibling</a>
            </span>
            <p>Not a link</p>
        """
        return to_element(text).find_all("div")[0]

    def test_returns_none_or_empty_list_if_element_is_root(
        self, to_element: ToElement, selector: RelativeSubsequentSibling
    ):
        """
        Tests if find methods return None or empty list if element is root element,
        which means it does not have any siblings.
        """
        text = """
            <a>Hello</a>
            <div>World</div>
        """
        root = to_element(text).find_ancestors()[-1]

        findall_result = selector.find_all(root)
        assert findall_result == []

        find_result = selector.find(root)
        assert find_result is None


class TestRelativeNextSibling(BaseRelativeCombinatorTest):
    """
    Class for RelativeNextSibling unit test suite.
    Some of the test methods had to be overwritten, because of the different behavior
    of RelativeNextSibling in comparison to other RelativeSelector classes.

    Its find_all method should return at most one element in the list.
    """

    base = RelativeNextSibling

    @pytest.fixture
    def match(self, to_element: ToElement) -> IElement:
        text = """
            <a>Not next sibling</a>
            <div class="anchor"></div>
            <a>1</a>
            <span>
                <a>Not a sibling</a>
            </span>
            <a>Not next sibling</a>
            <p>Not a link</p>
        """
        return to_element(text).find_all("div")[0]

    @pytest.fixture
    def no_match(self, to_element: ToElement) -> IElement:
        text = """
            <a>Not next sibling</a>
            <div class="anchor"></div>
            <p>Not a link</p>
            <span>
                <a>Not a sibling</a>
            </span>
        """
        return to_element(text).find_all("div")[0]

    @pytest.mark.parametrize(
        argnames="recursive",
        argvalues=[True, False],
        ids=["recursive", "not_recursive"],
    )
    def test_finds_all_elements_matching_selectors(
        self, selector: RelativeChild, recursive: bool, match: IElement
    ):
        """
        Tests if find_all method returns all children of element that match the selector,
        in case of RelativeNextSibling it should return only one element (next sibling).
        """
        result = selector.find_all(match, recursive=recursive)
        assert list(map(lambda x: strip(str(x)), result)) == [strip("""<a>1</a>""")]

    @pytest.mark.parametrize(
        argnames="recursive",
        argvalues=[True, False],
        ids=["recursive", "not_recursive"],
    )
    def test_find_all_returns_only_x_elements_when_limit_is_set(
        self, selector: RelativeChild, recursive: bool, match: IElement
    ):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned,
        but in case of RelativeNextSibling it should
        return only one element (next sibling).
        """
        result = selector.find_all(match, limit=2, recursive=recursive)
        assert list(map(lambda x: strip(str(x)), result)) == [strip("""<a>1</a>""")]

    def test_returns_none_or_empty_list_if_element_is_root(
        self, to_element: ToElement, selector: RelativeNextSibling
    ):
        """
        Tests if find methods return None or empty list if element is root element,
        which means it does not have any siblings.
        """
        text = """
            <a>Hello</a>
            <div>World</div>
        """
        root = to_element(text).find_ancestors()[-1]

        findall_result = selector.find_all(root)
        assert findall_result == []

        find_result = selector.find(root)
        assert find_result is None


class TestAnchor:
    """
    Test suite for Anchor object which is an instance of _Anchor class and it's supposed
    to be used as a singleton. It's used as a sugar syntax for creating RelativeSelector
    objects for different combinators.

    It's sole responsibility is to implement dunder methods for creating RelativeSelector
    that follow those implemented in SoupSelector interface for combinator selectors:

    - gt operator for RelativeChild
    - rshift operator for RelativeDescendant
    - add operator for RelativeNextSibling
    - mul operator for RelativeSubsequentSibling
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

    def test_anchoring_with_gt_operator_raises_exception_when_invalid_input(self):
        """
        Tests if using gt operator on Anchor instance raises NotSoupSelectorException
        when invalid input is provided.
        """
        with pytest.raises(NotSoupSelectorException):
            Anchor > "selector"  # type: ignore

    def test_anchoring_with_lt_operator_returns_parent_selector(self):
        """
        Tests if using gt operator on Anchor instance returns ParentSelector instance
        with proper selector attribute.
        """
        base = MockLinkSelector()
        result = Anchor < base
        assert isinstance(result, RelativeParent)
        assert result.selector == base

    def test_anchoring_with_lt_operator_raises_exception_when_invalid_input(self):
        """
        Tests if using lt operator on Anchor instance raises NotSoupSelectorException
        when invalid input is provided.
        """
        with pytest.raises(NotSoupSelectorException):
            Anchor < "selector"  # type: ignore

    def test_anchoring_with_rshift_operator_returns_relative_descendant(self):
        """
        Tests if using rshift operator on Anchor instance
        returns RelativeDescendant instance with proper selector attribute.
        """
        base = MockLinkSelector()
        result = Anchor >> base
        assert isinstance(result, RelativeDescendant)
        assert result.selector == base

    def test_anchoring_with_rshift_operator_raises_exception_when_invalid_input(self):
        """
        Tests if using rshift operator on Anchor instance
        raises NotSoupSelectorException when invalid input is provided.
        """
        with pytest.raises(NotSoupSelectorException):
            Anchor >> "selector"  # type: ignore

    def test_anchoring_with_lshift_operator_returns_ancestor_selector(self):
        """
        Tests if using rshift operator on Anchor instance
        returns AncestorSelector instance with proper selector attribute.
        """
        base = MockLinkSelector()
        result = Anchor << base
        assert isinstance(result, RelativeAncestor)
        assert result.selector == base

    def test_anchoring_with_lshift_operator_raises_exception_when_invalid_input(self):
        """
        Tests if using lshift operator on Anchor instance
        raises NotSoupSelectorException when invalid input is provided.
        """
        with pytest.raises(NotSoupSelectorException):
            Anchor << "selector"  # type: ignore

    def test_anchoring_with_add_operator_returns_relative_next_sibling(self):
        """
        Tests if using add operator on Anchor instance
        returns RelativeNextSibling instance with proper selector attribute.
        """
        base = MockLinkSelector()
        result = Anchor + base
        assert isinstance(result, RelativeNextSibling)
        assert result.selector == base

    def test_anchoring_with_add_operator_raises_exception_when_invalid_input(self):
        """
        Tests if using add operator on Anchor instance
        raises NotSoupSelectorException when invalid input is provided.
        """
        with pytest.raises(NotSoupSelectorException):
            Anchor + "selector"  # type: ignore

    def test_anchoring_with_mul_operator_returns_relative_subsequent_sibling(self):
        """
        Tests if using mul operator on Anchor instance returns
        RelativeSubsequentSibling instance with proper selector attribute.
        """
        base = MockLinkSelector()
        result = Anchor * base
        assert isinstance(result, RelativeSubsequentSibling)
        assert result.selector == base

    def test_anchoring_with_mul_operator_raises_exception_when_invalid_input(self):
        """
        Tests if using mul operator on Anchor instance
        raises NotSoupSelectorException when invalid input is provided.
        """
        with pytest.raises(NotSoupSelectorException):
            Anchor * "selector"  # type: ignore


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

        def find_all(
            self, tag: IElement, recursive: bool = True, limit=None
        ) -> list[IElement]:
            return []

    class MockRelativeSelectorNotEqual(RelativeSelector):
        """
        Mock class for testing equality of RelativeSelector,
        if right operand is instance of RelativeSelector but is of the
        different type, they are not equal.
        """

        def find_all(
            self, tag: IElement, recursive: bool = True, limit=None
        ) -> list[IElement]:
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


def _find_anchor(bs: IElement) -> IElement:
    """
    Finds element with 'anchor' class in the `IElement` object,
    which is used as an anchor element in the test cases.
    It needs to be in the element that's being searched.
    """
    return bs.find_all(attrs={"class": "anchor"})[0]


@pytest.mark.selector
class TestRelativeParent:
    """Class with test suite for RelativeParent selector."""

    @pytest.fixture(scope="class")
    def selector(self) -> RelativeParent:
        """
        Mock of simple RelativeParent selector that matches parent div elements,
        which is used in test cases.
        """
        return RelativeParent(MockDivSelector())

    def test_raises_exception_when_invalid_input(self):
        """
        Tests if selector raises NotSoupSelectorException when invalid input is provided
        on object initialization. It only accepts SoupSelector instances.
        """
        with pytest.raises(NotSoupSelectorException):
            RelativeParent("p")  # type: ignore

    def test_returns_none_or_empty_list_if_no_ancestors(
        self, selector: RelativeParent, to_element: ToElement
    ):
        """
        Tests if find method returns None if element does not have any ancestors,
        in such case, it must be the root element (html).
        """
        text = """
            <html><body><div class="anchor"></div></body></html>
        """
        bs = to_element(text)
        assert selector.find(bs) is None
        assert selector.find_all(bs) == []

    @pytest.mark.parametrize(
        argnames="recursive",
        argvalues=[True, False],
        ids=["recursive", "not_recursive"],
    )
    def test_find_returns_first_element_matching_selector(
        self, selector: RelativeParent, recursive: bool, to_element: ToElement
    ):
        """Tests if find method returns first element matching selector."""
        text = """
            <div><div><div class="anchor"><div></div></div></div></div>
            <div><div><p></p></div></div>
        """
        bs = _find_anchor(to_element(text))
        result = selector.find(bs, recursive=recursive)
        assert strip(str(result)) == strip(
            """<div><div class="anchor"><div></div></div></div>"""
        )

    @pytest.mark.parametrize(
        argnames="recursive",
        argvalues=[True, False],
        ids=["recursive", "not_recursive"],
    )
    def test_find_returns_none_if_no_match_and_strict_false(
        self, selector: RelativeParent, recursive: bool, to_element: ToElement
    ):
        """
        Tests if find returns None if no element matches the selector
        and strict is False.
        """
        text = """
            <div><span><div class="anchor"><div></div></div></span></div>
            <div><div><p></p></div></div>
        """
        bs = _find_anchor(to_element(text))
        result = selector.find(bs, recursive=recursive)
        assert result is None

    @pytest.mark.parametrize(
        argnames="recursive",
        argvalues=[True, False],
        ids=["recursive", "not_recursive"],
    )
    def test_find_raises_exception_if_no_match_and_strict_true(
        self, selector: RelativeParent, recursive: bool, to_element: ToElement
    ):
        """
        Tests if find raises TagNotFoundException if no element matches the selector
        and strict is True.
        """
        text = """
            <div><span><div class="anchor"><div></div></div></span></div>
            <div><div><p></p></div></div>
        """
        bs = _find_anchor(to_element(text))

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True, recursive=recursive)

    @pytest.mark.parametrize(
        argnames="recursive",
        argvalues=[True, False],
        ids=["recursive", "not_recursive"],
    )
    def test_find_all_returns_empty_list_when_no_match(
        self, selector: RelativeParent, recursive: bool, to_element: ToElement
    ):
        """Tests if find returns an empty list if no element matches the selector."""
        text = """
            <div><span><div class="anchor"><div></div></div></span></div>
            <div><div><p></p></div></div>
        """
        bs = _find_anchor(to_element(text))
        result = selector.find_all(bs, recursive=recursive)
        assert result == []

    @pytest.mark.parametrize(
        argnames="recursive",
        argvalues=[True, False],
        ids=["recursive", "not_recursive"],
    )
    def test_find_all_returns_all_matching_elements(
        self, selector: RelativeParent, recursive: bool, to_element: ToElement
    ):
        """Tests if find_all returns a list of all matching elements."""
        text = """
            <div><div><div class="anchor"><div></div></div></div></div>
            <div><div><p></p></div></div>
        """
        bs = _find_anchor(to_element(text))
        result = selector.find_all(bs, recursive=recursive)
        # returns at most one element (parent)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div><div class="anchor"><div></div></div></div>""")
        ]

    @pytest.mark.parametrize(
        argnames="recursive",
        argvalues=[True, False],
        ids=["recursive", "not_recursive"],
    )
    def test_find_all_returns_empty_list_if_element_is_root(
        self, selector: RelativeParent, recursive: bool, to_element: ToElement
    ):
        """Tests if find_all returns an empty list if element is root element."""
        text = """
            <div><div><div class="anchor"><div></div></div></div></div>
            <div><div><p></p></div></div>
        """
        bs = to_element(text).find_ancestors()[-1]
        result = selector.find_all(bs, recursive=recursive)
        assert result == []


@pytest.mark.selector
class TestRelativeAncestor:
    """Class with test suite for RelativeAncestor selector."""

    @pytest.fixture
    def selector(self) -> RelativeAncestor:
        """
        Mock of simple RelativeAncestor selector that matches parent div elements,
        which is used in test cases.
        """
        return RelativeAncestor(MockDivSelector())

    def test_raises_exception_when_invalid_input(self):
        """
        Tests if selector raises NotSoupSelectorException when invalid input is provided
        on object initialization. It only accepts SoupSelector instances.
        """
        with pytest.raises(NotSoupSelectorException):
            RelativeAncestor("p")  # type: ignore

    def test_returns_none_or_empty_list_if_no_ancestors(
        self, selector: RelativeAncestor, to_element: ToElement
    ):
        """
        Tests if find method returns None if element does not have any ancestors,
        in such case, it must be the root element (html).
        """
        text = """
            <html><body><div class="anchor"></div></body></html>
        """
        bs = to_element(text)
        assert selector.find(bs) is None
        assert selector.find_all(bs) == []

    @pytest.mark.parametrize(
        argnames="recursive",
        argvalues=[True, False],
        ids=["recursive", "not_recursive"],
    )
    def test_find_returns_first_element_matching_selector(
        self, selector: RelativeAncestor, recursive: bool, to_element: ToElement
    ):
        """Tests if find method returns first element matching selector."""
        text = """
            <div><div><div class="anchor"><div><div></div></div></div></div></div>
            <div><div><p></p></div></div>
        """
        bs = _find_anchor(to_element(text))
        result = selector.find(bs, recursive=recursive)
        assert strip(str(result)) == strip(
            """<div><div class="anchor"><div><div></div></div></div></div>"""
        )

    @pytest.mark.parametrize(
        argnames="recursive",
        argvalues=[True, False],
        ids=["recursive", "not_recursive"],
    )
    def test_find_returns_none_if_no_match_and_strict_false(
        self, selector: RelativeAncestor, recursive: bool, to_element: ToElement
    ):
        """
        Tests if find returns None if no element matches the selector
        and strict is False.
        """
        text = """
            <span><span><div class="anchor"><div><div></div></div></div></span></span>
            <div><div><p></p></div></div>
        """
        bs = _find_anchor(to_element(text))
        result = selector.find(bs, recursive=recursive)
        assert result is None

    @pytest.mark.parametrize(
        argnames="recursive",
        argvalues=[True, False],
        ids=["recursive", "not_recursive"],
    )
    def test_find_raises_exception_if_no_match_and_strict_true(
        self, selector: RelativeAncestor, recursive: bool, to_element: ToElement
    ):
        """
        Tests if find raises TagNotFoundException if no element matches the selector
        and strict is True.
        """
        text = """
            <span><span><div class="anchor"><div><div></div></div></div></span></span>
            <div><div><p></p></div></div>
        """
        bs = _find_anchor(to_element(text))

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True, recursive=recursive)

    @pytest.mark.parametrize(
        argnames="recursive",
        argvalues=[True, False],
        ids=["recursive", "not_recursive"],
    )
    def test_find_all_returns_empty_list_when_no_match(
        self, selector: RelativeAncestor, recursive: bool, to_element: ToElement
    ):
        """Tests if find returns an empty list if no element matches the selector."""
        text = """
            <span><span><div class="anchor"><div><div></div></div></div></span></span>
            <div><div><p></p></div></div>
        """
        bs = _find_anchor(to_element(text))
        result = selector.find_all(bs, recursive=recursive)
        assert result == []

    @pytest.mark.parametrize(
        argnames="recursive",
        argvalues=[True, False],
        ids=["recursive", "not_recursive"],
    )
    def test_find_all_returns_all_matching_elements(
        self, selector: RelativeAncestor, recursive: bool, to_element: ToElement
    ):
        """Tests if find_all returns a list of all matching elements."""
        text = """
            <div><span><div><a class="anchor"></a></div></span></div>
            <div><div><p></p></div></div>
        """
        bs = _find_anchor(to_element(text))
        result = selector.find_all(bs, recursive=recursive)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div><a class="anchor"></a></div>"""),
            strip("""<div><span><div><a class="anchor"></a></div></span></div>"""),
        ]

    @pytest.mark.parametrize(
        argnames="recursive",
        argvalues=[True, False],
        ids=["recursive", "not_recursive"],
    )
    def test_find_all_returns_only_x_elements_when_limit_is_set(
        self, selector: RelativeAncestor, recursive: bool, to_element: ToElement
    ):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <div><div><span><div><a class="anchor"></a></div></span></div></div>
        """
        bs = _find_anchor(to_element(text))
        result = selector.find_all(bs, limit=2, recursive=recursive)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div><a class="anchor"></a></div>"""),
            strip("""<div><span><div><a class="anchor"></a></div></span></div>"""),
        ]

    @pytest.mark.parametrize(
        argnames="recursive",
        argvalues=[True, False],
        ids=["recursive", "not_recursive"],
    )
    def test_find_all_returns_empty_list_if_element_is_root(
        self, selector: RelativeAncestor, recursive: bool, to_element: ToElement
    ):
        """Tests if find_all returns an empty list if element is root element."""
        text = """
            <div><div><span><div><a class="anchor"></a></div></span></div></div>
        """
        bs = to_element(text).find_ancestors()[-1]
        result = selector.find_all(bs, recursive=recursive)
        assert result == []
