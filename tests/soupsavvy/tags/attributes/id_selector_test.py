"""Testing module for IdSelector class."""

import re

import pytest

from soupsavvy.tags.attributes import IdSelector
from soupsavvy.tags.exceptions import TagNotFoundException
from tests.soupsavvy.tags.conftest import find_body_element, strip, to_bs


@pytest.mark.soup
class TestIdSelector:
    """Class for IdSelector unit test suite."""

    def test_find_returns_first_match_with_any_value(self):
        """
        Tests if find returns first tag with id attribute,
        when no value is specified.
        """
        markup = """
            <div href="widget"></div>
            <span></span>
            <div id=""></div>
        """
        bs = to_bs(markup)
        selector = IdSelector()
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<div id=""></div>""")

    def test_find_returns_first_match_with_specific_value(self):
        """Tests if find returns first tag with id attribute with specific value."""
        markup = """
            <div class="widget"></div>
            <span id="menu"></span>
            <a id="widget"></a>
        """
        bs = to_bs(markup)
        selector = IdSelector("widget")
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<a id="widget"></a>""")

    def test_find_returns_first_match_with_re_true(self):
        """
        Tests if find returns first tag with id attribute that contains
        specified value when re is set to True.
        """
        markup = """
            <div href="widget"></div>
            <span id="menu"></span>
            <div id="widget_menu"></div>
        """
        bs = to_bs(markup)
        selector = IdSelector(value="widget", re=True)
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<div id="widget_menu"></div>""")

    def test_find_returns_first_match_with_pattern(self):
        """
        Tests if find returns first tag with id attribute that matches
        specified regex pattern. Testing for passing both string and compiled
        regex pattern.
        """
        markup = """
            <div id="menu widget 12"></div>
            <span id="widget"></span>
            <div href="widget 12"></div>
            <div id="widget 123"></div>
        """
        bs = to_bs(markup)
        pattern = r"^widget.?\d{1,3}$"
        expected = strip("""<div id="widget 123"></div>""")

        selector = IdSelector(value=pattern, re=True)
        result = selector.find(bs)
        assert strip(str(result)) == expected

        # already compiled regex pattern should work the same way
        selector = IdSelector(value=re.compile(pattern))
        result = selector.find(bs)
        assert strip(str(result)) == expected

    def test_find_returns_none_if_no_match_and_strict_false(self):
        """
        Tests if find returns None if no element matches the selector
        and strict is False.
        """
        markup = """
            <div href="widget"></div>
            <span id=""></span>
            <div id="menu"></div>
        """
        bs = to_bs(markup)
        selector = IdSelector(value="widget")
        result = selector.find(bs)
        assert result is None

    def test_find_raises_exception_if_no_match_and_strict_true(self):
        """
        Tests find raises TagNotFoundException if no element matches the selector
        and strict is True.
        """
        markup = """
            <div href="widget"></div>
            <span id=""></span>
            <div id="menu"></div>
        """
        bs = to_bs(markup)
        selector = IdSelector(value="widget")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_all_returns_all_matching_elements(self):
        """Tests if find_all returns a list of all matching elements."""
        markup = """
            <div href="widget"></div>
            <div id="widget"></div>
            <span id=""></span>
            <div id="menu"></div>
            <a id="widget"></a>
            <div>
                <a id="widget">Hello</a>
            </div>
        """
        bs = to_bs(markup)
        selector = IdSelector(value="widget")

        result = selector.find_all(bs)
        excepted = [
            strip("""<div id="widget"></div>"""),
            strip("""<a id="widget"></a>"""),
            strip("""<a id="widget">Hello</a>"""),
        ]
        assert list(map(lambda x: strip(str(x)), result)) == excepted

    def test_find_all_returns_empty_list_when_no_match(self):
        """Tests if find returns an empty list if no element matches the selector."""
        markup = """
            <div href="widget"></div>
            <span id=""></span>
            <div id="menu"></div>
        """
        bs = to_bs(markup)
        selector = IdSelector(value="widget")
        result = selector.find_all(bs)
        assert result == []

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        markup = """
            <div>
                <a id="widget">Hello</a>
            </div>
            <div href="widget"></div>
            <div id="menu"></div>
            <a id="widget"></a>
        """
        bs = find_body_element(to_bs(markup))
        selector = IdSelector("widget")
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<a id="widget"></a>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        markup = """
            <div>
                <a id="widget">Hello</a>
            </div>
            <div href="widget"></div>
            <div id="menu"></div>
        """
        bs = find_body_element(to_bs(markup))
        selector = IdSelector("widget")
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        markup = """
            <div>
                <a id="widget">Hello</a>
            </div>
            <div href="widget"></div>
            <div id="menu"></div>
        """
        bs = find_body_element(to_bs(markup))
        selector = IdSelector("widget")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True, recursive=False)

    def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
        self,
    ):
        """
        Tests if find_all returns an empty list if no child element
        matches the selector and recursive is False.
        """
        markup = """
            <div>
                <a id="widget">Hello</a>
            </div>
            <div href="widget"></div>
            <div id="menu"></div>
        """
        bs = find_body_element(to_bs(markup))
        selector = IdSelector("widget")
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        markup = """
            <a id="widget"></a>
            <div>
                <a id="widget">Hello</a>
            </div>
            <div href="widget"></div>
            <div id="menu"></div>
            <div id="widget"></div>
            <span id=""></span>
            <div id="widget"></div>
        """
        bs = find_body_element(to_bs(markup))
        selector = IdSelector("widget")
        result = selector.find_all(bs, recursive=False)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a id="widget"></a>"""),
            strip("""<div id="widget"></div>"""),
            strip("""<div id="widget"></div>"""),
        ]

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        markup = """
            <a id="widget"></a>
            <div href="widget"></div>
            <div>
                <a id="widget">Hello</a>
            </div>
            <div id="menu"></div>
            <span id=""></span>
            <div id="widget"></div>
        """
        bs = find_body_element(to_bs(markup))
        selector = IdSelector("widget")
        result = selector.find_all(bs, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a id="widget"></a>"""),
            strip("""<a id="widget">Hello</a>"""),
        ]

    def test_find_all_returns_only_x_elements_when_limit_is_set_and_recursive_false(
        self,
    ):
        """
        Tests if find_all returns only x elements when limit is set and recursive
        is False. In this case only 2 first in order children matching
        the selector are returned.
        """
        markup = """
            <a id="widget"></a>
            <div href="widget"></div>
            <div>
                <a id="widget">Hello</a>
            </div>
            <div id="menu"></div>
            <div id="widget"></div>
            <span id=""></span>
            <span id="widget"></span>
        """
        bs = find_body_element(to_bs(markup))
        selector = IdSelector("widget")
        result = selector.find_all(bs, recursive=False, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a id="widget"></a>"""),
            strip("""<div id="widget"></div>"""),
        ]

    @pytest.mark.css_selector
    @pytest.mark.parametrize(
        argnames="selector, css",
        argvalues=[
            # id overrides default css selector with # syntax
            (IdSelector("menu"), "#menu"),
            # selector is constructed as default if re is True
            (IdSelector("menu", re=True), "[id*='menu']"),
            (IdSelector(re=True), "[id]"),
            (IdSelector(re=False), "[id]"),
            # pattern is reduced to containment operator *=
            (
                IdSelector(re.compile(r"^menu"), re=True),
                "[id*='^menu']",
            ),
            (
                IdSelector(re.compile(r"^menu"), re=False),
                "[id*='^menu']",
            ),
        ],
    )
    def test_selector_is_correct(self, selector: IdSelector, css: str):
        """Tests if css selector for AttributeSelector is constructed as expected."""
        assert selector.selector == css
