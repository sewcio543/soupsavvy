"""Testing module for NotSelector class."""

import pytest

from soupsavvy.exceptions import NotSoupSelectorException, TagNotFoundException
from soupsavvy.selectors.logical import NotSelector, SelectorList
from tests.soupsavvy.conftest import (
    MockDivSelector,
    MockLinkSelector,
    find_body_element,
    strip,
    to_bs,
)


@pytest.mark.selector
class TestNotSelector:
    """Class for NotSelector unit test suite."""

    def test_raises_exception_when_no_invalid_input(self):
        """
        Tests if init raises NotSoupSelectorException when invalid input is provided.
        All of the parameters must be SoupSelector instances.
        """
        with pytest.raises(NotSoupSelectorException):
            NotSelector("div", MockDivSelector())  # type: ignore

        with pytest.raises(NotSoupSelectorException):
            NotSelector(MockLinkSelector(), "div")  # type: ignore

    def test_find_returns_first_tag_matching_selector(self):
        """
        Tests if find method returns the first tag that matches all the selectors.
        """
        text = """
            <a class="link"></a>
            <a></a>
            <div class="widget">1</div>
            <a><p>2</p><a>Hello</a></a>
            <p>3</p>
            <div><a>4</a></div>
        """
        bs = find_body_element(to_bs(text))
        selector = NotSelector(MockLinkSelector())
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<div class="widget">1</div>""")

    def test_find_raises_exception_when_no_tags_match_in_strict_mode(self):
        """
        Tests if find method raises TagNotFoundException when no tag is found
        that matches all the selectors in strict mode.
        """
        text = """
            <a class="link"></a>
            <a></a>
            <a><a>Hello</a></a>
        """
        bs = find_body_element(to_bs(text))
        selector = NotSelector(MockLinkSelector())

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_returns_none_if_no_tags_match_in_not_strict_mode(self):
        """
        Tests if find method returns None when no tag is found that
        matches all the selectors in not strict mode.
        """
        text = """
            <a class="link"></a>
            <a></a>
            <a><a>Hello</a></a>
        """
        bs = find_body_element(to_bs(text))
        selector = NotSelector(MockLinkSelector())
        result = selector.find(bs)
        assert result is None

    def test_finds_all_tags_matching_selectors(self):
        """Tests if find_all method returns all tags that match selector."""
        text = """
            <a class="link"></a>
            <a></a>
            <div class="widget">1</div>
            <a><p>2</p><a>Hello</a></a>
            <div><p>34</p></div>
        """
        bs = find_body_element(to_bs(text))
        selector = NotSelector(MockLinkSelector())
        result = selector.find_all(bs)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div class="widget">1</div>"""),
            strip("""<p>2</p>"""),
            strip("""<div><p>34</p></div>"""),
            strip("""<p>34</p>"""),
        ]

    def test_find_all_returns_empty_list_if_no_tag_matches(self):
        """
        Tests if find_all method returns an empty list when no tag is found
        that matches selector.
        """
        text = """
            <a class="link"></a>
            <a></a>
            <a><a>Hello</a></a>
        """
        bs = find_body_element(to_bs(text))
        selector = NotSelector(MockLinkSelector())
        result = selector.find_all(bs)
        assert result == []

    def test_find_returns_match_with_multiple_selectors(self):
        """
        Tests if find method returns the first tag that matches selector
        if there are multiple selectors are provided.
        """
        text = """
            <a class="menu"></a>
            <div class="menu"></div>
            <a><p>1</p></a>
            <a>Hello</a>
            <div><span>2</span><a>Hello</a></div>
            <p>3</p>
        """
        bs = find_body_element(to_bs(text))

        selector = NotSelector(
            MockDivSelector(),
            MockLinkSelector(),
        )
        result = selector.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<p>1</p>"""),
            strip("""<span>2</span>"""),
            strip("""<p>3</p>"""),
        ]

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        text = """
            <a class="link"></a>
            <a><p>Not a child</p><a>Hello</a></a>
            <div><p>1</p></div>
            <a></a>
            <div class="widget">2</div>
            <p><a>3</a></p>
        """
        bs = find_body_element(to_bs(text))
        selector = NotSelector(MockLinkSelector())
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<div><p>1</p></div>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <a class="link"></a>
            <a><span>Not a child</span></a>
            <a><p>Not a child</p></a>
        """
        bs = find_body_element(to_bs(text))
        selector = NotSelector(MockLinkSelector())
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <a class="link"></a>
            <a><span>Not a child</span></a>
            <a><p>Not a child</p></a>
        """
        bs = find_body_element(to_bs(text))
        selector = NotSelector(MockLinkSelector())

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True, recursive=False)

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <a class="link"></a>
            <div class="widget">1</div>
            <a></a>
            <div><p>23</p></div>
            <a><p>4</p></a>
        """
        bs = find_body_element(to_bs(text))
        selector = NotSelector(MockLinkSelector())
        result = selector.find_all(bs, recursive=False)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div class="widget">1</div>"""),
            strip("""<div><p>23</p></div>"""),
        ]

    def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
        self,
    ):
        """
        Tests if find_all returns an empty list if no child element matches the selector
        and recursive is False.
        """
        text = """
            <a class="link"></a>
            <a><span>Not a child</span></a>
            <a><p>Not a child</p></a>
        """
        bs = find_body_element(to_bs(text))
        selector = NotSelector(MockLinkSelector())
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <a class="link"></a>
            <a><p>1</p></a>
            <a></a>
            <div class="widget">2</div>
            <p><a>3</a></p>
            <a class="link"></a>
            <div>4</div>
        """
        bs = find_body_element(to_bs(text))
        selector = NotSelector(MockLinkSelector())
        result = selector.find_all(bs, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<p>1</p>"""),
            strip("""<div class="widget">2</div>"""),
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
            <a class="link"></a>
            <div><p>1</p><a>Hello</a></div>
            <a><p>Not child</p></a>
            <a></a>
            <div class="widget">2</div>
            <p><a>3</a></p>
            <a class="link"></a>
            <div>4</div>
        """
        bs = find_body_element(to_bs(text))
        selector = NotSelector(MockLinkSelector())
        result = selector.find_all(bs, recursive=False, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div><p>1</p><a>Hello</a></div>"""),
            strip("""<div class="widget">2</div>"""),
        ]

    def test_bitwise_not_operator_with_multiple_selectors_returns_union(
        self,
    ):
        """
        Tests if bitwise NOT operator (__invert__) returns SelectorList instance
        when applied to NotSelector instance with multiple selectors.
        """
        selector1 = MockDivSelector()
        selector2 = MockLinkSelector()
        not_selector = NotSelector(selector1, selector2)
        negation = ~not_selector
        assert negation == SelectorList(selector1, selector2)

    def test_bitwise_not_operator_with_single_selector_returns_selector(
        self,
    ):
        """
        Tests if bitwise NOT operator (__invert__) returns NotSelector selector
        when applied to NotSelector instance with single selector.
        """
        selector = MockDivSelector()
        not_selector = NotSelector(selector)
        negation = ~not_selector
        assert negation == selector
