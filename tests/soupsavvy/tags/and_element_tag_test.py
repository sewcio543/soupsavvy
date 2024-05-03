"""Testing module for AndElementTag class."""

import pytest

from soupsavvy.tags.base import AndElementTag
from soupsavvy.tags.components import AttributeTag, ElementTag, StepsElementTag
from soupsavvy.tags.exceptions import NotSelectableSoupException, TagNotFoundException

from .conftest import strip, to_bs


@pytest.mark.soup
class TestAndElementTag:
    """Class for AndElementTag unit test suite."""

    def test_raises_exception_when_no_invalid_input(self):
        """
        Tests if init raises NotSelectableSoupException when invalid input is provided.
        All of the parameters must be SelectableSoup instances.
        """
        with pytest.raises(NotSelectableSoupException):
            AndElementTag("div", AttributeTag("class"))  # type: ignore

    def test_find_returns_first_tag_matching_all_selectors(self):
        """
        Tests if find method returns the first tag that matches all the selectors.
        """
        markup = """
            <a class="link"></a>
            <div class="widget"></div>
            <a class="widget"></a>
        """
        bs = to_bs(markup)

        tag = AndElementTag(ElementTag("a"), AttributeTag("class", "widget"))
        result = tag.find(bs)
        assert str(result) == strip("""<a class="widget"></a>""")

    def test_find_raises_exception_when_no_tags_match_in_strict_mode(self):
        """
        Tests if find method raises TagNotFoundException when no tag is found
        that matches all the selectors in strict mode.
        """
        markup = """<div class="widget"></div><a class="link"></a>"""
        bs = to_bs(markup)
        tag = AndElementTag(ElementTag("a"), AttributeTag("class", "widget"))

        with pytest.raises(TagNotFoundException):
            tag.find(bs, strict=True)

    def test_find_returns_none_if_no_tags_match_in_not_strict_mode(self):
        """
        Tests if find method returns None when no tag is found that
        matches all the selectors in not strict mode.
        """
        markup = """<div class="widget"></div><a class="link"></a>"""
        bs = to_bs(markup)
        tag = AndElementTag(ElementTag("a"), AttributeTag("class", "widget"))
        assert tag.find(bs) is None

    def test_find_returns_first_tag_that_matches_more_than_two_selectors(self):
        """
        Tests if find method returns the first tag that matches all the selectors.
        In this case testing for multiple selectors. For tag to be selected
        it must match all the selectors.
        """
        markup = """
            <a class="123"></a>
            <div><a class="widget 12"></a></div>
            <div class="123"></div>
            <a class="link"></a>
            <div class="link"></div>
        """
        bs = to_bs(markup)

        tag = AndElementTag(
            ElementTag("a"),
            AttributeTag("class", "1", re=True),
            StepsElementTag(ElementTag("div"), ElementTag("a")),
        )
        result = tag.find(bs)
        assert str(result) == strip("""<a class="widget 12"></a>""")

    def test_finds_all_tags_matching_selectors(self):
        """
        Tests if find_all method returns all tags that match all the selectors.
        """
        markup = """
            <a class="widget 12"></a>
            <div class="123"></div>
            <span class="empty"></span>
            <a class="link"></a>
            <div><a class="11"></a></div>
            <div class="link"></div>
            <a class="123"></a>
        """
        bs = to_bs(markup)

        tag = AndElementTag(ElementTag("a"), AttributeTag("class", "1", re=True))
        result = tag.find_all(bs)

        assert list(map(str, result)) == [
            strip("""<a class="widget 12"></a>"""),
            strip("""<a class="11"></a>"""),
            strip("""<a class="123"></a>"""),
        ]

    def test_find_all_returns_empty_list_if_no_tag_matches(self):
        """
        Tests if find_all method returns an empty list when no tag is found
        that matches all the selectors.
        """
        markup = """
            <a class="12"></a>
            <div class="widget"></div>
            <a class="link"></a>
            <span class="menu"></span>
        """
        bs = to_bs(markup)

        tag = AndElementTag(ElementTag("a"), AttributeTag("class", "widget"))
        result = tag.find_all(bs)
        assert result == []

    def test_bitwise_and_operator_returns_and_element_tag(self):
        """
        Tests if bitwise AND operator (__and__) returns AndElementTag instance
        with the same selectors.
        """
        tag1 = ElementTag("a")
        tag2 = AttributeTag("class", "link")
        intersection = tag1 & tag2
        assert isinstance(intersection, AndElementTag)
        assert intersection.steps == [tag1, tag2]

    def test_bitwise_and_operator_raises_exception_if_not_selectable_soup(self):
        """
        Tests if bitwise AND operator (__and__) raises TypeError
        when one of the operands is not SelectableSoup instance.
        """
        tag = ElementTag("a")

        with pytest.raises(TypeError):
            tag & "class"  # type: ignore
