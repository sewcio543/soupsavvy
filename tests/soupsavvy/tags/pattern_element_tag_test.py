"""Testing module for PatternElementTag class."""

import re

import pytest

from soupsavvy.tags.components import (
    AnyTag,
    AttributeTag,
    ElementTag,
    PatternElementTag,
)
from soupsavvy.tags.exceptions import (
    NavigableStringException,
    TagNotFoundException,
    WildcardTagException,
)

from .conftest import strip, to_bs


@pytest.mark.soup
class TestPatternElementTag:
    """Class for PatternElementTag unit test suite."""

    @pytest.mark.parametrize(
        argnames="tag",
        argvalues=[
            PatternElementTag(
                pattern="Hello World",
                tag=ElementTag(
                    "div", attributes=[AttributeTag("class", value="widget")]
                ),
            ),
            PatternElementTag(tag=ElementTag("div"), pattern="Hello World"),
            PatternElementTag(tag=ElementTag("div"), pattern="Hello", re=True),
            PatternElementTag(
                tag=ElementTag(attributes=[AttributeTag("class", value="widget")]),
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
    def test_element_is_found_for_valid_pattern_tags(self, tag: PatternElementTag):
        """
        Tests if element was found for various valid PatternElementTags.
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
            PatternElementTag(
                pattern="Hello World",
                tag=ElementTag("div", attributes=[AttributeTag("class", value="menu")]),
            ),
            PatternElementTag(tag=ElementTag("div"), pattern="Hello Python"),
            PatternElementTag(
                tag=ElementTag(attributes=[AttributeTag("class", value="widget")]),
                pattern=re.compile(r"World \d"),
            ),
        ],
        ids=["not_match_attr", "not_match_text", "not_match_pattern"],
    )
    def test_element_is_not_found_for_not_matching_pattern_tags(
        self, tag: PatternElementTag
    ):
        """
        Tests if element was not found and method returs None
        for various PatternElementTags that does not match element.
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
        tag = PatternElementTag(tag=ElementTag("div"), pattern="Hello Python")

        with pytest.raises(TagNotFoundException):
            tag.find(bs, strict=True)

    def test_init_raises_exception_if_input_tag_is_anytag(self):
        """
        Tests if init raises WildcardElementTagException if tag passed
        to pattern tag is AnyTag. This is not allowed since AnyTag is a wildcard tag.
        """
        with pytest.raises(WildcardTagException):
            PatternElementTag(tag=AnyTag(), pattern="Hello")

    def test_find_all_returns_list_of_matched_elements(self):
        """
        Tests if PatternElementTag find_all method returns
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
        tag = PatternElementTag(
            tag=ElementTag("a", attributes=[AttributeTag(name="href", value="github")]),
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
        Tests if PatternElementTag find_all method returns empty list if
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
        tag = PatternElementTag(
            tag=ElementTag("a", attributes=[AttributeTag(name="href", value="github")]),
            pattern="Hello World",
        )
        result = tag.find_all(bs)
        assert isinstance(result, list)
        assert len(result) == 0


class LegalWildcardTag(ElementTag):
    """
    Mock class that is ElementTag that allows no parameters passed to init.
    This way wildcard tag can be created that is a valid input into PatternElementTag.
    This enables to create hypothetical case when find method returns NavigableString
    instead of Tag (only string parameter was passed into bs4.find method).
    This should raise NavigableStringException that is an invalid output of
    SelectableSoup.find method.
    """

    def __post_init__(self):
        """Overriden post init to not raise exception on empty tag and attributes."""


@pytest.mark.soup
@pytest.mark.edge_case
def test_exception_is_raised_when_navigable_string_is_a_result():
    """
    Tests if NavigableStringException is raised when bs4.find returns NavigableString.
    Child classes of SelectableSoup should always always prevent that,
    thus this is a hypothetical case that is covered anyway to ensure that it does
    not break code downstream.
    """
    markup = """<div class="widget">Hello World</div>"""
    bs = to_bs(markup)
    tag = PatternElementTag(tag=LegalWildcardTag(), pattern="Hello World")

    with pytest.raises(NavigableStringException):
        tag.find(bs, strict=True)
