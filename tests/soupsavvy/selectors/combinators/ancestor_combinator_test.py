"""Testing module for AncestorCombinator class."""

import pytest

from soupsavvy.exceptions import NotSoupSelectorException, TagNotFoundException
from soupsavvy.selectors.combinators import AncestorCombinator
from tests.soupsavvy.conftest import (
    MockClassMenuSelector,
    MockDivSelector,
    MockLinkSelector,
    find_body_element,
    strip,
    to_bs,
)


@pytest.mark.selector
@pytest.mark.combinator
class TestAncestorCombinator:
    """Class for AncestorCombinator unit test suite."""

    def test_raises_exception_when_invalid_input(self):
        """
        Tests if init raises NotSoupSelectorException when invalid input is provided.
        """
        with pytest.raises(NotSoupSelectorException):
            AncestorCombinator(MockDivSelector(), "p")  # type: ignore

        with pytest.raises(NotSoupSelectorException):
            AncestorCombinator("a", MockDivSelector())  # type: ignore

    def test_find_returns_first_tag_matching_selector(self):
        """Tests if find method returns the first tag that matches selector."""
        text = """
            <p>Hello</p>
            <div>Hello</div>
            <span><a>Hello</a></span>
            <div><span><a>1</a><p></p></span><p></p></div>
            <div><p></p></div>
            <span>
                <div><a>2</a><a><p>Hello</p></a></div>
                <p>Hello</p>
            </span>
            <div><div><a>34</a></div></div>
        """
        bs = find_body_element(to_bs(text))
        selector = AncestorCombinator(MockLinkSelector(), MockDivSelector())
        result = selector.find(bs)
        assert strip(str(result)) == strip(
            """<div><span><a>1</a><p></p></span><p></p></div>"""
        )

    def test_find_raises_exception_when_no_tags_match_in_strict_mode(self):
        """
        Tests if find method raises TagNotFoundException when no tag is found
        that matches selector in strict mode.
        """
        text = """
            <p>Hello</p>
            <div>Hello</div>
            <span><a>Hello</a></span>
            <div><p></p></div>
            <span><span><a></a></span></span>
        """
        bs = to_bs(text)
        selector = AncestorCombinator(MockLinkSelector(), MockDivSelector())

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_returns_none_if_no_tags_match_in_not_strict_mode(self):
        """
        Tests if find method returns None when no tag is found that
        matches selector in not strict mode.
        """
        text = """
            <p>Hello</p>
            <div>Hello</div>
            <span><a>Hello</a></span>
            <div><p></p></div>
            <span><span><a></a></span></span>
        """
        bs = to_bs(text)
        selector = AncestorCombinator(MockLinkSelector(), MockDivSelector())
        result = selector.find(bs)
        assert result is None

    def test_finds_all_tags_matching_selectors(self):
        """Tests if find_all method returns all tags that match selector."""
        text = """
            <p>Hello</p>
            <div>Hello</div>
            <span><a>Hello</a></span>
            <div><span><a>1</a><p></p></span><p></p></div>
            <div><p></p></div>
            <span>
                <div><a>2</a><a><p>Hello</p></a></div>
                <p>Hello</p>
            </span>
            <div><div><a>34</a></div><a>Hello</a></div>
        """
        bs = find_body_element(to_bs(text))
        selector = AncestorCombinator(MockLinkSelector(), MockDivSelector())
        result = selector.find_all(bs)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div><span><a>1</a><p></p></span><p></p></div>"""),
            strip("""<div><a>2</a><a><p>Hello</p></a></div>"""),
            strip("""<div><div><a>34</a></div><a>Hello</a></div>"""),
            strip("""<div><a>34</a></div>"""),
        ]

    def test_find_all_returns_empty_list_if_no_tag_matches(self):
        """
        Tests if find_all method returns an empty list when no tag is found
        that matches selector.
        """
        text = """
            <p>Hello</p>
            <div>Hello</div>
            <span><a>Hello</a></span>
            <div><p></p></div>
            <span><span><a></a></span></span>
        """
        bs = to_bs(text)
        selector = AncestorCombinator(MockLinkSelector(), MockDivSelector())
        result = selector.find_all(bs)
        assert result == []

    def test_find_returns_match_with_multiple_selectors(self):
        """
        Tests if find method returns the first tag that matches selector
        if there are multiple selectors are provided.
        """
        text = """
            <div>Hello</div>
            <span class="menu"><a>Missing div</a></span>
            <div><a><p class="menu">Not in order</p></a></div>
            <div><span><a>Not menu ancestor</a></span></div>
            <div><span class="menu"><p>Not a</p></span></div>
            <div><span class="menu"><a>1</a></span></div>
            <div><div><span><span class="menu"><a>23</a></span></span></div></div>
            <div><span><p class="menu"><span><a>4</a><a>Hello</a></span></p></span></div>
        """
        bs = find_body_element(to_bs(text))
        selector = AncestorCombinator(
            MockLinkSelector(),
            MockClassMenuSelector(),
            MockDivSelector(),
        )
        result = selector.find_all(bs)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div><span class="menu"><a>1</a></span></div>"""),
            strip(
                """<div><div><span><span class="menu"><a>23</a></span></span></div></div>"""
            ),
            strip("""<div><span><span class="menu"><a>23</a></span></span></div>"""),
            strip(
                """<div><span><p class="menu"><span><a>4</a><a>Hello</a></span></p></span></div>"""
            ),
        ]

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        text = """
            <p>Hello</p>
            <div>Hello</div>
            <span><a>Hello</a></span>
            <span>
                <div><a>Not child</a><a><p>Hello</p></a></div>
                <p>Hello</p>
            </span>
            <div><span><a>1</a><p></p></span><p></p></div>
            <div><p></p></div>
            <div><div><a>23</a></div><a>Hello</a></div>
        """
        bs = find_body_element(to_bs(text))
        selector = AncestorCombinator(MockLinkSelector(), MockDivSelector())
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip(
            """<div><span><a>1</a><p></p></span><p></p></div>"""
        )

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <p>Hello</p>
            <div>Hello</div>
            <span><a>Hello</a></span>
            <span>
                <div><a>Not child</a><a><p>Hello</p></a></div>
                <p>Hello</p>
            </span>
            <div><p></p></div>
        """
        bs = find_body_element(to_bs(text))
        selector = AncestorCombinator(MockLinkSelector(), MockDivSelector())
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <p>Hello</p>
            <div>Hello</div>
            <span><a>Hello</a></span>
            <span>
                <div><a>Not child</a><a><p>Hello</p></a></div>
                <p>Hello</p>
            </span>
            <div><p></p></div>
        """
        bs = find_body_element(to_bs(text))
        selector = AncestorCombinator(MockLinkSelector(), MockDivSelector())

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True, recursive=False)

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <p>Hello</p>
            <div>Hello</div>
            <span>
                <div><a>Not child</a><a><p>Hello</p></a></div>
                <p>Hello</p>
            </span>
            <div><span><a>1</a><p></p></span><p></p></div>
            <div><p></p></div>
            <div><div><a>2</a></div><a>Hello</a></div>
            <span><a>Hello</a></span>
            <div><a>3</a></div>
        """
        bs = find_body_element(to_bs(text))
        selector = AncestorCombinator(MockLinkSelector(), MockDivSelector())
        result = selector.find_all(bs, recursive=False)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div><span><a>1</a><p></p></span><p></p></div>"""),
            strip("""<div><div><a>2</a></div><a>Hello</a></div>"""),
            strip("""<div><a>3</a></div>"""),
        ]

    def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
        self,
    ):
        """
        Tests if find_all returns an empty list if no child element matches the selector
        and recursive is False.
        """
        text = """
            <p>Hello</p>
            <div>Hello</div>
            <span><a>Hello</a></span>
            <span>
                <div><a>Not child</a><a><p>Hello</p></a></div>
                <p>Hello</p>
            </span>
            <div><p></p></div>
        """
        bs = find_body_element(to_bs(text))
        selector = AncestorCombinator(MockLinkSelector(), MockDivSelector())
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <p>Hello</p>
            <div>Hello</div>
            <span><a>Hello</a></span>
            <div><span><a>1</a><p></p></span><p></p></div>
            <div><p></p></div>
            <span>
                <div><a>2</a><a><p>Hello</p></a></div>
                <p>Hello</p>
            </span>
            <div><div><a>34</a></div><a>Hello</a></div>
        """
        bs = find_body_element(to_bs(text))
        selector = AncestorCombinator(MockLinkSelector(), MockDivSelector())
        result = selector.find_all(bs, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div><span><a>1</a><p></p></span><p></p></div>"""),
            strip("""<div><a>2</a><a><p>Hello</p></a></div>"""),
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
            <p>Hello</p>
            <div>Hello</div>
            <span>
                <div><a>Not child</a><a><p>Hello</p></a></div>
                <p>Hello</p>
            </span>
            <div><span><a>1</a><p></p></span><p></p></div>
            <div><p></p></div>
            <div><div><a>2</a></div><a>Hello</a></div>
            <span><a>Hello</a></span>
            <div><a>3</a></div>
        """
        bs = find_body_element(to_bs(text))
        selector = AncestorCombinator(MockLinkSelector(), MockDivSelector())
        result = selector.find_all(bs, recursive=False, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div><span><a>1</a><p></p></span><p></p></div>"""),
            strip("""<div><div><a>2</a></div><a>Hello</a></div>"""),
        ]

    def test_find_returns_none_if_first_step_was_not_found(self):
        """
        Tests if find returns None if the first step was not found.
        Ensures that combinators don't break when first step does not match anything.
        """
        text = """<span>First element</sp>"""
        bs = to_bs(text)
        selector = AncestorCombinator(MockLinkSelector(), MockDivSelector())
        result = selector.find_all(bs)
        assert result == []
