"""Testing module for IdSelector class."""

import re

import pytest

from soupsavvy.exceptions import TagNotFoundException
from soupsavvy.tags.attributes import IdSelector
from tests.soupsavvy.tags.conftest import find_body_element, strip, to_bs

#! in these tests there are examples where multiple elements have the same id
#! this is not a valid html, but it is used for testing purposes


@pytest.mark.soup
class TestIdSelector:
    """Class for IdSelector unit test suite."""

    def test_find_returns_first_match_with_any_value(self):
        """
        Tests if find returns first tag with id attribute,
        when no value is specified.
        """
        text = """
            <div href="widget"></div>
            <span></span>
            <div id=""></div>
            <div id="dog"></div>
        """
        bs = to_bs(text)
        selector = IdSelector()
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<div id=""></div>""")

    def test_find_returns_first_match_with_specific_value(self):
        """Tests if find returns first tag with id attribute with specific value."""
        # even though there should not be multiple elements with the same id
        text = """
            <div class="widget"></div>
            <span id="menu"></span>
            <a id="widget"></a>
            <div id="widget"></d>
        """
        bs = to_bs(text)
        selector = IdSelector("widget")
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<a id="widget"></a>""")

    def test_find_returns_first_match_with_re_true(self):
        """
        Tests if find returns first tag with id attribute that contains
        specified value when re is set to True.
        """
        text = """
            <div href="widget"></div>
            <span id="menu"></span>
            <div id="widget_menu"></div>
            <div id="widget_123"></div>
        """
        bs = to_bs(text)
        selector = IdSelector(value="widget", re=True)
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<div id="widget_menu"></div>""")

    def test_find_returns_first_match_with_pattern(self):
        """
        Tests if find returns first tag with id attribute that matches
        specified regex pattern. Testing for passing both string and compiled
        regex pattern.
        """
        text = """
            <div id="menu widget 12"></div>
            <span id="widget"></span>
            <div href="widget 12"></div>
            <div id="widget 123"></div>
            <div id="widget 45"></div>
        """
        bs = to_bs(text)
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
        text = """
            <div href="widget"></div>
            <span id=""></span>
            <div id="widget123"></div>
            <div id="menu"></div>
        """
        bs = to_bs(text)
        selector = IdSelector(value="widget")
        result = selector.find(bs)
        assert result is None

    def test_find_raises_exception_if_no_match_and_strict_true(self):
        """
        Tests find raises TagNotFoundException if no element matches the selector
        and strict is True.
        """
        text = """
            <div href="widget"></div>
            <span id=""></span>
            <div id="widget123"></div>
            <div id="menu"></div>
        """
        bs = to_bs(text)
        selector = IdSelector(value="widget")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_all_returns_all_matching_elements(self):
        """Tests if find_all returns a list of all matching elements."""
        text = """
            <div href="widget"></div>
            <div id="widget">1</div>
            <span id=""></span>
            <div id="menu"></div>
            <a id="widget">2</a>
            <div>
                <a id="widget">3</a>
            </div>
            <span class="widget"></span>
            <div id="widget"><span>4</span></div>
            <div id="widget123"></div>
        """
        bs = to_bs(text)
        selector = IdSelector(value="widget")

        result = selector.find_all(bs)
        excepted = [
            strip("""<div id="widget">1</div>"""),
            strip("""<a id="widget">2</a>"""),
            strip("""<a id="widget">3</a>"""),
            strip("""<div id="widget"><span>4</span></div>"""),
        ]
        assert list(map(lambda x: strip(str(x)), result)) == excepted

    def test_find_all_returns_empty_list_when_no_match(self):
        """Tests if find returns an empty list if no element matches the selector."""
        text = """
            <div href="widget"></div>
            <span id=""></span>
            <div id="menu"></div>
            <div id="widget123"></div>
        """
        bs = to_bs(text)
        selector = IdSelector(value="widget")
        result = selector.find_all(bs)
        assert result == []

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        text = """
            <div>
                <a id="widget">Hello</a>
            </div>
            <div href="widget"></div>
            <div id="menu"></div>
            <a id="widget"></a>
            <div id="widget"></div>
        """
        bs = find_body_element(to_bs(text))
        selector = IdSelector("widget")
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<a id="widget"></a>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div>
                <a id="widget">Not child</a>
            </div>
            <div href="widget"></div>
            <div id="widget123"></div>
            <div id="menu"></div>
        """
        bs = find_body_element(to_bs(text))
        selector = IdSelector("widget")
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <div>
                <a id="widget">Not child</a>
            </div>
            <div href="widget"></div>
            <div id="widget123"></div>
            <div id="menu"></div>
        """
        bs = find_body_element(to_bs(text))
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
        text = """
            <div>
                <a id="widget">Hello</a>
            </div>
            <div href="widget"></div>
            <div id="widget123"></div>
            <div id="menu"></div>
        """
        bs = find_body_element(to_bs(text))
        selector = IdSelector("widget")
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <a id="widget">1</a>
            <div>
                <a id="widget">Hello</a>
            </div>
            <div href="widget"></div>
            <div id="menu"></div>
            <div id="widget">2</div>
            <span id=""></span>
            <div id="widget">3</div>
            <span class="widget"></span>
            <div id="widget"><span>4</span></div>
        """
        bs = find_body_element(to_bs(text))
        selector = IdSelector("widget")
        result = selector.find_all(bs, recursive=False)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a id="widget">1</a>"""),
            strip("""<div id="widget">2</div>"""),
            strip("""<div id="widget">3</div>"""),
            strip("""<div id="widget"><span>4</span></div>"""),
        ]

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <a id="widget">1</a>
            <div href="widget"></div>
            <div>
                <a id="widget">2</a>
            </div>
            <div id="menu"></div>
            <div id="widget">3</div>
            <span id=""></span>
        """
        bs = find_body_element(to_bs(text))
        selector = IdSelector("widget")
        result = selector.find_all(bs, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a id="widget">1</a>"""),
            strip("""<a id="widget">2</a>"""),
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
            <a id="widget">1</a>
            <div href="widget"></div>
            <div>
                <a id="widget">Not child</a>
            </div>
            <div id="menu"></div>
            <div id="widget">2</div>
            <span id=""></span>
            <span id="widget">3</span>
        """
        bs = find_body_element(to_bs(text))
        selector = IdSelector("widget")
        result = selector.find_all(bs, recursive=False, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a id="widget">1</a>"""),
            strip("""<div id="widget">2</div>"""),
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
