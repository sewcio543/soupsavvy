"""Testing module for AttributeSelector class."""

import re

import pytest

from soupsavvy.tags.attributes import AttributeSelector
from soupsavvy.tags.exceptions import TagNotFoundException
from tests.soupsavvy.tags.conftest import find_body_element, strip, to_bs


@pytest.mark.soup
class TestAttributeSelector:
    """Class for AttributeSelector unit test suite."""

    def test_tag_was_found_based_on_exact_value_match(self):
        """Tests if bs4.Tag was found for exact value match."""
        markup = """<a class="widget"></a>"""
        bs = to_bs(markup)
        tag = AttributeSelector(name="class", value="widget")
        result = tag.find(bs)
        assert str(result) == strip(markup)

    @pytest.mark.parametrize(
        argnames="markup",
        argvalues=[
            """<a class="widget_2"></a>""",
            """<a class="widget menu"></a>""",
        ],
        ids=["with_underscore", "with_space"],
    )
    def test_tag_was_found_based_on_partial_value_match(self, markup: str):
        """
        Tests if bs4.Tag was found when element attribute value
        contains value specified in AttributeSelector.
        Case when re=True and re.Pattern is used for element search.
        """
        bs = to_bs(markup)
        tag = AttributeSelector(name="class", value="widget", re=True)
        result = tag.find(bs)
        assert str(result) == strip(markup)

    @pytest.mark.parametrize(
        argnames="markup",
        argvalues=[
            """<a class="widget_1"></a>""",
            """<a class="widget 345"></a>""",
        ],
        ids=["one_digit", "three_digits"],
    )
    def test_pattern_as_string_matches_element_based_on_re_pattern(self, markup: str):
        """Tests if bs4.Tag was found based on regex string for attribute."""
        bs = to_bs(markup)
        tag = AttributeSelector(name="class", pattern=r"^widget.?\d{1,3}$")
        result = tag.find(bs)
        assert str(result) == strip(markup)

    @pytest.mark.css_selector
    def test_when_pattern_and_value_pattern_used_in_find_value_in_selector(self):
        """
        Tests if both value and pattern are passed, value is used in selector attribute
        and pattern is used in find method.
        """
        bs = to_bs("""<a class="widgets"></a>""")
        tag = AttributeSelector(
            name="class", value="widget", re=True, pattern=r"^widget.?\d{1,3}$"
        )
        assert tag.selector == "[class*='widget']"
        # tag does not match pattern, on the contrary to css selector
        assert tag.find(bs) is None

    @pytest.mark.parametrize(
        argnames="markup",
        argvalues=[
            """<a class="widget_1"></a>""",
            """<a class="widget 345"></a>""",
        ],
        ids=["one_digit", "three_digits"],
    )
    def test_pattern_as_re_pattern(self, markup: str):
        """
        Tests if bs4.Tag was found based on regex pattern (re.Pattern) for attribute.
        """
        bs = to_bs(markup)
        tag = AttributeSelector(name="class", pattern=re.compile("widget"))
        result = tag.find(bs)
        assert str(result) == strip(markup)

    @pytest.mark.parametrize(
        argnames="markup",
        argvalues=[
            """<a class="profile"></a>""",
            """<a class="photo" href="github" id="123"></a>""",
            """
            <div class="container">
                <span class="record"></span>
                <a class="menu"></a>
            </div>
            """,
        ],
        ids=["only_class", "additional_parameters", "nested"],
    )
    def test_pattern_and_value_are_none_matches_anything(self, markup: str):
        """
        Tests if neither pattern nor value was specified any element matches tag
        and first one is returned.
        """
        bs = to_bs(markup)
        tag = AttributeSelector(name="class")
        result = tag.find(bs)
        assert str(result) == strip(markup)

    @pytest.mark.parametrize(
        argnames="markup",
        argvalues=[
            """<a class="widget_1_menu"></a>""",
            """<a class="widget 3454"></a>""",
        ],
        ids=["suffix", "too_many_digits"],
    )
    def test_pattern_does_not_match(self, markup: str):
        """
        Tests find return None if class of the element in html
        does not match specified regex pattern.
        """
        bs = to_bs(markup)
        tag = AttributeSelector(name="class", pattern=r"^widget.?\d{1,3}$")
        assert tag.find(bs) is None

    @pytest.mark.parametrize(
        argnames="markup",
        argvalues=[
            """<a id="widget_1"></a>""",
            """<div id="widget 3454"></div>""",
        ],
        ids=["suffix", "too_many_digits"],
    )
    def test_does_not_find_element_without_attribute_despite_match_anything_pattern(
        self,
        markup: str,
    ):
        """
        Tests find return None if element does not have class attribute
        even when value and pattern are not specified and any attribute
        value is matched.
        """
        bs = to_bs(markup)
        tag = AttributeSelector(name="class")
        assert tag.find(bs) is None

    @pytest.mark.parametrize(
        argnames="markup",
        argvalues=[
            """<a awesomeness="5"></a>""",
            """<div awesomeness="5"></div>""",
        ],
        ids=["a", "div"],
    )
    def test_matches_any_attribute_name(self, markup: str):
        """
        Tests find matches any attribute name, including custom like "awesomeness".
        """
        bs = to_bs(markup)
        tag = AttributeSelector(name="awesomeness", value="5")
        result = tag.find(bs)
        assert str(result) == strip(markup)

    @pytest.mark.parametrize(
        argnames="markup",
        argvalues=[
            """<a awesomeness="2"></a>""",
            """<div awesomeness="-5"></div>""",
        ],
        ids=["a", "div"],
    )
    def test_does_not_match_random_attribute_name(self, markup: str):
        """
        Tests find returns none for custom attribute name if element does not match
        the tag value.
        """
        bs = to_bs(markup)
        tag = AttributeSelector(name="awesomeness", value="5")
        assert tag.find(bs) is None

    @pytest.mark.parametrize(
        argnames="markup",
        argvalues=[
            """<a class="menu"></a>""",
            """
            <div>
                <span class="record"></span>
                <a class="menu"></a>
            </div>
            """,
        ],
        ids=["single_tag", "nested_tag"],
    )
    def test_raises_exception_if_element_not_found_in_strict_mode(self, markup: str):
        """
        Tests find raises a TagNotFoundException exception if no element matches
        the value and thus None was returned. Setting strict parameter to True
        results in function raising exception in this case.
        """
        bs = to_bs(markup)
        tag = AttributeSelector(name="class", value="photo")

        with pytest.raises(TagNotFoundException):
            tag.find(bs, strict=True)

    @pytest.mark.parametrize(
        argnames="markup",
        argvalues=[
            """<a href="github/settings"></a>""",
            """<a href="github pages"></a>""",
            """<a href="github "></a>""",
        ],
        ids=["with_slash", "with_space", "with_trailing_whitespace"],
    )
    def test_setting_re_false_matches_only_exact_attribute_name(self, markup: str):
        """
        Tests if finds returns None if re was set to False and elements don't
        match specified name exactly.
        """
        bs = to_bs(markup)
        tag = AttributeSelector(name="href", value="github", re=False)
        assert tag.find(bs) is None

    def test_find_all_returns_all_matching_elements_in_a_list(self):
        """
        Tests if find_all returns a list of all matching elements.
        Elements of this list should be the instances of bs4.Tag.
        """
        text = """
            <a href="github/settings"></a>
            <a href="github pages"></a>
            <a href="github "></a>
        """
        bs = to_bs(text)
        tag = AttributeSelector(name="href", value="github", re=True)
        result = tag.find_all(bs)
        excepted = [
            strip("""<a href="github/settings"></a>"""),
            strip("""<a href="github pages"></a>"""),
            strip("""<a href="github "></a>"""),
        ]
        assert list(map(str, result)) == excepted

    def test_find_all_returns_only_matching_elements(self):
        """
        Tests if find_all returns a list of all matching elements.
        It does not contain not exact match if re=False.
        It should match based on element attribute value and not by element name.
        """
        text = """
            <a href="github"></a>
            <div href="github"></div>
            <a id="github"></a>
            <a href="github pages"></a>
        """
        bs = to_bs(text)
        tag = AttributeSelector(name="href", value="github", re=False)
        result = tag.find_all(bs)
        excepted = [
            strip("""<a href="github"></a>"""),
            strip("""<div href="github"></div>"""),
        ]
        assert list(map(str, result)) == excepted

    @pytest.mark.parametrize(
        argnames="markup",
        argvalues=[
            """<a href="github"></a>""",
            """<div class="photos"></div>""",
            """<span id="photos "></span>""",
        ],
        ids=["wrong_href", "div_class", "span_id"],
    )
    def test_find_all_returns_empty_list_when_not_found(self, markup: str):
        """Tests if find returns an empty list if no element matches the tag."""
        bs = to_bs(markup)
        tag = AttributeSelector(name="href", value="photos")
        result = tag.find_all(bs)
        assert result == []

    def test_find_all_matches_all_nested_elements(self):
        """
        Tests if find_all matches both parent and child element
        in html tree if they match the tag.
        """
        text = """
            <div href="github">
                <a class="github/settings"></a>
                <a id="github pages"></a>
                <a href="github "></a>
            </div>
        """
        bs = to_bs(text)
        tag = AttributeSelector(name="href", value="github", re=True)
        result = tag.find_all(bs)
        expected_1 = """
            <div href="github">
                <a class="github/settings"></a>
                <a id="github pages"></a>
                <a href="github "></a>
            </div>
        """
        expected_2 = """<a href="github "></a>"""
        assert list(map(str, result)) == [strip(expected_1), strip(expected_2)]

    def test_do_not_shadow_bs4_find_method_parameters(self):
        """
        Tests that find method does not shadow bs4.Tag find method parameters.
        If attribute name is the same as bs4.Tag find method parameter
        like ex. 'string' or 'name' it should not cause any conflicts.
        The way to avoid it is to pass attribute filters as a dictionary to 'attrs'
        parameter in bs4.Tag find method instead of as keyword arguments.
        """
        markup = """<a name="github"></a>"""
        bs = to_bs(markup)
        tag = AttributeSelector(name="name", value="github")
        result = tag.find(bs)
        assert str(result) == strip(markup)

    @pytest.mark.css_selector
    @pytest.mark.parametrize(
        argnames="tag, selector",
        argvalues=[
            (AttributeSelector("class", value="menu"), "[class='menu']"),
            (AttributeSelector("href", value="menu", re=True), "[href*='menu']"),
            (AttributeSelector("id", value=None, re=True), "[id]"),
            (AttributeSelector("level", value=None, re=False), "[level]"),
            (
                AttributeSelector("id", value="string", pattern="pattern"),
                "[id='string']",
            ),
        ],
        ids=[
            "exact_match",
            "contains_match",
            "match_all_re_true",
            "match_all_re_false",
            "pattern_skipped_in_selector",
        ],
    )
    def test_selector_is_correct(self, tag: AttributeSelector, selector: str):
        """Tests if css selector for AttributeSelector is constructed as expected."""
        assert tag.selector == selector

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
        tag = AttributeSelector(name="href", value="github")
        result = tag.find(bs, recursive=False)

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
        tag = AttributeSelector(name="href", value="github")
        result = tag.find(bs, recursive=False)
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
        tag = AttributeSelector(name="href", value="github")

        with pytest.raises(TagNotFoundException):
            tag.find(bs, strict=True, recursive=False)

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
        tag = AttributeSelector(name="href", value="github")
        results = tag.find_all(bs, recursive=False)
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
        tag = AttributeSelector(name="class")
        results = tag.find_all(bs, recursive=False)

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
        tag = AttributeSelector(name="class")
        results = tag.find_all(bs, limit=2)

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
        tag = AttributeSelector(name="class")
        results = tag.find_all(bs, recursive=False, limit=2)

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
                AttributeSelector("class", pattern="hello_world"),
            ),
            # if pattern is provided, value is ignored
            (
                AttributeSelector("class", value="pizza", pattern="^hello_world"),
                AttributeSelector("class", value="pasta", pattern="^hello_world"),
            ),
            # if pattern is provided, re parameter is ignored
            (
                AttributeSelector("class", re=True, pattern="^hello_world"),
                AttributeSelector("class", re=False, pattern="^hello_world"),
            ),
            # if pattern is provided, both re and value are ignored
            (
                AttributeSelector(
                    "class", value="pizza", re=True, pattern="^hello_world"
                ),
                AttributeSelector(
                    "class", value="pasta", re=False, pattern="^hello_world"
                ),
            ),
            # if compiled pattern is provided, it must be equal
            (
                AttributeSelector("class", pattern=re.compile(r"^hello_world")),
                AttributeSelector("class", pattern=re.compile(r"^hello_world")),
            ),
            # if compiled pattern is provided, other parameters are ignored
            (
                AttributeSelector(
                    "class",
                    value="pizza",
                    re=True,
                    pattern=re.compile(r"^hello_world"),
                ),
                AttributeSelector(
                    "class",
                    value="pasta",
                    re=False,
                    pattern=re.compile(r"^hello_world"),
                ),
            ),
            # compiled and string patterns are equal
            (
                AttributeSelector("class", pattern="widget"),
                AttributeSelector("class", pattern=re.compile(r"widget")),
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
            # if pattern is provided, is must not be equal
            (
                AttributeSelector("class", pattern="^widget"),
                AttributeSelector("class", pattern="widget"),
            ),
            # if pattern is provided, other parameters are ignored
            (
                AttributeSelector("class", value="pizza", re=True, pattern="^widget"),
                AttributeSelector("class", value="pizza", re=True, pattern="^menu"),
            ),
            # pattern is the same, but name is different
            (
                AttributeSelector("class", pattern="^widget"),
                AttributeSelector("id", pattern="^widget"),
            ),
            # compiled patterns are different
            (
                AttributeSelector("class", pattern=re.compile("^widget")),
                AttributeSelector("class", pattern=re.compile("widget")),
            ),
            # pattern and value with the same strings are not equal
            (
                AttributeSelector("class", pattern="menu"),
                AttributeSelector("class", value="menu"),
            ),
        ],
    )
    def test_two_attribute_selectors_are_not_equal(
        self, selectors: tuple[AttributeSelector, AttributeSelector]
    ):
        """Tests if two AttributeSelector instances are not equal."""
        assert (selectors[0] == selectors[1]) is False
