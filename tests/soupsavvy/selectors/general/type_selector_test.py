"""Testing module for TypeSelector class."""

import pytest

from soupsavvy.exceptions import TagNotFoundException
from soupsavvy.selectors.general import TypeSelector
from tests.soupsavvy.selectors.conftest import (
    MockLinkSelector,
    find_body_element,
    strip,
    to_bs,
)


@pytest.mark.selector
class TestTypeSelector:
    """Class for TypeSelector unit test suite."""

    def test_find_returns_first_tag_matching_selector(self):
        """Tests if find method returns first tag matching selector."""
        text = """
            <div href="github"></div>
            <h1 class="widget">1</h1>
            <h1><p>2</p></h1>
            <span>
                <h1>3</h1>
            </span>
        """
        bs = to_bs(text)
        selector = TypeSelector("h1")
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<h1 class="widget">1</h1>""")

    def test_find_returns_none_if_no_match_and_strict_false(self):
        """
        Tests if find returns None if no element matches the selector
        and strict is False.
        """
        text = """
            <div href="github"></div>
            <span class="widget"></span>
            <div><p>Hello</p></div>
            <span>
                <div>Hello</div>
            </span>
        """
        bs = to_bs(text)
        selector = TypeSelector("a")
        result = selector.find(bs)
        assert result is None

    def test_find_raises_exception_if_no_match_and_strict_true(self):
        """
        Tests if find raises TagNotFoundException if no element matches the selector
        and strict is True.
        """
        text = """
            <div href="github"></div>
            <span class="widget"></span>
            <div><p>Hello</p></div>
            <span>
                <div>Hello</div>
            </span>
        """
        bs = to_bs(text)
        selector = TypeSelector("a")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_all_returns_empty_list_when_no_match(self):
        """Tests if find returns an empty list if no element matches the selector."""
        text = """
            <div href="github"></div>
            <span class="widget"></span>
            <div><p>Hello</p></div>
            <span>
                <div>Hello</div>
            </span>
        """
        bs = to_bs(text)
        selector = TypeSelector("a")
        result = selector.find_all(bs)
        assert result == []

    def test_find_all_returns_all_matching_elements(self):
        """Tests if find_all returns a list of all matching elements."""
        text = """
            <div href="github"></div>
            <a class="widget">1</a>
            <a><p>2</p></a>
            <span>
                <a>3</a>
            </span>
        """
        bs = to_bs(text)
        selector = TypeSelector("a")
        result = selector.find_all(bs)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="widget">1</a>"""),
            strip("""<a><p>2</p></a>"""),
            strip("""<a>3</a>"""),
        ]

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        text = """
            <div class="google">
                <a href="github">Not child</a>
            </div>
            <a href="github">1</a>
            <div><a>Not child</a></div>
            <a><p>2</p></a>
            <span>Hello</span>
            <a>3</a>
        """
        bs = find_body_element(to_bs(text))
        selector = TypeSelector("a")
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<a href="github">1</a>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div class="google">
                <a href="github">Not child</a>
            </div>
            <div><a>Not child</a></div>
            <span>Hello</span>
        """
        bs = find_body_element(to_bs(text))
        selector = TypeSelector("a")
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <div class="google">
                <a href="github">Not child</a>
            </div>
            <div><a>Not child</a></div>
            <span>Hello</span>
        """
        bs = find_body_element(to_bs(text))
        selector = TypeSelector("a")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True, recursive=False)

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <div class="google">
                <a href="github">Not child</a>
            </div>
            <a href="github">1</a>
            <div><a>Not child</a></div>
            <a><p>2</p></a>
            <span>Hello</span>
            <a>3</a>
        """
        bs = find_body_element(to_bs(text))
        selector = TypeSelector("a")
        result = selector.find_all(bs, recursive=False)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a href="github">1</a>"""),
            strip("""<a><p>2</p></a>"""),
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
            <div class="google">
                <a href="github">Not child</a>
            </div>
            <div><a>Not child</a></div>
            <span>Hello</span>
        """
        bs = find_body_element(to_bs(text))
        selector = TypeSelector("a")
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <div href="github"></div>
            <a class="widget">1</a>
            <a><p>2</p></a>
            <span>
                <a>3</a>
            </span>
        """
        bs = find_body_element(to_bs(text))
        selector = TypeSelector("a")
        result = selector.find_all(bs, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="widget">1</a>"""),
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
            <div class="google">
                <a href="github">Not child</a>
            </div>
            <a href="github">1</a>
            <div><a>Not child</a></div>
            <a><p>2</p></a>
            <span>Hello</span>
            <a>3</a>
        """
        bs = find_body_element(to_bs(text))
        selector = TypeSelector("a")
        result = selector.find_all(bs, recursive=False, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a href="github">1</a>"""),
            strip("""<a><p>2</p></a>"""),
        ]

    @pytest.mark.parametrize(
        argnames="selectors",
        argvalues=[
            # tag names must be equal
            (TypeSelector("a"), TypeSelector("a")),
        ],
    )
    def test_two_tag_selectors_are_equal(self, selectors: tuple):
        """Tests if selector is equal to TypeSelector."""
        assert (selectors[0] == selectors[1]) is True

    @pytest.mark.parametrize(
        argnames="selectors",
        argvalues=[
            # tags are different
            (TypeSelector("a"), TypeSelector("div")),
            # not TypeSelector instance
            (TypeSelector("a"), MockLinkSelector()),
        ],
    )
    def test_two_tag_selectors_are_not_equal(self, selectors: tuple):
        """Tests if selector is equal to TypeSelector."""
        assert (selectors[0] == selectors[1]) is False

    @pytest.mark.parametrize(
        argnames="name",
        argvalues=["div", "p", "some_other_random"],
    )
    def test_returns_correct_css_selector(self, name: str):
        """Tests if css property always returns name of the tag as css selector."""
        assert TypeSelector(name).css == name
