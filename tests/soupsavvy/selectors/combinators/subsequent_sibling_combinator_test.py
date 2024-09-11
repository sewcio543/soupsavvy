"""Testing module for SubsequentSiblingCombinator class."""

import pytest

from soupsavvy.exceptions import NotSoupSelectorException, TagNotFoundException
from soupsavvy.selectors.combinators import SubsequentSiblingCombinator
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
class TestSubsequentSiblingCombinator:
    """Class for SubsequentSiblingCombinator unit test suite."""

    def test_raises_exception_when_invalid_input(self):
        """
        Tests if init raises NotSoupSelectorException when invalid input is provided.
        """
        with pytest.raises(NotSoupSelectorException):
            SubsequentSiblingCombinator(MockLinkSelector(), "p")  # type: ignore

        with pytest.raises(NotSoupSelectorException):
            SubsequentSiblingCombinator("a", MockLinkSelector())  # type: ignore

    def test_find_returns_first_tag_matching_selector(self):
        """Tests if find method returns the first tag that matches selector."""
        text = """
            <a>Hello</a>
            <div></div>
            <div><span>Hello</span></div>
            <span class="widget"><a>Not a sibling</a></span>
            <a class="link">1</a>
            <div>
                <div>Hello</div>
                <a class="widget">2</a>
                <span class="widget"></span>
                <a>3</a>
            </div>
            <a class="widget"><p>4</p></a>
        """
        bs = find_body_element(to_bs(text))

        selector = SubsequentSiblingCombinator(MockDivSelector(), MockLinkSelector())
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<a class="link">1</a>""")

    def test_find_raises_exception_when_no_tags_match_in_strict_mode(self):
        """
        Tests if find method raises TagNotFoundException when no tag is found
        that matches selector in strict mode.
        """
        text = """
            <a>Hello</a>
            <div></div>
            <div><span>Hello</span></div>
            <span class="widget"><a>Not a sibling</a></span>
            <div>
                <a class="widget"></a>
                <div>Hello</div>
                <span class="widget"></span>
            </div>
            <span class="widget">Hello</span>
        """
        bs = to_bs(text)
        selector = SubsequentSiblingCombinator(MockDivSelector(), MockLinkSelector())

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_returns_none_if_no_tags_match_in_not_strict_mode(self):
        """
        Tests if find method returns None when no tag is found that
        matches selector in not strict mode.
        """
        text = """
            <a>Hello</a>
            <div></div>
            <div><span>Hello</span></div>
            <span class="widget"><a>Not a sibling</a></span>
            <div>
                <a class="widget"></a>
                <div>Hello</div>
                <span class="widget"></span>
            </div>
            <span class="widget">Hello</span>
        """
        bs = to_bs(text)
        selector = SubsequentSiblingCombinator(MockDivSelector(), MockLinkSelector())
        result = selector.find(bs)
        assert result is None

    def test_finds_all_tags_matching_selectors(self):
        """Tests if find_all method returns all tags that match selector."""
        text = """
            <a>Hello</a>
            <div></div>
            <div><span>Hello</span></div>
            <span class="widget"><a>Not a sibling</a></span>
            <a class="link">1</a>
            <div>
                <div>Hello</div>
                <a class="widget">2</a>
                <span class="widget"></span>
                <a>3</a>
            </div>
            <a class="widget"><p>4</p></a>
        """
        bs = find_body_element(to_bs(text))
        selector = SubsequentSiblingCombinator(MockDivSelector(), MockLinkSelector())
        result = selector.find_all(bs)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="link">1</a>"""),
            strip("""<a class="widget">2</a>"""),
            strip("""<a>3</a>"""),
            strip("""<a class="widget"><p>4</p></a>"""),
        ]

    def test_find_all_returns_empty_list_if_no_tag_matches(self):
        """
        Tests if find_all method returns an empty list when no tag is found
        that matches selector.
        """
        text = """
            <a>Hello</a>
            <div></div>
            <div><span>Hello</span></div>
            <span class="widget"><a>Not a sibling</a></span>
            <div>
                <a class="widget"></a>
                <div>Hello</div>
                <span class="widget"></span>
            </div>
            <span class="widget">Hello</span>
        """
        bs = to_bs(text)
        selector = SubsequentSiblingCombinator(MockDivSelector(), MockLinkSelector())
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
            <span></span>
            <a></a>
            <p></p>
            <span class="menu">1</span>

            <div></div>
            <a></a>
            <p></p>

            <div>
                <a></a>
                <div></div>
                <a></a>
                <div></div>
                <a>Hello</a>
                <span>Hello</span>
                <p></p>
                <p class="menu"><a>2</a></p>
                <div class="menu">3</div>
            </div>
        """
        bs = find_body_element(to_bs(text))
        selector = SubsequentSiblingCombinator(
            MockDivSelector(),
            MockLinkSelector(),
            MockClassMenuSelector(),
        )
        result = selector.find_all(bs)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<span class="menu">1</span>"""),
            strip("""<p class="menu"><a>2</a></p>"""),
            strip("""<div class="menu">3</div>"""),
        ]

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        text = """
            <a>Hello</a>
            <div>
                <div>Hello</div>
                <a class="widget">Not child</a>
                <span class="widget"></span>
                <a>Not child</a>
            </div>
            <div><span>Hello</span></div>
            <a class="link">1</a>
            <span class="widget"><a>Not a sibling</a></span>
            <a class="widget"><p>2</p></a>
        """
        bs = find_body_element(to_bs(text))
        selector = SubsequentSiblingCombinator(MockDivSelector(), MockLinkSelector())
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<a class="link">1</a>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <a>Hello</a>
            <div>
                <div>Hello</div>
                <a class="widget">Not child</a>
                <span class="widget"></span>
                <a>Not child</a>
            </div>
            <div><span>Hello</span></div>
            <span class="widget"><a>Not a sibling</a></span>
        """
        bs = find_body_element(to_bs(text))
        selector = SubsequentSiblingCombinator(MockDivSelector(), MockLinkSelector())
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <a>Hello</a>
            <div>
                <div>Hello</div>
                <a class="widget">Not child</a>
                <span class="widget"></span>
                <a>Not child</a>
            </div>
            <div><span>Hello</span></div>
            <span class="widget"><a>Not a sibling</a></span>
        """
        bs = find_body_element(to_bs(text))
        selector = SubsequentSiblingCombinator(MockDivSelector(), MockLinkSelector())

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True, recursive=False)

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <a>Hello</a>
            <div>
                <div>Hello</div>
                <a class="widget">Not child</a>
                <span class="widget"></span>
                <a>Not child</a>
            </div>
            <a class="link">1</a>
            <div><span>Hello</span></div>
            <a class="widget"><p>2</p></a>
            <span class="widget"><a>Not a sibling</a></span>
            <a>3</a>
        """
        bs = find_body_element(to_bs(text))
        selector = SubsequentSiblingCombinator(MockDivSelector(), MockLinkSelector())
        result = selector.find_all(bs, recursive=False)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="link">1</a>"""),
            strip("""<a class="widget"><p>2</p></a>"""),
            strip("""<a>3</a>"""),
        ]

    def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
        self,
    ):
        """
        Tests if find_all returns an empty list if no child element matches the selector
        and recursive is False.
        """
        text = """
            <a>Hello</a>
            <div>
                <div>Hello</div>
                <a class="widget">Not child</a>
                <span class="widget"></span>
                <a>Not child</a>
            </div>
            <div><span>Hello</span></div>
            <span class="widget"><a>Not a sibling</a></span>
        """
        bs = find_body_element(to_bs(text))
        selector = SubsequentSiblingCombinator(MockDivSelector(), MockLinkSelector())
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <a>Hello</a>
            <div></div>
            <div><span>Hello</span></div>
            <span class="widget"><a>Not a sibling</a></span>
            <a class="link">1</a>
            <div>
                <div>Hello</div>
                <a class="widget">2</a>
                <span class="widget"></span>
                <a>3</a>
            </div>
            <a class="widget"><p>4</p></a>
        """
        bs = find_body_element(to_bs(text))
        selector = SubsequentSiblingCombinator(MockDivSelector(), MockLinkSelector())
        result = selector.find_all(bs, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="link">1</a>"""),
            strip("""<a class="widget">2</a>"""),
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
            <a>Hello</a>
            <div>
                <div>Hello</div>
                <a class="widget">Not child</a>
                <span class="widget"></span>
                <a>Not child</a>
            </div>
            <a class="link">1</a>
            <div><span>Hello</span></div>
            <a class="widget"><p>2</p></a>
            <span class="widget"><a>Not a sibling</a></span>
            <a>3</a>
        """
        bs = find_body_element(to_bs(text))
        selector = SubsequentSiblingCombinator(MockDivSelector(), MockLinkSelector())
        result = selector.find_all(bs, recursive=False, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="link">1</a>"""),
            strip("""<a class="widget"><p>2</p></a>"""),
        ]

    def test_find_returns_none_if_first_step_was_not_found(self):
        """
        Tests if find returns None if the first step was not found.
        Ensures that combinators don't break when first step does not match anything.
        """
        text = """<a>First element</a>"""
        bs = to_bs(text)
        selector = SubsequentSiblingCombinator(MockDivSelector(), MockLinkSelector())
        result = selector.find_all(bs)
        assert result == []
