"""Testing module for ClassSelector class."""

import re

import pytest

from soupsavvy.tags.attributes import ClassSelector
from soupsavvy.tags.exceptions import TagNotFoundException
from tests.soupsavvy.tags.conftest import find_body_element, strip, to_bs


@pytest.mark.soup
class TestClassSelector:
    """Class for ClassSelector unit test suite."""

    @pytest.mark.edge_case
    def test_find_matches_element_with_list_of_classes_if_one_matches(self):
        """
        Tests if find returns first tag with that has a list of classes
        and one of them matches the value.

        Example
        -------
        >>> <div class="menu widget"></div>

        In this case, the tag has two classes 'menu' and 'widget'.
        If selector looks for 'widget' or 'menu' class, it should match.
        """
        markup = """
            <div href="menu"></div>
            <div class="widget_class menu"></div>
            <div class="it has a long list of widget classes"></div>
        """
        bs = to_bs(markup)
        selector = ClassSelector("widget")
        result = selector.find(bs)
        assert str(result) == strip(
            """<div class="it has a long list of widget classes"></div>"""
        )

    def test_find_returns_first_match_with_any_value(self):
        """
        Tests if find returns first tag with class attribute,
        when no value is specified.
        """
        markup = """
            <div href="widget"></div>
            <span></span>
            <div class=""></div>
        """
        bs = to_bs(markup)
        selector = ClassSelector()
        result = selector.find(bs)
        assert str(result) == strip("""<div class=""></div>""")

    def test_find_returns_first_match_with_specific_value(self):
        """Tests if find returns first tag with class attribute with specific value."""
        markup = """
            <div href="widget"></div>
            <span class=""></span>
            <div class="menu"></div>
            <a class="widget"></a>
        """
        bs = to_bs(markup)
        selector = ClassSelector("widget")
        result = selector.find(bs)
        assert str(result) == strip("""<a class="widget"></a>""")

    def test_find_returns_first_match_with_re_true(self):
        """
        Tests if find returns first tag with class attribute that contains
        specified value when re is set to True.
        """
        markup = """
            <div href="widget"></div>
            <span class="menu"></span>
            <div class="widget_menu"></div>
        """
        bs = to_bs(markup)
        selector = ClassSelector("widget", re=True)
        result = selector.find(bs)
        assert str(result) == strip("""<div class="widget_menu"></div>""")

    def test_find_returns_first_match_with_pattern(self):
        """
        Tests if find returns first tag with class attribute that matches
        specified regex pattern. Testing for passing both string and compiled
        regex pattern.
        """
        markup = """
            <div class="menu widget 12"></div>
            <span class="widget"></span>
            <div href="widget 12"></div>
            <div class="widget 123"></div>
        """
        bs = to_bs(markup)
        pattern = r"^widget.?\d{1,3}$"
        expected = strip("""<div class="widget 123"></div>""")

        selector = ClassSelector(value=pattern, re=True)
        result = selector.find(bs)
        assert str(result) == expected

        # already compiled regex pattern should work the same way
        selector = ClassSelector(value=re.compile(pattern))
        result = selector.find(bs)
        assert str(result) == expected

    def test_find_returns_none_if_no_match_and_strict_false(self):
        """
        Tests if find returns None if no element matches the selector
        and strict is False.
        """
        markup = """
            <div href="widget"></div>
            <span class=""></span>
            <div class="menu"></div>
        """
        bs = to_bs(markup)
        selector = ClassSelector("widget")
        result = selector.find(bs)
        assert result is None

    def test_find_raises_exception_if_no_match_and_strict_true(self):
        """
        Tests find raises TagNotFoundException if no element matches the selector
        and strict is True.
        """
        markup = """
            <div href="widget"></div>
            <span class=""></span>
            <div class="menu"></div>
        """
        bs = to_bs(markup)
        selector = ClassSelector("widget")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_all_returns_all_matching_elements(self):
        """Tests if find_all returns a list of all matching elements."""
        markup = """
            <div href="widget"></div>
            <div class="widget"></div>
            <span class=""></span>
            <div class="menu"></div>
            <a class="widget"></a>
            <div>
                <a class="widget">Hello</a>
            </div>
        """
        bs = to_bs(markup)
        selector = ClassSelector("widget")

        result = selector.find_all(bs)
        excepted = [
            strip("""<div class="widget"></div>"""),
            strip("""<a class="widget"></a>"""),
            strip("""<a class="widget">Hello</a>"""),
        ]
        assert list(map(str, result)) == excepted

    def test_find_all_returns_empty_list_when_no_match(self):
        """Tests if find returns an empty list if no element matches the selector."""
        markup = """
            <div href="widget"></div>
            <span class=""></span>
            <div class="menu"></div>
        """
        bs = to_bs(markup)
        selector = ClassSelector("widget")
        result = selector.find_all(bs)
        assert result == []

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        markup = """
            <div>
                <a class="widget">Hello</a>
            </div>
            <div href="widget"></div>
            <div class="menu"></div>
            <a class="widget"></a>
        """
        bs = find_body_element(to_bs(markup))
        selector = ClassSelector("widget")
        result = selector.find(bs, recursive=False)
        assert str(result) == strip("""<a class="widget"></a>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        markup = """
            <div>
                <a class="widget">Hello</a>
            </div>
            <div href="widget"></div>
            <div class="menu"></div>
        """
        bs = find_body_element(to_bs(markup))
        selector = ClassSelector("widget")
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        markup = """
            <div>
                <a class="widget">Hello</a>
            </div>
            <div href="widget"></div>
            <div class="menu"></div>
        """
        bs = find_body_element(to_bs(markup))
        selector = ClassSelector("widget")

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
                <a class="widget">Hello</a>
            </div>
            <div href="widget"></div>
            <div class="menu"></div>
        """
        bs = find_body_element(to_bs(markup))
        selector = ClassSelector("widget")
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        markup = """
            <a class="widget" href="menu"></a>
            <div>
                <a class="widget">Hello</a>
            </div>
            <div href="widget"></div>
            <div class="menu"></div>
            <div class="widget"></div>
            <span class=""></span>
            <div class="widget"></div>
        """
        bs = find_body_element(to_bs(markup))
        selector = ClassSelector("widget")
        result = selector.find_all(bs, recursive=False)

        assert list(map(str, result)) == [
            strip("""<a class="widget" href="menu"></a>"""),
            strip("""<div class="widget"></div>"""),
            strip("""<div class="widget"></div>"""),
        ]

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        markup = """
            <a class="widget" href="menu"></a>
            <div href="widget"></div>
            <div>
                <a class="widget">Hello</a>
            </div>
            <div class="menu"></div>
            <span class=""></span>
            <div class="widget"></div>
        """
        bs = find_body_element(to_bs(markup))
        selector = ClassSelector("widget")
        result = selector.find_all(bs, limit=2)

        assert list(map(str, result)) == [
            strip("""<a class="widget" href="menu"></a>"""),
            strip("""<a class="widget">Hello</a>"""),
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
            <a class="widget" href="menu"></a>
            <div href="widget"></div>
            <div>
                <a class="widget">Hello</a>
            </div>
            <div class="menu"></div>
            <div class="widget"></div>
            <span class=""></span>
            <span class="widget"></span>
        """
        bs = find_body_element(to_bs(markup))
        selector = ClassSelector("widget")
        result = selector.find_all(bs, recursive=False, limit=2)

        assert list(map(str, result)) == [
            strip("""<a class="widget" href="menu"></a>"""),
            strip("""<div class="widget"></div>"""),
        ]

    @pytest.mark.css_selector
    @pytest.mark.parametrize(
        argnames="selector, css",
        argvalues=[
            # class overrides default css selector with . syntax
            (ClassSelector("menu"), ".menu"),
            # selector is constructed as default if re is True
            (ClassSelector("menu", re=True), "[class*='menu']"),
            (ClassSelector(re=True), "[class]"),
            (ClassSelector(re=False), "[class]"),
            # pattern is reduced to containment operator *=
            (
                ClassSelector(re.compile(r"^menu"), re=True),
                "[class*='^menu']",
            ),
            (
                ClassSelector(re.compile(r"^menu"), re=False),
                "[class*='^menu']",
            ),
        ],
    )
    def test_selector_is_correct(self, selector: ClassSelector, css: str):
        """Tests if css selector for AttributeSelector is constructed as expected."""
        assert selector.selector == css
