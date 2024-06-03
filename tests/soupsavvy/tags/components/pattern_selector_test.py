"""Testing module for PatternSelector class."""

import re

import pytest

from soupsavvy.tags.components import (
    AnyTagSelector,
    AttributeSelector,
    PatternSelector,
    TagSelector,
)
from soupsavvy.tags.exceptions import (
    NavigableStringException,
    TagNotFoundException,
    WildcardTagException,
)
from tests.soupsavvy.tags.conftest import find_body_element, strip, to_bs


@pytest.mark.soup
class TestPatternSelector:
    """Class for PatternSelector unit test suite."""

    @pytest.mark.parametrize(
        argnames="tag",
        argvalues=[
            PatternSelector(
                pattern="Hello World",
                tag=TagSelector(
                    "div", attributes=[AttributeSelector("class", value="widget")]
                ),
            ),
            PatternSelector(tag=TagSelector("div"), pattern="Hello World"),
            PatternSelector(tag=TagSelector("div"), pattern="Hello", re=True),
            PatternSelector(
                tag=TagSelector(
                    attributes=[AttributeSelector("class", value="widget")]
                ),
                pattern=re.compile("World"),
            ),
        ],
        ids=[
            "match_with_name_and_attrs",
            "match_with_tag_name",
            "match_with_re",
            "match_with_re_pattern",
        ],
    )
    def test_element_is_found_for_valid_pattern_tags(self, tag: PatternSelector):
        """
        Tests if element was found for various valid PatternSelectors.
        Element is returned if it matches the ElementTag and has text matching
        provided pattern.
        """
        markup = """<div class="widget">Hello World</div>"""
        bs = to_bs(markup)
        result = tag.find(bs)
        assert str(result) == strip(markup)

    @pytest.mark.parametrize(
        argnames="tag",
        argvalues=[
            PatternSelector(
                pattern="Hello World",
                tag=TagSelector(
                    "div", attributes=[AttributeSelector("class", value="menu")]
                ),
            ),
            PatternSelector(tag=TagSelector("div"), pattern="Hello Python"),
            PatternSelector(
                tag=TagSelector(
                    attributes=[AttributeSelector("class", value="widget")]
                ),
                pattern=re.compile(r"World \d"),
            ),
        ],
        ids=["not_match_attr", "not_match_text", "not_match_pattern"],
    )
    def test_element_is_not_found_for_not_matching_pattern_tags(
        self, tag: PatternSelector
    ):
        """
        Tests if element was not found and method returns None
        for various PatternSelectors that does not match element.
        """
        markup = """<div class="widget">Hello World</div>"""
        bs = to_bs(markup)
        assert tag.find(bs) is None

    def test_find_raises_exception_when_tag_not_found_in_strict_mode(self):
        """
        Tests if find raises TagNotFoundException exception if no element was found
        and method was called in a strict mode.
        """
        markup = """<div class="widget">Hello World</div>"""
        bs = to_bs(markup)
        tag = PatternSelector(tag=TagSelector("div"), pattern="Hello Python")

        with pytest.raises(TagNotFoundException):
            tag.find(bs, strict=True)

    def test_init_raises_exception_if_input_tag_is_anytag(self):
        """
        Tests if init raises WildcardElementTagException if tag passed
        to pattern tag is AnyTag. This is not allowed since AnyTag is a wildcard tag.
        """
        with pytest.raises(WildcardTagException):
            PatternSelector(tag=AnyTagSelector(), pattern="Hello")

    def test_find_all_returns_list_of_matched_elements(self):
        """
        Tests if PatternSelector find_all method returns
        a list of all matched elements.
        """
        text = """
            <a href="github">Hello World</a>
            <div href="github">Hello World</div>
            <a href="github/settings">Hello World</a>
            <a href="github">Hello</a>
            <a href="github">World</a>
            <a class="github">Hello World</a>
            <a href="github">Hello Python</a>
        """
        bs = to_bs(text)
        tag = PatternSelector(
            tag=TagSelector(
                "a", attributes=[AttributeSelector(name="href", value="github")]
            ),
            pattern="Hello",
            re=True,
        )
        result = tag.find_all(bs)
        expected = [
            strip("""<a href="github">Hello World</a>"""),
            strip("""<a href="github">Hello</a>"""),
            strip("""<a href="github">Hello Python</a>"""),
        ]
        assert list(map(str, result)) == expected

    def test_find_all_returns_empty_list_if_no_matched_elements(self):
        """
        Tests if PatternSelector find_all method returns empty list if
        no element matches the tag.
        """
        text = """
            <div href="github">Hello World</div>
            <a href="github/settings">Hello World</a>
            <a href="github">Hello</a>
            <a href="github">World</a>
            <a class="github">Hello World</a>
            <a href="github">Hello Python</a>
        """
        bs = to_bs(text)
        tag = PatternSelector(
            tag=TagSelector(
                "a", attributes=[AttributeSelector(name="href", value="github")]
            ),
            pattern="Hello World",
        )
        result = tag.find_all(bs)
        assert result == []

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        In this case first span and <div>Hello 1</div> do not match
        because they are not div and not direct child in this order.
        """
        text = """
            <span>Hello</span>
            <div class="Hello"></div>
            <div>
                <div>Hello 1</div>
            </div>
            <div>Hello 2</div>
        """
        bs = find_body_element(to_bs(text))
        tag = PatternSelector(
            TagSelector(tag="div"),
            pattern="Hello",
            re=True,
        )
        result = tag.find(bs, recursive=False)

        assert str(result) == strip("""<div>Hello 2</div>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <span>Hello</span>
            <div class="Hello"></div>
            <div>
                <div>Hello 1</div>
            </div>
        """
        bs = find_body_element(to_bs(text))
        tag = PatternSelector(
            TagSelector(tag="div"),
            pattern="Hello",
            re=True,
        )
        result = tag.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <span>Hello</span>
            <div class="Hello"></div>
            <div>
                <div>Hello 1</div>
            </div>
        """
        bs = find_body_element(to_bs(text))
        tag = PatternSelector(
            TagSelector(tag="div"),
            pattern="Hello",
            re=True,
        )

        with pytest.raises(TagNotFoundException):
            tag.find(bs, strict=True, recursive=False)

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <span>Hello</span>
            <div class="Hello"></div>
            <div>
                <div>Hello 1</div>
            </div>
            <div>Hello 2</div>
            <div>Morning, Hello</div>
        """
        bs = find_body_element(to_bs(text))
        tag = PatternSelector(
            TagSelector(tag="div"),
            pattern="Hello",
            re=True,
        )
        results = tag.find_all(bs, recursive=False)

        assert list(map(str, results)) == [
            strip("""<div>Hello 2</div>"""),
            strip("""<div>Morning, Hello</div>"""),
        ]

    def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
        self,
    ):
        """
        Tests if find_all returns an empty list if no child element matches the selector
        and recursive is False.
        """
        text = """
            <span>Hello</span>
            <div class="Hello"></div>
            <div>
                <div>Hello 1</div>
            </div>
        """
        bs = find_body_element(to_bs(text))
        tag = PatternSelector(
            TagSelector(tag="div"),
            pattern="Hello",
            re=True,
        )

        results = tag.find_all(bs, recursive=False)
        assert results == []

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <span>
                <div>Hello 1</div>
            </span>
            <div>Github</div>
            <div>Hello 2</div>
            <div>Hello 3</div>
        """
        bs = find_body_element(to_bs(text))
        tag = PatternSelector(
            TagSelector(tag="div"),
            pattern="Hello",
            re=True,
        )
        results = tag.find_all(bs, limit=2)

        assert list(map(str, results)) == [
            strip("""<div>Hello 1</div>"""),
            strip("""<div>Hello 2</div>"""),
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
            <span>
                <div>Hello 1</div>
            </span>
            <div>Github</div>
            <div>Hello 2</div>
            <div>Hello 3</div>
        """
        bs = find_body_element(to_bs(text))
        tag = PatternSelector(
            TagSelector(tag="div"),
            pattern="Hello",
            re=True,
        )
        results = tag.find_all(bs, recursive=False, limit=2)

        assert list(map(str, results)) == [
            strip("""<div>Hello 2</div>"""),
            strip("""<div>Hello 3</div>"""),
        ]


class LegalWildcardTag(TagSelector):
    """
    Mock class that is ElementTag that allows no parameters passed to init.
    This way wildcard tag can be created that is a valid input into PatternSelector.
    This enables to create hypothetical case when find method returns NavigableString
    instead of Tag (only string parameter was passed into bs4.find method).
    This should raise NavigableStringException that is an invalid output of
    SoupSelector.find method.
    """

    def __post_init__(self):
        """Overridden post init to not raise exception on empty tag and attributes."""


@pytest.mark.soup
@pytest.mark.edge_case
def test_exception_is_raised_when_navigable_string_is_a_result():
    """
    Tests if NavigableStringException is raised when bs4.find returns NavigableString.
    Child classes of SoupSelector should always always prevent that,
    thus this is a hypothetical case that is covered anyway to ensure that it does
    not break code downstream.
    """
    markup = """<div class="widget">Hello World</div>"""
    bs = to_bs(markup)
    tag = PatternSelector(tag=LegalWildcardTag(), pattern="Hello World")

    with pytest.raises(NavigableStringException):
        tag.find(bs, strict=True)
