"""Testing module for PatternSelector class."""

import re

import pytest

from soupsavvy.exceptions import TagNotFoundException
from soupsavvy.selectors.general import PatternSelector
from tests.soupsavvy.conftest import MockLinkSelector, find_body_element, strip, to_bs


@pytest.mark.selector
class TestPatternSelector:
    """Class for PatternSelector unit test suite."""

    def test_find_returns_first_match_with_exact_value(self):
        """
        Tests if find returns first selector with text content that matches the specified value.
        """
        text = """
            <div class="Hello"></div>
            <div>Hi Hi Hello</div>
            <a>Hello</a>
            <div>
                <div>Good morning</div>
            </div>
            <div>Hello</div>
        """
        bs = to_bs(text)
        selector = PatternSelector("Hello")
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<a>Hello</a>""")

    def test_find_returns_first_match_with_re_true(self):
        """
        Tests if find returns first selector with text content
        that matches the specified regex pattern. Checks as wel if if in case of
        compiled regex pattern, re.search is used instead of re.match.
        """
        text = """
            <div class="Hello">Good Morning</div>
            <a>Helllo</a>
            <div>Hi Hi Hello</div>
            <div>
                <div>Good morning</div>
            </div>
            <div>Hello Hello</div>
        """
        bs = to_bs(text)
        selector = PatternSelector(pattern=re.compile("Hello"))
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<div>Hi Hi Hello</div>""")

    def test_find_returns_first_match_with_pattern(self):
        """
        Tests if find returns first selector with text content that matches compiled regex pattern,
        ignoring re parameter. The same behavior should be observed when passing
        string of the same regex pattern and re=True.
        """
        text = """
            <div>Good Morning</div>
            <div>Morning, Hello 12</div>
            <a>Hello 1234</a>
            <div>
                <p>Hello 12 World</p>
                <div>Good morning</div>
            </div>
            <a>Hello 123</a>
            <a>Hello 456</a>
        """
        bs = to_bs(text)
        selector = PatternSelector(pattern=re.compile(r"^Hello.?\d{1,3}$"))
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<a>Hello 123</a>""")

    def test_find_returns_first_match_with_raw_string_as_pattern(self):
        """
        Tests if find returns first selector with text content
        that matches the specified raw string. When raw string is used, and re is False,
        the pattern is treated as a literal string.
        """
        text = """
            <div>Hello</div>
            <div>
                <div>Hello, Good morning</div>
            </div>
            <a>^Hello World</a>
            <a>^Hello</a>
            <div>Hi Hi Hello</div>
            <div>^Hello</div>
        """
        bs = to_bs(text)
        selector = PatternSelector(r"^Hello")
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<a>^Hello</a>""")

    def test_find_does_not_return_element_with_children_that_matches_text(self):
        """
        Tests if find does not return element that has children, even though
        its text content matches the selector. It's due to bs4 implementation
        that does not match element on text if it has children.
        """
        text = """
            <div>Hello<div></div></div>
        """
        bs = to_bs(text)
        selector = PatternSelector(re.compile("Hello"))
        result = selector.find(bs)
        assert result is None

    def test_find_returns_none_if_no_match_and_strict_false(self):
        """
        Tests if find returns None if no element matches the selector
        and strict is False.
        """
        text = """
            <div class="Hello"></div>
            <div>Hi Hi Hello</div>
            <div>
                <div>Good morning</div>
            </div>
        """
        bs = to_bs(text)
        selector = PatternSelector("Hello")
        result = selector.find(bs)
        assert result is None

    def test_find_raises_exception_if_no_match_and_strict_true(self):
        """
        Tests find raises TagNotFoundException if no element matches the selector
        and strict is True.
        """
        text = """
            <div class="Hello"></div>
            <div>Hi Hi Hello</div>
            <div>
                <div>Good morning</div>
            </div>
        """
        bs = to_bs(text)
        selector = PatternSelector("Hello")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_all_returns_all_matching_elements(self):
        """Tests if find_all returns a list of all matching elements."""
        text = """
            <div class="Hello"></div>
            <div>Hello</div>
            <div>Hi Hi Hello</div>
            <div>
                <div>Good morning</div>
                <a>Hello</a>
            </div>
            <p>Hello</p>
        """
        bs = to_bs(text)
        selector = PatternSelector("Hello")

        result = selector.find_all(bs)
        excepted = [
            strip("""<div>Hello</div>"""),
            strip("""<a>Hello</a>"""),
            strip("""<p>Hello</p>"""),
        ]
        assert list(map(lambda x: strip(str(x)), result)) == excepted

    def test_find_all_returns_empty_list_when_no_match(self):
        """Tests if find returns an empty list if no element matches the selector."""
        text = """
            <div class="Hello"></div>
            <div>Hi Hi Hello</div>
            <div>
                <div>Good morning</div>
            </div>
        """
        bs = to_bs(text)
        selector = PatternSelector("Hello")
        result = selector.find_all(bs)
        assert result == []

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """Tests if find returns first matching child element if recursive is False."""
        text = """
            <div class="Hello 2"></div>
            <div>
                <div>Hello</div>
            </div>
            <span>Hello</span>
            <div>Hi Hi Hello</div>
            <div>Hello</div>
        """
        bs = find_body_element(to_bs(text))
        selector = PatternSelector(pattern="Hello")
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<span>Hello</span>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div class="Hello 2"></div>
            <div>
                <div>Hello</div>
            </div>
            <div>Hi Hi Hello</div>
        """
        bs = find_body_element(to_bs(text))
        selector = PatternSelector(pattern="Hello")
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <div class="Hello 2"></div>
            <div>
                <div>Hello</div>
            </div>
            <div>Hi Hi Hello</div>
        """
        bs = find_body_element(to_bs(text))
        selector = PatternSelector(pattern="Hello")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True, recursive=False)

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <p>Hello</p>
            <div class="Hello 2"></div>
            <div>Hi Hi Hello</div>
            <div>
                <div>Hello</div>
            </div>
            <a>Hello</a>
            <span>Hello</span>
        """
        bs = find_body_element(to_bs(text))
        selector = PatternSelector(pattern="Hello")
        result = selector.find_all(bs, recursive=False)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<p>Hello</p>"""),
            strip("""<a>Hello</a>"""),
            strip("""<span>Hello</span>"""),
        ]

    def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
        self,
    ):
        """
        Tests if find_all returns an empty list if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div class="Hello 2"></div>
            <div>
                <div>Hello</div>
            </div>
            <div>Hi Hi Hello</div>
        """
        bs = find_body_element(to_bs(text))
        selector = PatternSelector(pattern="Hello")
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <p>Hello</p>
            <div class="Hello 2"></div>
            <div>Hi Hi Hello</div>
            <div>
                <div>Hello</div>
            </div>
            <a>Hello</a>
            <span>Hello</span>
        """
        bs = find_body_element(to_bs(text))
        selector = PatternSelector(pattern="Hello")
        result = selector.find_all(bs, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<p>Hello</p>"""),
            strip("""<div>Hello</div>"""),
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
            <div class="Hello 2"></div>
            <div>Hi Hi Hello</div>
            <div>
                <div>Hello</div>
            </div>
            <a>Hello</a>
            <span>Hello</span>
        """
        bs = find_body_element(to_bs(text))
        selector = PatternSelector(pattern="Hello")
        result = selector.find_all(bs, recursive=False, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<p>Hello</p>"""),
            strip("""<a>Hello</a>"""),
        ]

    @pytest.mark.parametrize(
        argnames="selectors",
        argvalues=[
            # pattern is the same string
            (PatternSelector("menu"), PatternSelector("menu")),
            # pattern is the same compiled regex
            (
                PatternSelector(re.compile("^menu")),
                PatternSelector(re.compile("^menu")),
            ),
        ],
    )
    def test_two_selectors_are_equal(
        self, selectors: tuple[PatternSelector, PatternSelector]
    ):
        """Tests if two PatternSelectors are equal."""
        assert (selectors[0] == selectors[1]) is True

    @pytest.mark.parametrize(
        argnames="selectors",
        argvalues=[
            # string pattern is different
            (PatternSelector("menu"), PatternSelector("widget")),
            # string pattern with re=False not equal to compiled regex
            (PatternSelector(re.compile("menu")), PatternSelector("menu")),
            # compiled regex patterns are different
            (PatternSelector(re.compile("menu")), PatternSelector(re.compile("^menu"))),
            # not PatternSelector instance
            (PatternSelector("menu"), MockLinkSelector()),
        ],
    )
    def test_two_selectors_are_not_equal(
        self, selectors: tuple[PatternSelector, PatternSelector]
    ):
        """Tests if two PatternSelectors are not equal."""
        assert (selectors[0] == selectors[1]) is False
