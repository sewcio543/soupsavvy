"""Testing module for AttributeTag class."""

import re

import pytest
from bs4 import Tag

from soupsavvy.tags.components import AttributeTag
from soupsavvy.tags.exceptions import TagNotFoundException

from .conftest import strip, to_bs


@pytest.mark.soup
class TestAttributeTag:
    """Class for AttributeTag unit test suite."""

    def test_tag_was_found_based_on_exact_value_match(self):
        """Tests if bs4.Tag was found for exact value match."""
        markup = """<a class="widget"></a>"""
        bs = to_bs(markup)
        tag = AttributeTag(name="class", value="widget")
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
        contains value specified in AttributeTag.
        Case when re=True and re.Pattern is used for element search.
        """
        bs = to_bs(markup)
        tag = AttributeTag(name="class", value="widget", re=True)
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
        tag = AttributeTag(name="class", pattern=r"^widget.?\d{1,3}$")
        result = tag.find(bs)
        assert str(result) == strip(markup)

    @pytest.mark.css_selector
    def test_when_pattern_and_value_pattern_used_in_find_value_in_selector(self):
        """
        Tests if both value and pattern are passed, value is used in selector attribute
        and pattern is used in find method.
        """
        bs = to_bs("""<a class="widgets"></a>""")
        tag = AttributeTag(
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
        tag = AttributeTag(name="class", pattern=re.compile("widget"))
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
        tag = AttributeTag(name="class")
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
        tag = AttributeTag(name="class", pattern=r"^widget.?\d{1,3}$")
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
        tag = AttributeTag(name="class")
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
        tag = AttributeTag(name="awesomeness", value="5")
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
        tag = AttributeTag(name="awesomeness", value="5")
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
        tag = AttributeTag(name="class", value="photo")

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
        tag = AttributeTag(name="href", value="github", re=False)
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
        tag = AttributeTag(name="href", value="github", re=True)
        result = tag.find_all(bs)
        assert len(result) == 3
        assert isinstance(result, list)
        assert all(isinstance(tag, Tag) for tag in result)

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
        tag = AttributeTag(name="href", value="github", re=False)
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
        tag = AttributeTag(name="href", value="photos")
        result = tag.find_all(bs)
        assert isinstance(result, list)
        assert len(result) == 0

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
        tag = AttributeTag(name="href", value="github", re=True)
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

    @pytest.mark.css_selector
    @pytest.mark.parametrize(
        argnames="tag, selector",
        argvalues=[
            (AttributeTag("class", value="menu"), "[class='menu']"),
            (AttributeTag("href", value="menu", re=True), "[href*='menu']"),
            (AttributeTag("id", value=None, re=True), "[id]"),
            (AttributeTag("level", value=None, re=False), "[level]"),
            (AttributeTag("id", value="string", pattern="pattern"), "[id='string']"),
        ],
        ids=[
            "exact_match",
            "contains_match",
            "match_all_re_true",
            "match_all_re_false",
            "pattern_skipped_in_selector",
        ],
    )
    def test_selector_is_correct(self, tag: AttributeTag, selector: str):
        """Tests if css selector for AttributeTag is constructed as expected."""
        assert tag.selector == selector

    @pytest.mark.parametrize(
        argnames="tags",
        argvalues=[
            (
                AttributeTag("class", value="widget"),
                AttributeTag("class", value="widget"),
            ),
            (
                AttributeTag("class", value="widget", re=True),
                AttributeTag("class", value="widget", re=True),
            ),
            (
                AttributeTag("class", pattern="^widget"),
                AttributeTag("class", pattern="^widget"),
            ),
        ],
        ids=["re_false", "re_true", "pattern"],
    )
    def test_equal_method_returns_true_for_the_same_parameters(
        self, tags: list[AttributeTag]
    ):
        """Tests if __eq__ returns True if tags have the same init parameters."""
        assert tags[0] == tags[1]

    @pytest.mark.parametrize(
        argnames="tags",
        argvalues=[
            (
                AttributeTag("class", value="widget"),
                AttributeTag("class", value="menu"),
            ),
            (
                AttributeTag("class", value="widget"),
                AttributeTag("id", value="widget"),
            ),
            (
                AttributeTag("class", value="widget", re=False),
                AttributeTag("class", value="widget", re=True),
            ),
            (
                AttributeTag("class", pattern="^widget"),
                AttributeTag("class", pattern="^menu"),
            ),
            (
                AttributeTag("class", pattern="^widget", value="hello"),
                AttributeTag("class", pattern="^menu", value="world"),
            ),
        ],
        ids=["value", "name", "re", "pattern", "value_with_pattern"],
    )
    def test_equal_method_returns_false_for_the_different_parameters(
        self, tags: list[AttributeTag]
    ):
        """Tests if __eq__ returns False if tags have different init parameters."""
        assert tags[0] != tags[1]
