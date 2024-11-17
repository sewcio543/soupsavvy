"""Testing module for ParentCombinator class."""

import pytest

from soupsavvy.exceptions import NotSoupSelectorException, TagNotFoundException
from soupsavvy.selectors.combinators import ParentCombinator
from tests.soupsavvy.conftest import (
    MockClassMenuSelector,
    MockDivSelector,
    MockLinkSelector,
    ToElement,
    strip,
)


@pytest.mark.selector
@pytest.mark.combinator
class TestParentCombinator:
    """Class for ParentCombinator unit test suite."""

    def test_raises_exception_when_invalid_input(self):
        """
        Tests if init raises NotSoupSelectorException when invalid input is provided.
        """
        with pytest.raises(NotSoupSelectorException):
            ParentCombinator(MockDivSelector(), "p")  # type: ignore

        with pytest.raises(NotSoupSelectorException):
            ParentCombinator("a", MockDivSelector())  # type: ignore

    def test_find_returns_first_element_matching_selector(self, to_element: ToElement):
        """Tests if find method returns the first element, that matches selector."""
        text = """
            <p>Hello</p>
            <div>Hello</div>
            <span><a>Hello</a></span>
            <div><span><a>Hello</a></span></div>
            <div><a>1</a><a><p>Hello</p></a></div>
            <div><p></p></div>
            <span>
                <div><a>2</a><p><a>Hello</a></p></div>
                <p>Hello</p>
            </span>
            <div><a>3</a></div>
        """
        bs = to_element(text)
        selector = ParentCombinator(MockLinkSelector(), MockDivSelector())
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<div><a>1</a><a><p>Hello</p></a></div>""")

    def test_find_raises_exception_when_no_element_match_in_strict_mode(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find method raises TagNotFoundException when no element is found
        that matches selector in strict mode.
        """
        text = """
            <p>Hello</p>
            <div>Hello</div>
            <span><a>Hello</a></span>
            <div><span><a>Hello</a></span></div>
            <div><p></p></div>
        """
        bs = to_element(text)
        selector = ParentCombinator(MockLinkSelector(), MockDivSelector())

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_returns_none_if_no_elements_match_in_not_strict_mode(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find method returns None when no element is found that
        matches selector in not strict mode.
        """
        text = """
            <p>Hello</p>
            <div>Hello</div>
            <span><a>Hello</a></span>
            <div><span><a>Hello</a></span></div>
            <div><p></p></div>
        """
        bs = to_element(text)
        selector = ParentCombinator(MockLinkSelector(), MockDivSelector())
        result = selector.find(bs)
        assert result is None

    def test_finds_all_elements_matching_selectors(self, to_element: ToElement):
        """Tests if find_all method returns all elements that match selector."""
        text = """
            <p>Hello</p>
            <div>Hello</div>
            <span><a>Hello</a></span>
            <div><span><a>Hello</a></span></div>
            <div><a>1</a><a><p>Hello</p></a></div>
            <div><p></p></div>
            <span>
                <div><a>2</a><p><a>Hello</a></p></div>
                <p>Hello</p>
            </span>
            <div><a>3</a></div>
        """
        bs = to_element(text)
        selector = ParentCombinator(MockLinkSelector(), MockDivSelector())
        result = selector.find_all(bs)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div><a>1</a><a><p>Hello</p></a></div>"""),
            strip("""<div><a>2</a><p><a>Hello</a></p></div>"""),
            strip("""<div><a>3</a></div>"""),
        ]

    def test_find_all_returns_empty_list_if_no_element_matches(
        self, to_element: ToElement
    ):
        """
        Tests if find_all method returns an empty list when no element is found
        that matches selector.
        """
        text = """
            <p>Hello</p>
            <div>Hello</div>
            <span><a>Hello</a></span>
            <div><span><a>Hello</a></span></div>
            <div><p></p></div>
        """
        bs = to_element(text)
        selector = ParentCombinator(MockLinkSelector(), MockDivSelector())
        result = selector.find_all(bs)
        assert result == []

    def test_find_returns_match_with_multiple_selectors(self, to_element: ToElement):
        """
        Tests if find method returns the first element, that matches selector
        if there are multiple selectors are provided.
        """
        text = """
            <div>Hello</div>
            <span class="menu"><a>Missing div</a></span>
            <div><a><p class="menu">Not in order</p></a></div>
            <div><span><a>Not menu parent</a></span></div>
            <div><span class="menu"><p>Not a</p></span></div>
            <div><span class="menu"><a>1</a></span></div>
            <div><span><span class="menu"><a>Menu not child of div</a></span></span></div>
            <div><p class="menu"><a>2</a><a>Hello</a></p><a>Hello</a></div>
        """
        bs = to_element(text)
        selector = ParentCombinator(
            MockLinkSelector(),
            MockClassMenuSelector(),
            MockDivSelector(),
        )
        result = selector.find_all(bs)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div><span class="menu"><a>1</a></span></div>"""),
            strip(
                """<div><p class="menu"><a>2</a><a>Hello</a></p><a>Hello</a></div>"""
            ),
        ]

    def test_find_returns_first_matching_child_if_recursive_false(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        text = """
            <p>Hello</p>
            <span><a>Hello</a></span>
            <div><p></p></div>
            <span>
                <div><a>Not child</a></div>
                <p>Hello</p>
            </span>
            <div><a>1</a><a><p>Hello</p></a></div>
            <div><span><a>Hello</a></span></div>
            <div><a>2</a></div>
            <div>Hello</div>
            <div><a>3</a><p>Hello</p></div>
        """
        bs = to_element(text)
        selector = ParentCombinator(MockLinkSelector(), MockDivSelector())
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<div><a>1</a><a><p>Hello</p></a></div>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <p>Hello</p>
            <span><a>Hello</a></span>
            <div><p></p></div>
            <span>
                <div><a>Not child</a></div>
                <p>Hello</p>
            </span>
            <div><span><a>Not child of div</a></span></div>
            <div>Hello</div>
        """
        bs = to_element(text)
        selector = ParentCombinator(MockLinkSelector(), MockDivSelector())
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
            <p>Hello</p>
            <span><a>Hello</a></span>
            <div><p></p></div>
            <span>
                <div><a>Not child</a></div>
                <p>Hello</p>
            </span>
            <div><span><a>Not child of div</a></span></div>
            <div>Hello</div>
        """
        bs = to_element(text)
        selector = ParentCombinator(MockLinkSelector(), MockDivSelector())

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
            <p>Hello</p>
            <span><a>Hello</a></span>
            <div><p></p></div>
            <div><a>1</a><a><p>Hello</p></a></div>
            <span>
                <div><a>Not child</a></div>
                <p>Hello</p>
            </span>
            <div><span><a>Hello</a></span></div>
            <div><a>2</a></div>
            <div>Hello</div>
            <div><a>3</a><p>Hello</p></div>
        """
        bs = to_element(text)
        selector = ParentCombinator(MockLinkSelector(), MockDivSelector())
        result = selector.find_all(bs, recursive=False)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div><a>1</a><a><p>Hello</p></a></div>"""),
            strip("""<div><a>2</a></div>"""),
            strip("""<div><a>3</a><p>Hello</p></div>"""),
        ]

    def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find_all returns an empty list if no child element matches the selector
        and recursive is False.
        """
        text = """
            <p>Hello</p>
            <span><a>Hello</a></span>
            <div><p></p></div>
            <span>
                <div><a>Not child</a></div>
                <p>Hello</p>
            </span>
            <div><span><a>Not child of div</a></span></div>
            <div>Hello</div>
        """
        bs = to_element(text)
        selector = ParentCombinator(MockLinkSelector(), MockDivSelector())
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
            <p>Hello</p>
            <div>Hello</div>
            <span><a>Hello</a></span>
            <div><span><a>Hello</a></span></div>
            <div><a>1</a><a><p>Hello</p></a></div>
            <div><p></p></div>
            <span>
                <div><a>2</a><p><a>Hello</a></p></div>
                <p>Hello</p>
            </span>
            <div><a>3</a></div>
        """
        bs = to_element(text)
        selector = ParentCombinator(MockLinkSelector(), MockDivSelector())
        result = selector.find_all(bs, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div><a>1</a><a><p>Hello</p></a></div>"""),
            strip("""<div><a>2</a><p><a>Hello</a></p></div>"""),
        ]

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
            <p>Hello</p>
            <span><a>Hello</a></span>
            <div><p></p></div>
            <div><a>1</a><a><p>Hello</p></a></div>
            <span>
                <div><a>Not child</a></div>
                <p>Hello</p>
            </span>
            <div><span><a>Hello</a></span></div>
            <div><a>2</a></div>
            <div>Hello</div>
            <div><a>3</a><p>Hello</p></div>
        """
        bs = to_element(text)
        selector = ParentCombinator(MockLinkSelector(), MockDivSelector())
        result = selector.find_all(bs, recursive=False, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div><a>1</a><a><p>Hello</p></a></div>"""),
            strip("""<div><a>2</a></div>"""),
        ]

    def test_find_returns_none_if_first_step_was_not_found(self, to_element: ToElement):
        """
        Tests if find returns None if the first step was not found.
        Ensures that combinators don't break when first step does not match anything.
        """
        text = """<span>First element</sp>"""
        bs = to_element(text)
        selector = ParentCombinator(MockLinkSelector(), MockDivSelector())
        result = selector.find_all(bs)
        assert result == []
