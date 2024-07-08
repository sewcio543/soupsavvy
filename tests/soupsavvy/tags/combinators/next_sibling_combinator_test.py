"""Testing module for NextSiblingCombinator class."""

import pytest

from soupsavvy.tags.combinators import NextSiblingCombinator
from soupsavvy.tags.exceptions import NotSoupSelectorException, TagNotFoundException
from tests.soupsavvy.tags.conftest import (
    MockClassMenuSelector,
    MockDivSelector,
    MockLinkSelector,
    find_body_element,
    strip,
    to_bs,
)


@pytest.mark.soup
@pytest.mark.combinator
class TestNextSiblingCombinator:
    """Class for NextSiblingCombinator unit test suite."""

    def test_raises_exception_when_invalid_input(self):
        """
        Tests if init raises NotSoupSelectorException when invalid input is provided.
        """
        with pytest.raises(NotSoupSelectorException):
            NextSiblingCombinator(MockDivSelector(), "p")  # type: ignore

        with pytest.raises(NotSoupSelectorException):
            NextSiblingCombinator("a", MockDivSelector())  # type: ignore

    def test_find_returns_first_tag_matching_selector(self):
        """Tests if find method returns the first tag that matches selector."""
        text = """
            <p>Hello</p>
            <div>Hello</div>
            <span><a>Hello</a></span>
            <a></a>
            <div class="widget"><span></span></div>
            <a class="link">1</a>
            <span>
                <a></a>
                <div></div>
                <a>2</a>
            </span>
        """
        bs = find_body_element(to_bs(text))
        selector = NextSiblingCombinator(MockDivSelector(), MockLinkSelector())
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<a class="link">1</a>""")

    def test_find_raises_exception_when_no_tags_match_in_strict_mode(self):
        """
        Tests if find method raises TagNotFoundException when no tag is found
        that matches selector in strict mode.
        """
        text = """
            <p>Hello</p>
            <div><a>Not a sibling</a></div>
            <span><a>Hello</a></span>
            <a></a>
            <div class="widget"><span></span></div>
            <p class="link"></p>
            <a>2</a>
        """
        bs = to_bs(text)
        selector = NextSiblingCombinator(MockDivSelector(), MockLinkSelector())

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_returns_none_if_no_tags_match_in_not_strict_mode(self):
        """
        Tests if find method returns None when no tag is found that
        matches selector in not strict mode.
        """
        text = """
            <p>Hello</p>
            <div><a>Not a sibling</a></div>
            <span><a>Hello</a></span>
            <a></a>
            <div class="widget"><span></span></div>
            <p class="link"></p>
            <a>2</a>
        """
        bs = to_bs(text)
        selector = NextSiblingCombinator(MockDivSelector(), MockLinkSelector())
        result = selector.find(bs)
        assert result is None

    def test_finds_all_tags_matching_selectors(self):
        """Tests if find_all method returns all tags that match selector."""
        text = """
            <p>Hello</p>
            <div>Hello</div>
            <span><a>Hello</a></span>
            <a></a>
            <div class="widget"><span></span></div>
            <a class="link">1</a>
            <span>
                <a></a>
                <div></div>
                <a><p>2</p></a>
            </span>
            <div><a>Not sibling</a></div>
            <div><span>Hello</span></div>
            <a class="widget">3</a>
        """
        bs = find_body_element(to_bs(text))
        selector = NextSiblingCombinator(MockDivSelector(), MockLinkSelector())
        result = selector.find_all(bs)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="link">1</a>"""),
            strip("""<a><p>2</p></a>"""),
            strip("""<a class="widget">3</a>"""),
        ]

    def test_find_all_returns_empty_list_if_no_tag_matches(self):
        """
        Tests if find_all method returns an empty list when no tag is found
        that matches selector.
        """
        text = """
            <p>Hello</p>
            <div><a>Not a sibling</a></div>
            <span><a>Hello</a></span>
            <a></a>
            <div class="widget"><span></span></div>
            <p class="link"></p>
            <a>2</a>
        """
        bs = to_bs(text)
        selector = NextSiblingCombinator(MockDivSelector(), MockLinkSelector())
        result = selector.find_all(bs)
        assert result == []

    def test_find_returns_match_with_multiple_selectors(self):
        """
        Tests if find method returns the first tag that matches selector
        if there are multiple selectors are provided.
        """
        text = """
            <div></div>
            <span></span>

            <div></div>
            <a></a>
            <span class="menu">1</span>

            <div></div>
            <a></a>
            <p></p>

            <div>
                <a></a>
                <div></div>
                <a></a>
                <p class="menu"><a>2</a></p>
            </div>
        """
        bs = find_body_element(to_bs(text))
        selector = NextSiblingCombinator(
            MockDivSelector(),
            MockLinkSelector(),
            MockClassMenuSelector(),
        )
        result = selector.find_all(bs)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<span class="menu">1</span>"""),
            strip("""<p class="menu"><a>2</a></p>"""),
        ]

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        text = """
            <p>Hello</p>
            <div>Hello</div>
            <span>
                <a></a>
                <div></div>
                <a>Not child</a>
            </span>
            <div class="widget"><span></span></div>
            <a class="link">1</a>
            <a></a>
            <div><a>Not a sibling</a></div>
            <a class="link">2</a>
        """
        bs = find_body_element(to_bs(text))
        selector = NextSiblingCombinator(MockDivSelector(), MockLinkSelector())
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<a class="link">1</a>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <p>Hello</p>
            <div><a>Not a sibling</a></div>
            <span><a>Hello</a></span>
            <div>
                <div></div>
                <a>Not a child</a>
            </div>
            <div class="widget"><span></span></div>
            <p class="link"></p>
        """
        bs = find_body_element(to_bs(text))
        selector = NextSiblingCombinator(MockDivSelector(), MockLinkSelector())
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <p>Hello</p>
            <div><a>Not a sibling</a></div>
            <span><a>Hello</a></span>
            <div>
                <div></div>
                <a>Not a child</a>
            </div>
            <div class="widget"><span></span></div>
            <p class="link"></p>
        """
        bs = find_body_element(to_bs(text))
        selector = NextSiblingCombinator(MockDivSelector(), MockLinkSelector())

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
            <span><a>Hello</a></span>
            <a></a>
            <div class="widget"><span></span></div>
            <a class="link">1</a>
            <span>
                <a></a>
                <div></div>
                <a><p>Not a child</p></a>
            </span>
            <div><a>Not sibling</a></div>
            <div><span>Hello</span></div>
            <a class="widget">2</a>
        """
        bs = find_body_element(to_bs(text))
        selector = NextSiblingCombinator(MockDivSelector(), MockLinkSelector())
        result = selector.find_all(bs, recursive=False)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="link">1</a>"""),
            strip("""<a class="widget">2</a>"""),
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
            <div><a>Not a sibling</a></div>
            <span><a>Hello</a></span>
            <div>
                <div></div>
                <a>Not a child</a>
            </div>
            <div class="widget"><span></span></div>
            <p class="link"></p>
        """
        bs = find_body_element(to_bs(text))
        selector = NextSiblingCombinator(MockDivSelector(), MockLinkSelector())
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
            <a></a>
            <div class="widget"><span></span></div>
            <a class="link">1</a>
            <span>
                <a></a>
                <div></div>
                <a><p>2</p></a>
            </span>
            <div><a>Not sibling</a></div>
            <div><span>Hello</span></div>
            <a class="widget">3</a>
        """
        bs = find_body_element(to_bs(text))
        selector = NextSiblingCombinator(MockDivSelector(), MockLinkSelector())
        result = selector.find_all(bs, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="link">1</a>"""),
            strip("""<a><p>2</p></a>"""),
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
            <div></div>
            <a><p>1</p></a>
            <div>Hello</div>
            <span><a>Hello</a></span>
            <a></a>
            <span>
                <a></a>
                <div></div>
                <a><p>Not a child</p></a>
            </span>
            <div class="widget"><span></span></div>
            <a class="link">2</a>
            <div><a>Not sibling</a></div>
            <div><span>Hello</span></div>
            <a class="widget">3</a>
        """
        bs = find_body_element(to_bs(text))
        selector = NextSiblingCombinator(MockDivSelector(), MockLinkSelector())
        result = selector.find_all(bs, recursive=False, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a><p>1</p></a>"""),
            strip("""<a class="link">2</a>"""),
        ]

    def test_find_returns_none_if_first_step_was_not_found(self):
        """
        Tests if find returns None if the first step was not found.
        Ensures that combinators don't break when first step does not match anything.
        """
        text = """<a>First element</a>"""
        bs = to_bs(text)
        selector = NextSiblingCombinator(MockDivSelector(), MockLinkSelector())
        result = selector.find_all(bs)
        assert result == []
