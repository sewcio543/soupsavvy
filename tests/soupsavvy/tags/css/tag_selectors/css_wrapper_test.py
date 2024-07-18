"""
Module with unit tests for CSS selector, which is a wrapped
for css selector-based search.
"""

import pytest

from soupsavvy.exceptions import TagNotFoundException
from soupsavvy.tags.css.tag_selectors import CSS
from tests.soupsavvy.tags.conftest import find_body_element, strip, to_bs


@pytest.mark.css_selector
@pytest.mark.soup
class TestCSS:
    """
    Class with unit tests for CSS tag selector.
    Idea for the tests is to check cases for simple selector, css search is delegated
    to `soupsieve` library.
    """

    @pytest.mark.parametrize(
        argnames="css",
        argvalues=[
            ":not(div.menu, a)",
            "div",
            # invalid attrs do not raise exceptions in the constructor
            ":nth-attr(2n+1)",
        ],
    )
    def test_selector_attribute_is_equal_to_init_param(self, css: str):
        """
        Tests if selector property returns the same value
        as string passed to the constructor.
        """
        assert CSS(css).selector == css

    def test_find_returns_first_tag_matching_selector(self):
        """Tests if find method returns first tag matching selector."""
        text = """
            <div></div>
            <div class="widget123"></div>
            <a class="widget"></a>
            <div class="widget">1</div>
            <span>
                <div id="widget"></div>
                <div class="widget">2</div>
            </span>
            <div class="widget"><p>3</p></div>
        """
        bs = to_bs(text)
        selector = CSS("div.widget")
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<div class="widget">1</div>""")

    def test_find_returns_none_if_no_match_and_strict_false(self):
        """
        Tests if find returns None if no element matches the selector
        and strict is False.
        """
        text = """
            <div></div>
            <div class="widget123"></div>
            <a class="widget"></a>
            <span>
                <div id="widget"></div>
            </span>
            <span class="widget"></span>
        """
        bs = to_bs(text)
        selector = CSS("div.widget")
        result = selector.find(bs)
        assert result is None

    def test_find_raises_exception_if_no_match_and_strict_true(self):
        """
        Tests if find raises TagNotFoundException if no element matches the selector
        and strict is True.
        """
        text = """
            <div></div>
            <div class="widget123"></div>
            <a class="widget"></a>
            <span>
                <div id="widget"></div>
            </span>
            <span class="widget"></span>
        """
        bs = to_bs(text)
        selector = CSS("div.widget")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_all_returns_all_matching_elements(self):
        """Tests if find_all returns a list of all matching elements."""
        text = """
            <div></div>
            <div class="widget123"></div>
            <a class="widget"></a>
            <div class="widget">1</div>
            <span>
                <div id="widget"></div>
                <div class="widget">2</div>
            </span>
            <div class="widget"><p>3</p></div>
        """
        bs = to_bs(text)
        selector = CSS("div.widget")

        result = selector.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div class="widget">1</div>"""),
            strip("""<div class="widget">2</div>"""),
            strip("""<div class="widget"><p>3</p></div>"""),
        ]

    def test_find_all_returns_empty_list_when_no_match(self):
        """Tests if find returns an CSS list if no element matches the selector."""
        text = """
            <div></div>
            <div class="widget123"></div>
            <a class="widget"></a>
            <span>
                <div id="widget"></div>
            </span>
            <span class="widget"></span>
        """
        bs = to_bs(text)
        selector = CSS("div.widget")
        result = selector.find_all(bs)
        assert result == []

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        text = """
            <div></div>
            <span>
                <div id="widget"></div>
                <div class="widget">Not child</div>
            </span>
            <div class="widget">1</div>
            <a class="widget"></a>
            <div class="widget"><p>2</p></div>
            <div class="widget123"></div>
            <div class="widget" href="github">3</div>
        """
        bs = find_body_element(to_bs(text))
        selector = CSS("div.widget")
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<div class="widget">1</div>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div></div>
            <span>
                <div id="widget"></div>
                <div class="widget">Not child</div>
            </span>
            <a class="widget"></a>
            <div class="widget123"></div>
        """
        bs = find_body_element(to_bs(text))
        selector = CSS("div.widget")
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <div></div>
            <span>
                <div id="widget"></div>
                <div class="widget">Not child</div>
            </span>
            <a class="widget"></a>
            <div class="widget123"></div>
        """
        bs = find_body_element(to_bs(text))
        selector = CSS("div.widget")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True, recursive=False)

    def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
        self,
    ):
        """
        Tests if find_all returns an CSS list if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div></div>
            <span>
                <div id="widget"></div>
                <div class="widget">Not child</div>
            </span>
            <a class="widget"></a>
            <div class="widget123"></div>
        """
        bs = find_body_element(to_bs(text))
        selector = CSS("div.widget")
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <div></div>
            <span>
                <div id="widget"></div>
                <div class="widget">Not child</div>
            </span>
            <div class="widget">1</div>
            <a class="widget"></a>
            <div class="widget"><p>2</p></div>
            <div class="widget123"></div>
            <div class="widget" href="github">3</div>
        """
        bs = find_body_element(to_bs(text))
        selector = CSS("div.widget")
        result = selector.find_all(bs, recursive=False)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div class="widget">1</div>"""),
            strip("""<div class="widget"><p>2</p></div>"""),
            strip("""<div class="widget" href="github">3</div>"""),
        ]

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <div></div>
            <div class="widget123"></div>
            <a class="widget"></a>
            <div class="widget">1</div>
            <span>
                <div id="widget"></div>
                <div class="widget">2</div>
            </span>
            <div class="widget"><p>3</p></div>
        """
        bs = find_body_element(to_bs(text))
        selector = CSS("div.widget")
        result = selector.find_all(bs, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div class="widget">1</div>"""),
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
            <div></div>
            <span>
                <div id="widget"></div>
                <div class="widget">Not child</div>
            </span>
            <div class="widget">1</div>
            <a class="widget"></a>
            <div class="widget"><p>2</p></div>
            <div class="widget123"></div>
            <div class="widget" href="github">3</div>
        """
        bs = find_body_element(to_bs(text))
        selector = CSS("div.widget")
        result = selector.find_all(bs, recursive=False, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div class="widget">1</div>"""),
            strip("""<div class="widget"><p>2</p></div>"""),
        ]
