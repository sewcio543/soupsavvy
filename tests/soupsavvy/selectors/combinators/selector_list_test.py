"""Testing module for SelectorList class."""

import pytest

from soupsavvy.exceptions import NotSoupSelectorException, TagNotFoundException
from soupsavvy.selectors.combinators import SelectorList
from tests.soupsavvy.selectors.conftest import (
    MockClassMenuSelector,
    MockDivSelector,
    MockLinkSelector,
    find_body_element,
    strip,
    to_bs,
)


@pytest.mark.selector
@pytest.mark.combinator
class TestSelectorList:
    """Class for SelectorList unit test suite."""

    def test_raises_exception_when_invalid_input(self):
        """
        Tests if init raises NotSoupSelectorException when invalid input is provided.
        """
        with pytest.raises(NotSoupSelectorException):
            SelectorList(MockDivSelector(), "p")  # type: ignore

        with pytest.raises(NotSoupSelectorException):
            SelectorList("a", MockDivSelector())  # type: ignore

    def test_find_returns_first_tag_matching_selector(self):
        """Tests if find method returns the first tag that matches selector."""
        text = """
            <p>Hello</p>
            <span><p>Hello</p></span>
            <a>1</a>
            <div class="widget"><span>2</span></div>
            <span>
                <a class="widget">3</a>
                <span class="widget"><div>4</div></span>
            </span>
        """
        bs = find_body_element(to_bs(text))

        selector = SelectorList(MockDivSelector(), MockLinkSelector())
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<a>1</a>""")

    def test_find_raises_exception_when_no_tags_match_in_strict_mode(self):
        """
        Tests if find method raises TagNotFoundException when no tag is found
        that matches selector in strict mode.
        """
        text = """
            <p>Hello</p>
            <span><p>Hello</p></span>
            <span>
                <h1>Header</h1>
                <span class="widget"></span>
            </span>
        """
        bs = to_bs(text)
        selector = SelectorList(MockDivSelector(), MockLinkSelector())

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_returns_none_if_no_tags_match_in_not_strict_mode(self):
        """
        Tests if find method returns None when no tag is found that
        matches selector in not strict mode.
        """
        text = """
            <p>Hello</p>
            <span><p>Hello</p></span>
            <span>
                <h1>Header</h1>
                <span class="widget"></span>
            </span>
        """
        bs = to_bs(text)
        selector = SelectorList(MockDivSelector(), MockLinkSelector())
        result = selector.find(bs)
        assert result is None

    def test_finds_all_tags_matching_selectors(self):
        """Tests if find_all method returns all tags that match selector."""
        text = """
            <p>Hello</p>
            <span><p>Hello</p></span>
            <a>1</a>
            <div class="widget"><a>23</a></div>
            <span>
                <a class="widget">4</a>
                <span class="widget"><div>5</div></span>
            </span>
        """
        bs = find_body_element(to_bs(text))
        selector = SelectorList(MockDivSelector(), MockLinkSelector())
        result = selector.find_all(bs)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a>1</a>"""),
            strip("""<div class="widget"><a>23</a></div>"""),
            strip("""<a>23</a>"""),
            strip("""<a class="widget">4</a>"""),
            strip("""<div>5</div>"""),
        ]

    def test_find_all_returns_empty_list_if_no_tag_matches(self):
        """
        Tests if find_all method returns an empty list when no tag is found
        that matches selector.
        """
        text = """
            <p>Hello</p>
            <span><p>Hello</p></span>
            <span>
                <h1>Header</h1>
                <span class="widget"></span>
            </span>
        """
        bs = to_bs(text)
        selector = SelectorList(MockDivSelector(), MockLinkSelector())
        result = selector.find_all(bs)
        assert result == []

    def test_find_returns_match_with_multiple_selectors(self):
        """
        Tests if find method returns the first tag that matches selector
        if there are multiple selectors are provided.
        """
        text = """
            <p>Hello</p>
            <span><p>Hello</p></span>
            <a>1</a>
            <span>
                <a class="widget">2</a>
                <span class="widget"><div>3</div></span>
            </span>
            <span id="menu">
                <h2>Menu</h2>
            </span>
            <p class="menu123">4</p>
            <p class="menu">4</p>
            <span>Hello</span>
            <div class="menu">5</div>
        """
        bs = to_bs(text)
        selector = SelectorList(
            MockDivSelector(),
            MockLinkSelector(),
            MockClassMenuSelector(),
        )
        result = selector.find_all(bs)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a>1</a>"""),
            strip("""<a class="widget">2</a>"""),
            strip("""<div>3</div>"""),
            strip("""<p class="menu">4</p>"""),
            strip("""<div class="menu">5</div>"""),
        ]

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        text = """
            <p>Hello</p>
            <span>
                <a class="widget">3</a>
                <span class="widget"><div>4</div></span>
            </span>
            <a>1</a>
            <span><p>Hello</p></span>
            <div class="widget"><span>2</span></div>
        """
        bs = find_body_element(to_bs(text))
        selector = SelectorList(MockDivSelector(), MockLinkSelector())
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<a>1</a>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <p>Hello</p>
            <span>
                <a class="widget">Not child</a>
                <span class="widget"><div>Not child</div></span>
            </span>
            <span><p>Hello</p></span>
        """
        bs = find_body_element(to_bs(text))
        selector = SelectorList(MockDivSelector(), MockLinkSelector())
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <p>Hello</p>
            <span>
                <a class="widget">Not child</a>
                <span class="widget"><div>Not child</div></span>
            </span>
            <span><p>Hello</p></span>
        """
        bs = find_body_element(to_bs(text))
        selector = SelectorList(MockDivSelector(), MockLinkSelector())

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True, recursive=False)

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <p>Hello</p>
            <span><p>Hello</p></span>
            <a>1</a>
            <span>
                <a class="widget">Not child</a>
                <span class="widget"><div>Not child</div></span>
            </span>
            <p class="menu"></p>
            <div class="widget"><a>2</a></div>
        """
        bs = find_body_element(to_bs(text))
        selector = SelectorList(MockDivSelector(), MockLinkSelector())
        result = selector.find_all(bs, recursive=False)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a>1</a>"""),
            strip("""<div class="widget"><a>2</a></div>"""),
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
            <span>
                <a class="widget">Not child</a>
                <span class="widget"><div>Not child</div></span>
            </span>
            <span><p>Hello</p></span>
        """
        bs = find_body_element(to_bs(text))
        selector = SelectorList(MockDivSelector(), MockLinkSelector())
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <p>Hello</p>
            <span><p>Hello</p></span>
            <a>1</a>
            <span>
                <a class="widget">2</a>
                <span class="widget"><div>3</div></span>
            </span>
            <div>4</div>
            <span id="menu">
                <h2>Menu</h2>
            </span>
        """
        bs = find_body_element(to_bs(text))
        selector = SelectorList(MockDivSelector(), MockLinkSelector())
        result = selector.find_all(bs, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a>1</a>"""),
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
            <p>Hello</p>
            <span><p>Hello</p></span>
            <a>1</a>
            <span>
                <a class="widget">Not child</a>
                <span class="widget"><div>Not child</div></span>
            </span>
            <div>2</div>
            <span id="menu">
                <h2>Menu</h2>
            </span>
            <a class="widget">3</a>
        """
        bs = find_body_element(to_bs(text))
        selector = SelectorList(MockDivSelector(), MockLinkSelector())
        result = selector.find_all(bs, recursive=False, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a>1</a>"""),
            strip("""<div>2</div>"""),
        ]
