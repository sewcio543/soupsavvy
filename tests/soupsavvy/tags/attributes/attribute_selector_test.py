"""Testing module for AttributeSelector class."""

import re

import pytest

from soupsavvy.tags.attributes import AttributeSelector, ClassSelector
from soupsavvy.tags.exceptions import TagNotFoundException
from tests.soupsavvy.tags.conftest import (
    MockDivSelector,
    find_body_element,
    strip,
    to_bs,
)


@pytest.mark.soup
class TestAttributeSelector:
    """Class for AttributeSelector unit test suite."""

    def test_find_returns_first_matching_tag_with_specific_attribute(self):
        """Tests if find method returns first matching tag with specific attribute."""
        text = """
            <div href="github"></div>
            <a></a>
            <a class="widget"></a>
        """
        bs = to_bs(text)
        selector = AttributeSelector(name="class")
        result = selector.find(bs)
        assert str(result) == strip("""<a class="widget"></a>""")

    def test_find_returns_first_matching_tag_with_exact_attribute_value(self):
        """
        Tests if find method returns first matching tag with exact attribute value.
        """
        text = """
            <div href="github" class="menu"></div>
            <a></a>
            <span class="widgets"></span>
            <a class="widget"></a>
        """
        bs = to_bs(text)
        selector = AttributeSelector(name="class", value="widget")
        result = selector.find(bs)
        assert str(result) == strip("""<a class="widget"></a>""")

    @pytest.mark.parametrize(
        argnames="selector",
        argvalues=[
            AttributeSelector(name="class", value="^widget", re=True),
            # re parameter is ignored if value is compiled pattern
            AttributeSelector(name="class", value=re.compile("^widget"), re=False),
            AttributeSelector(name="class", value=re.compile("^widget"), re=True),
        ],
    )
    def test_find_returns_first_matching_tag_with_regex(
        self, selector: AttributeSelector
    ):
        """
        Tests if find method returns first matching tag with regex pattern.
        Selector should behave the same way when value is compiled regex pattern
        and when value is string pattern with re parameter set to True.

        """
        text = """
            <div href="github" class="menu"></div>
            <a></a>
            <span class="super_widget"></span>
            <a class="wid__get"></a>
            <span class="widget_123"></span>
        """
        bs = to_bs(text)
        result = selector.find(bs)
        assert str(result) == strip("""<span class="widget_123"></span>""")

    def test_find_returns_none_if_no_match_and_strict_false(self):
        """
        Tests if find returns None if no element matches the selector
        and strict is False.
        """
        text = """
            <div href="github" class="menu"></div>
            <a></a>
            <span class="widgets"></span>
            <a class="super_widget"></a>
            <a class="widget_2"></a>
        """
        bs = to_bs(text)
        selector = AttributeSelector(name="class", value="widget")
        result = selector.find(bs)
        assert result is None

    def test_find_raises_exception_if_no_match_and_strict_true(self):
        """
        Tests if find raises TagNotFoundException if no element matches the selector
        and strict is True.
        """
        text = """
            <div href="github" class="menu"></div>
            <a></a>
            <span class="widgets"></span>
            <a class="super_widget"></a>
            <a class="widget_2"></a>
        """
        bs = to_bs(text)
        selector = AttributeSelector(name="class", value="widget")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_returns_tag_that_matches_custom_attribute_name(self):
        """
        Tests find returns first matching element with custom attribute name
        matching the selector value.
        """
        text = """
            <div href="github" class="menu"></div>
            <a class="5"></a>
            <span awesomeness="4"></span>
            <a class="super_widget"></a>
            <span awesomeness="5"></span>
        """
        bs = to_bs(text)
        selector = AttributeSelector(name="awesomeness", value="5")
        result = selector.find(bs)
        assert str(result) == strip("""<span awesomeness="5"></span>""")

    def test_find_all_returns_all_matching_elements(self):
        """Tests if find_all returns a list of all matching elements."""
        text = """
            <div href="github" class="menu"></div>
            <div>
                <a class="widget">1</a>
            </div>
            <span class="widgets"></span>
            <a class="widget" href="github">2</a>
            <a class="widget_2"></a>
            <div class="widget"><a>3</a></div>
        """
        bs = to_bs(text)
        selector = AttributeSelector(name="class", value="widget")

        result = selector.find_all(bs)
        assert list(map(str, result)) == [
            strip("""<a class="widget">1</a>"""),
            strip("""<a class="widget" href="github">2</a>"""),
            strip("""<div class="widget"><a>3</a></div>"""),
        ]

    def test_find_all_returns_empty_list_when_no_match(self):
        """Tests if find returns an empty list if no element matches the selector."""
        text = """
            <div href="github" class="menu"></div>
            <a></a>
            <span class="widgets"></span>
            <a class="super_widget"></a>
            <a class="widget_2"></a>
        """
        bs = to_bs(text)
        selector = AttributeSelector(name="class", value="widget")

        result = selector.find_all(bs)
        assert result == []

    def test_do_not_shadow_bs4_find_method_parameters(self):
        """
        Tests that find method does not shadow bs4.selector find method parameters.
        If attribute name is the same as bs4.selector find method parameter
        like ex. 'string' or 'name' it should not cause any conflicts.
        The way to avoid it is to pass attribute filters as a dictionary to 'attrs'
        parameter in bs4.selector find method instead of as keyword arguments.
        """
        text = """
            <div href="github" class="menu"></div>
            <a class="github"></a>
            <span name="github"></span>
        """
        bs = to_bs(text)
        selector = AttributeSelector(name="name", value="github")
        result = selector.find(bs)
        assert str(result) == strip("""<span name="github"></span>""")

    @pytest.mark.css_selector
    @pytest.mark.parametrize(
        argnames="selector, css",
        argvalues=[
            (AttributeSelector("class", value="menu"), "[class='menu']"),
            (AttributeSelector("href", value="menu", re=True), "[href*='menu']"),
            (AttributeSelector("id", value=None, re=True), "[id]"),
            (AttributeSelector("id", value=None, re=False), "[id]"),
            (
                AttributeSelector("id", value=re.compile("menu"), re=True),
                "[id*='menu']",
            ),
            (
                AttributeSelector("id", value=re.compile("menu"), re=False),
                "[id*='menu']",
            ),
            (
                AttributeSelector("id", value=re.compile("^menu[0-9]$"), re=False),
                "[id*='^menu[0-9]$']",
            ),
            (
                AttributeSelector("id", value=re.compile("^menu[0-9]$"), re=True),
                "[id*='^menu[0-9]$']",
            ),
        ],
    )
    def test_selector_is_correct(self, selector: AttributeSelector, css: str):
        """Tests if css selector for AttributeSelector is constructed as expected."""
        assert selector.selector == css

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        In this case first 'a' element with href="github" matches the selector,
        but it's not a child of body element, so it's not returned.
        """
        text = """
            <div class="google">
                <a href="github">Hello 1</a>
            </div>
            <a href="github">Hello 2</a>
        """
        bs = find_body_element(to_bs(text))
        selector = AttributeSelector(name="href", value="github")
        result = selector.find(bs, recursive=False)

        assert str(result) == strip("""<a href="github">Hello 2</a>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False. In this case first 'a' element with href="github"
        matches the selector, but it's not a child of body element,
        so it's not returned.
        """
        text = """
            <div class="google">
                <a href="github">Hello 1</a>
            </div>
            <a class="github">Hello 2</a>
        """
        bs = find_body_element(to_bs(text))
        selector = AttributeSelector(name="href", value="github")
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <div class="google">
                <a href="github">Hello 1</a>
            </div>
            <a class="github">Hello 2</a>
        """
        bs = find_body_element(to_bs(text))
        selector = AttributeSelector(name="href", value="github")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True, recursive=False)

    def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
        self,
    ):
        """
        Tests if find_all returns an empty list if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div class="google">
                <a href="github">Hello 1</a>
            </div>
            <a class="github">Hello 2</a>
        """
        bs = find_body_element(to_bs(text))
        selector = AttributeSelector(name="href", value="github")
        results = selector.find_all(bs, recursive=False)
        assert results == []

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <div>
                <a class="github">Hello 1</a>
            </div>
            <a class="github">Hello 2</a>
            <div class="google"></div>
        """
        bs = find_body_element(to_bs(text))
        selector = AttributeSelector(name="class")
        results = selector.find_all(bs, recursive=False)

        assert list(map(str, results)) == [
            strip("""<a class="github">Hello 2</a>"""),
            strip("""<div class="google"></div>"""),
        ]

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <span>
                <a class="github">Hello 2</a>
            </span>
            <div class="menu"></div>
            <div class="google"></div>
            <span class="menu"></span>
        """
        bs = find_body_element(to_bs(text))
        selector = AttributeSelector(name="class")
        results = selector.find_all(bs, limit=2)

        assert list(map(str, results)) == [
            strip("""<a class="github">Hello 2</a>"""),
            strip("""<div class="menu"></div>"""),
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
                <a class="github">Hello 2</a>
            </span>
            <div class="menu"></div>
            <div>
                <div class="google"></div>
            </div>
            <span class="menu"></span>
        """
        bs = find_body_element(to_bs(text))
        selector = AttributeSelector(name="class")
        results = selector.find_all(bs, recursive=False, limit=2)

        assert list(map(str, results)) == [
            strip("""<div class="menu"></div>"""),
            strip("""<span class="menu"></span>"""),
        ]

    @pytest.mark.parametrize(
        argnames="selectors",
        argvalues=[
            # if only name is provided, it must be equal
            (AttributeSelector("class"), AttributeSelector("class")),
            # re does not matter if value is not provided
            (AttributeSelector("class", re=True), AttributeSelector("class", re=False)),
            # if value is provided, it must be equal
            (
                AttributeSelector("class", value="hello_world"),
                AttributeSelector("class", value="hello_world"),
            ),
            # if value is provided, re parameter must match
            (
                AttributeSelector("class", value="hello_world", re=True),
                AttributeSelector("class", value="hello_world", re=True),
            ),
            # value + re is equal to the same pattern
            (
                AttributeSelector("class", value="hello_world", re=True),
                AttributeSelector("class", value=re.compile("hello_world")),
            ),
            # the same compiled pattern
            (
                AttributeSelector("class", value=re.compile("hello_world")),
                AttributeSelector("class", value=re.compile("hello_world")),
            ),
            # if compiled pattern is provided, re is ignored
            (
                AttributeSelector("class", value=re.compile("hello_world"), re=True),
                AttributeSelector("class", value=re.compile("hello_world"), re=False),
            ),
            # equal if subclass of AttributeSelector and same value
            (
                AttributeSelector("class", value="widget"),
                ClassSelector("widget"),
            ),
        ],
    )
    def test_two_attribute_selectors_are_equal(
        self, selectors: tuple[AttributeSelector, AttributeSelector]
    ):
        """Tests if two AttributeSelector instances are equal."""
        assert (selectors[0] == selectors[1]) is True

    @pytest.mark.parametrize(
        argnames="selectors",
        argvalues=[
            # if only name is provided, it must not be equal
            (AttributeSelector("class"), AttributeSelector("id")),
            # if value is provided, names or values must not match
            (
                AttributeSelector("class", value="widget"),
                AttributeSelector("class", value="menu"),
            ),
            # different re parameter when pattern not provided
            (
                AttributeSelector("class", value="widget", re=False),
                AttributeSelector("class", value="widget", re=True),
            ),
            # different compiled patterns
            (
                AttributeSelector("class", value=re.compile("widget")),
                AttributeSelector("class", value=re.compile("^widget")),
            ),
            # compiled pattern string is not equal to string pattern with re=True
            (
                AttributeSelector("class", value="widget", re=True),
                AttributeSelector("class", value=re.compile("^widget")),
            ),
            # if not subclass of AttributeSelector, it is not equal
            (
                AttributeSelector("class", value="menu"),
                MockDivSelector(),
            ),
            # if subclass with different parameters, it is not equal
            (
                AttributeSelector("id", value="widget"),
                ClassSelector(value="widget"),
            ),
        ],
    )
    def test_two_attribute_selectors_are_not_equal(
        self, selectors: tuple[AttributeSelector, AttributeSelector]
    ):
        """Tests if two AttributeSelector instances are not equal."""
        assert (selectors[0] == selectors[1]) is False

    @pytest.mark.edge_case
    def test_find_matches_element_with_list_of_values_if_one_matches(self):
        """
        Tests if find returns first tag with that has a list of values
        of specific attribute, if one of the values matches the selector.

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
        selector = AttributeSelector("class", value="widget")
        result = selector.find(bs)
        assert str(result) == strip(
            """<div class="it has a long list of widget classes"></div>"""
        )
