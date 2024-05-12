"""Testing module for AnyTag class."""

import pytest
from bs4 import Tag

from soupsavvy.tags.components import AnyTag
from soupsavvy.tags.exceptions import TagNotFoundException
from soupsavvy.tags.namespace import CSS_SELECTOR_WILDCARD

from .conftest import find_body_element, strip, to_bs


def find_tag(bs: Tag, name: str = "body") -> Tag:
    """
    Helper function to find tag in bs4 object.

    Parameters
    ----------
    bs : Tag
        bs4 object to search for tag.
    name : str
        Tag name to search for, default is "body".
    """
    return bs.find(name)  # type: ignore


@pytest.mark.soup
class TestAnyTag:
    """Class for AnyTag unit test suite."""

    @pytest.fixture(scope="class")
    def tag(self) -> AnyTag:
        """Fixture for AnyTag instance."""
        return AnyTag()

    def test_find_extracts_first_tag_when_there_is_only_one(self, tag: AnyTag):
        """Test if first tag is extracted when there is only one tag."""
        markup = """<a class="widget"></a>"""
        bs = find_tag(to_bs(markup))
        result = tag.find(bs)
        assert str(result) == strip(markup)

    def test_find_extracts_first_tag_when_there_are_many(self, tag: AnyTag):
        """Test if first tag is extracted when there are many tags."""
        markup = """<a class="widget"></a><a class="widget_2"></a>"""
        bs = find_tag(to_bs(markup))
        result = tag.find(bs)
        assert str(result) == strip("""<a class="widget"></a>""")

    def test_find_extracts_first_tag_parent_tag(self, tag: AnyTag):
        """Test if first tag is extracted if it is parent tag with children tags."""
        markup = """
            <div><a class="widget"></a></div>
            <div><a class="widget_2"></a></div>
        """
        bs = find_tag(to_bs(markup))
        result = tag.find(bs)
        assert str(result) == strip("""<div><a class="widget"></a></div>""")

    def test_find_all_extracts_all_tags(self, tag: AnyTag):
        """
        Test if all tags are extracted by find_all method,
        no matter if they are nested or in the root.
        """
        markup = """
            <div><a class="widget"></a></div>
            <div><a class="widget_2"></a></div>
        """
        bs = find_tag(to_bs(markup))
        result = tag.find_all(bs)
        expected = [
            strip("""<div><a class="widget"></a></div>"""),
            strip("""<a class="widget"></a>"""),
            strip("""<div><a class="widget_2"></a></div>"""),
            strip("""<a class="widget_2"></a>"""),
        ]
        assert list(map(str, result)) == expected

    def test_find_returns_none_if_there_are_no_child_tags(self, tag: AnyTag):
        """Test if None is returned when there are no child tags in bs4 object."""
        markup = """<a class="widget"></a>"""
        bs = find_tag(to_bs(markup), name="a")
        result = tag.find(bs)
        assert result is None

    def test_find_raises_exception_if_strict_mode_and_no_child_tags(self, tag: AnyTag):
        """
        Test if exception is raised when there are no child tags in bs4 object
        and strict mode is on.
        """
        markup = """<a class="widget"></a>"""
        bs = find_tag(to_bs(markup), name="a")

        with pytest.raises(TagNotFoundException):
            tag.find(bs, strict=True)

    def test_find_all_returns_empty_list_if_no_child_tags(self, tag: AnyTag):
        """Test if empty list is returned when there are no child tags in bs4 object."""
        markup = """<a class="widget"></a>"""
        bs = find_tag(to_bs(markup), name="a")
        assert tag.find_all(bs) == []

    @pytest.mark.css_selector
    def test_selector_is_a_css_selector_wildcard(self, tag: AnyTag):
        """Test if selector attribute is a css selector wildcard."""
        assert tag.selector == CSS_SELECTOR_WILDCARD

    def test_find_returns_first_child_if_recursive_false(self, tag: AnyTag):
        """
        Tests if find returns first matching child element if recursive is False.
        For AnyTag it doesn't matter if recursive is True or False, it always
        returns first element.
        """
        markup = """<a class="widget"></a><a class="widget_2"></a>"""
        bs = find_tag(to_bs(markup))
        result = tag.find(bs, recursive=False)
        assert str(result) == strip("""<a class="widget"></a>""")

    def test_find_all_returns_all_children_when_recursive_false(self, tag: AnyTag):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns all children of the body element, but not nested children.
        """
        text = """
            <div><a>Hello 1</a></div>
            <a class="link">Hello 2</a>
            <div class="google"><span>Hello</span></div>
            <a>Hello 3</a>
        """
        bs = find_body_element(to_bs(text))
        results = tag.find_all(bs, recursive=False)

        assert list(map(str, results)) == [
            strip("""<div><a>Hello 1</a></div>"""),
            strip("""<a class="link">Hello 2</a>"""),
            strip("""<div class="google"><span>Hello</span></div>"""),
            strip("""<a>Hello 3</a>"""),
        ]

    def test_find_all_returns_only_x_elements_when_limit_is_set(self, tag: AnyTag):
        """
        Tests if find_all returns only x elements when limit is set.
        Always first in order elements are returned.
        """
        text = """
            <div>Hello 1</div>
            <div>Hello 2</div>
            <div>Hello 3</div>
            <div>Hello 4</div>
        """
        bs = find_body_element(to_bs(text))
        results = tag.find_all(bs, limit=2)

        assert list(map(str, results)) == [
            strip("""<div>Hello 1</div>"""),
            strip("""<div>Hello 2</div>"""),
        ]
