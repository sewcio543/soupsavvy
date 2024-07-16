"""Testing module for AnyTagSelector class."""

import pytest
from bs4 import Tag

from soupsavvy.tags.components import AnyTagSelector, TagSelector
from soupsavvy.tags.exceptions import TagNotFoundException
from soupsavvy.tags.namespace import CSS_SELECTOR_WILDCARD
from tests.soupsavvy.tags.conftest import find_body_element, strip, to_bs


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
class TestAnyTagSelector:
    """Class for AnyTagSelector unit test suite."""

    @pytest.fixture(scope="class")
    def selector(self) -> AnyTagSelector:
        """
        Fixture for AnyTagSelector instance. Since there are no parameters
        for AnyTagSelector, it does not make sense to create it in each test.
        """
        return AnyTagSelector()

    def test_find_returns_first_tag_matching_selector(self, selector: AnyTagSelector):
        """Tests if find method returns the first tag that matches selector."""
        text = """
            <a class="widget">1</a>
            <div><a>23</a></div>
            <p>4</p>
        """
        bs = find_body_element(to_bs(text))
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<a class="widget">1</a>""")

    def test_find_raises_exception_when_no_tags_match_in_strict_mode(
        self, selector: AnyTagSelector
    ):
        """
        Tests if find method raises TagNotFoundException when no tag is found
        that matches selector in strict mode.
        """
        text = """
            <a class="widget"></a>
            <div><p></p></div>
        """
        bs = find_tag(to_bs(text), name="a")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_returns_none_if_no_tags_match_in_not_strict_mode(
        self, selector: AnyTagSelector
    ):
        """
        Tests if find method returns None when no tag is found that
        matches selector in not strict mode.
        """
        text = """
            <a class="widget"></a>
            <div><p></p></div>
        """
        bs = find_tag(to_bs(text), name="a")
        result = selector.find(bs)
        assert result is None

    def test_finds_all_tags_matching_selectors(self, selector: AnyTagSelector):
        """Tests if find_all method returns all tags that match selector."""
        text = """
            <a class="widget">1</a>
            <div><a>23</a></div>
            <p>4</p>
        """
        bs = find_body_element(to_bs(text))
        result = selector.find_all(bs)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="widget">1</a>"""),
            strip("""<div><a>23</a></div>"""),
            strip("""<a>23</a>"""),
            strip("""<p>4</p>"""),
        ]

    def test_find_all_returns_empty_list_if_no_tag_matches(
        self, selector: AnyTagSelector
    ):
        """
        Tests if find_all method returns an empty list when no tag is found
        that matches selector.
        """
        text = """
            <a class="widget"></a>
            <div><p></p></div>
        """
        bs = find_tag(to_bs(text), name="a")
        assert selector.find_all(bs) == []

    def test_find_returns_first_matching_child_if_recursive_false(
        self, selector: AnyTagSelector
    ):
        """
        Tests if find returns first matching child element if recursive is False.
        For AnyTagSelector it doesn't matter if recursive is True or False, it always
        returns first element.
        """
        text = """
            <a class="widget">1</a>
            <div><a>23</a></div>
            <p>4</p>
        """
        bs = find_body_element(to_bs(text))
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<a class="widget">1</a>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(
        self, selector: AnyTagSelector
    ):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <a class="widget"></a>
            <div><p></p></div>
        """
        bs = find_tag(to_bs(text), name="a")
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(
        self, selector: AnyTagSelector
    ):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <a class="widget"></a>
            <div><p></p></div>
        """
        bs = find_tag(to_bs(text), name="a")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True, recursive=False)

    def test_find_all_returns_all_matching_children_when_recursive_false(
        self, selector: AnyTagSelector
    ):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <div><a></a><p><span>1</span></p></div>
            <a class="widget">2</a>
            <p>3</p>
        """
        bs = find_body_element(to_bs(text))
        result = selector.find_all(bs, recursive=False)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div><a></a><p><span>1</span></p></div>"""),
            strip("""<a class="widget">2</a>"""),
            strip("""<p>3</p>"""),
        ]

    def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
        self, selector: AnyTagSelector
    ):
        """
        Tests if find_all returns an empty list if no child element matches the selector
        and recursive is False.
        """
        text = """
            <a class="widget"></a>
            <div><p></p></div>
        """
        bs = find_tag(to_bs(text), name="a")
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_only_x_elements_when_limit_is_set(
        self, selector: AnyTagSelector
    ):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <a class="widget">1</a>
            <div><a>23</a></div>
            <p>4</p>
        """
        bs = find_body_element(to_bs(text))
        result = selector.find_all(bs, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="widget">1</a>"""),
            strip("""<div><a>23</a></div>"""),
        ]

    def test_find_all_returns_only_x_elements_when_limit_is_set_and_recursive_false(
        self, selector: AnyTagSelector
    ):
        """
        Tests if find_all returns only x elements when limit is set and recursive
        is False. In this case only 2 first in order children matching
        the selector are returned.
        """
        text = """
            <div><a></a><p><span>1</span></p></div>
            <a class="widget">2</a>
            <p>3</p>
        """
        bs = find_body_element(to_bs(text))
        result = selector.find_all(bs, recursive=False, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div><a></a><p><span>1</span></p></div>"""),
            strip("""<a class="widget">2</a>"""),
        ]

    @pytest.mark.css_selector
    def test_selector_is_a_css_selector_wildcard(self, selector: AnyTagSelector):
        """Test if selector attribute is a css selector wildcard."""
        assert selector.selector == CSS_SELECTOR_WILDCARD

    @pytest.mark.parametrize(
        argnames="selectors",
        argvalues=[
            # Two AnyTagSelectors
            (AnyTagSelector(), AnyTagSelector()),
            # AnyTagSelector and empty TagSelector
            (AnyTagSelector(), TagSelector()),
        ],
    )
    def test_two_selectors_are_equal(
        self, selectors: tuple[AnyTagSelector, AnyTagSelector]
    ):
        """Tests if two selectors are equal."""
        assert (selectors[0] == selectors[1]) is True

    def test_two_selectors_are_not_equal(self):
        """
        Tests if two selectors are not equal. In case of AnyTagSelector,
        any other selector that is not AnyTagSelector or empty TagSelector
        is not equal to it.
        """
        assert AnyTagSelector() != TagSelector("div")
