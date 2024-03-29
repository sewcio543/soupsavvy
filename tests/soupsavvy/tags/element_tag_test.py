"""Testing module for ElementTag class."""

import pytest
from bs4 import Tag

from soupsavvy.tags.base import SoupUnionTag
from soupsavvy.tags.components import AttributeTag, ElementTag
from soupsavvy.tags.exceptions import TagNotFoundException, WildcardTagException

from .conftest import strip, to_bs


@pytest.mark.soup
class TestElementTag:
    """Class for ElementTag unit test suite."""

    @pytest.mark.parametrize(
        argnames="tag",
        argvalues=[
            ElementTag(
                tag="a", attributes=[AttributeTag(name="class", value="widget")]
            ),
            ElementTag(tag="a"),
            ElementTag(
                tag=None, attributes=[AttributeTag(name="class", value="widget")]
            ),
            ElementTag(
                tag="a",
                attributes=[AttributeTag(name="class", value="widget", re=True)],
            ),
            ElementTag(
                tag="a", attributes=[AttributeTag(name="class", pattern="widget")]
            ),
            ElementTag(tag="a", attributes=[AttributeTag(name="class")]),
        ],
        ids=[
            "exact_tag_name_match",
            "only_tag_name_match",
            "any_tag_name_match",
            "re_match",
            "pattern_match",
            "existing_attribute_match",
        ],
    )
    def test_tag_was_found_based_on_valid_tag_and_attributes(self, tag: ElementTag):
        """
        Tests if bs4.Tag was found for various combinations of tag and attributes.
        Element should be matched if tag is specified as 'a' or None
        for any element name and matching attribute tag.
        """
        markup = """<a class="widget"></a>"""
        bs = to_bs(markup)
        result = tag.find(bs)
        assert str(result) == strip(markup)

    @pytest.mark.parametrize(
        argnames="tag",
        argvalues=[
            ElementTag(
                tag="a",
                attributes=[
                    AttributeTag(name="class", value="widget menu"),
                    AttributeTag(name="id", value="menu 1"),
                ],
            ),
            ElementTag(
                tag="a",
                attributes=[AttributeTag(name="class", value="widget", re=True)],
            ),
            ElementTag(
                tag="a",
                attributes=[AttributeTag(name="class", value="widget menu", re=False)],
            ),
            ElementTag(
                tag=None,
                attributes=[AttributeTag(name="id", pattern=r"^menu.?\d$")],
            ),
        ],
        ids=[
            "element_match_with_multiple_attributes",
            "element_match_with_one_attributes_re",
            "element_match_with_one_attributes",
            "any_match_with_one_attributes_pattern",
        ],
    )
    def test_tag_with_attributes_was_found_for_valid_tags(self, tag: ElementTag):
        """
        Tests if bs4.Tag with multiple attributes was found for various tags
        that should match them. Tag is found only if all defined attributes tags match
        element's attribute and tag name is the same.
        """
        markup = """<a class="widget menu" id="menu 1"></a>"""
        bs = to_bs(markup)
        result = tag.find(bs)
        assert str(result) == strip(markup)

    def test_raises_exception_when_initialized_without_parameters(self):
        """
        Tests if ElementTag initialized without any parameters raises WildcardTagException.
        This is illegal move sincve it matches all elements
        and AnyTag should be used instead.
        """
        with pytest.raises(WildcardTagException):
            ElementTag()

    @pytest.mark.parametrize(
        argnames="tag",
        argvalues=[
            ElementTag(
                tag="div",
                attributes=[
                    AttributeTag(name="class", value="widget menu"),
                    AttributeTag(name="id", value="menu 1"),
                ],
            ),
            ElementTag(
                tag="a",
                attributes=[
                    AttributeTag(name="class", value="wrong name"),
                    AttributeTag(name="id", value="wrong name"),
                ],
            ),
            ElementTag(
                tag="a",
                attributes=[
                    AttributeTag(name="class", value="widget menu"),
                    AttributeTag(name="id", value="wrong name"),
                ],
            ),
            ElementTag(tag=None, attributes=[AttributeTag(name="id", value="menu")]),
            ElementTag(tag=None, attributes=[AttributeTag(name="name", value="123")]),
        ],
        ids=[
            "tag_name_not_match",
            "all_attribute_not_match",
            "one_attribute_not_match",
            "any_tag_not_match",
            "not_exisitng_attribute_match",
        ],
    )
    def test_tag_with_attributes_was_found_for_not_matching_tags(self, tag: ElementTag):
        """
        Tests find return None for various tags that does not match given element.
        Element should not be match if tag and all attributes are not matching.
        """
        markup = """<a class="widget menu" id="menu 1"></a>"""
        bs = to_bs(markup)
        assert tag.find(bs) is None

    def test_additional_attribute_is_not_matched(self):
        """
        Tests find return element if it has attributes that are not specified
        in ElementTag, they can take any value and are skipped in find.
        In this case, the fact that element has 'id' attribute
        does not affect the find method.
        """
        markup = """<a class="widget" id="menu 1"></a>"""
        bs = to_bs(markup)
        tag = ElementTag(
            tag="a", attributes=[AttributeTag(name="class", value="widget")]
        )
        result = tag.find(bs)
        assert str(result) == strip(markup)

    def test_find_raises_exception_in_strict_mode_if_non_matching(self):
        """
        Tests find raises TagNotFoundException exception if no element was matched.
        """
        markup = """<a class="widget menu" id="menu 1"></a>"""
        bs = to_bs(markup)
        tag = ElementTag(tag="div")

        with pytest.raises(TagNotFoundException):
            tag.find(bs, strict=True)

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
        tag = ElementTag(
            tag="a",
            attributes=[AttributeTag(name="href", value="github", re=True)],
        )
        result = tag.find_all(bs)
        assert len(result) == 3
        assert isinstance(result, list)
        assert all(isinstance(tag, Tag) for tag in result)

    def test_find_all_returns_only_matching_elements(self):
        """
        Tests if find_all returns a list of all matching elements.
        In this case it should match any 'a' element with href="github"
        and id that contains a digit.
        """
        text = """
            <a href="github" id="1"></a>
            <a href="github" id="2"></a>
            <a href="github", id="hello"></a>
            <div href="github", id="6"></div>
            <div id="github"></div>
            <a href="github pages", id="5"></a>
        """
        bs = to_bs(text)
        tag = ElementTag(
            tag="a",
            attributes=[
                AttributeTag(name="href", value="github"),
                AttributeTag(name="id", pattern=r"\d"),
            ],
        )
        result = tag.find_all(bs)
        excepted = [
            strip("""<a href="github" id="1"></a>"""),
            strip("""<a href="github" id="2"></a>"""),
        ]
        assert list(map(str, result)) == excepted

    def test_find_all_returns_empty_list_when_not_found(self):
        """Tests if find returns an empty list if no element matches the tag."""
        text = """
            <a href="github" id="hello"></a>
            <a href="github pages", id="5"></a>
        """
        bs = to_bs(text)
        tag = ElementTag(
            tag="a",
            attributes=[
                AttributeTag(name="href", value="github"),
                AttributeTag(name="id", pattern=r"\d"),
            ],
        )
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
        tag = ElementTag(
            tag=None,
            attributes=[AttributeTag(name="href", value="github", re=True)],
        )
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
            (
                ElementTag(attributes=[AttributeTag("class", value="menu")]),
                "[class='menu']",
            ),
            (
                ElementTag(
                    attributes=[
                        AttributeTag("class", value="menu"),
                        AttributeTag("id", value="menu_2"),
                    ]
                ),
                "[class='menu'][id='menu_2']",
            ),
            (
                ElementTag(
                    tag="div",
                    attributes=[
                        AttributeTag("class", value="menu"),
                        AttributeTag("id", value="menu_2"),
                    ],
                ),
                "div[class='menu'][id='menu_2']",
            ),
            (
                ElementTag(
                    tag="a",
                    attributes=[
                        AttributeTag("class", value="menu", re=True),
                        AttributeTag("awesomeness", value="3", re=False),
                    ],
                ),
                "a[class*='menu'][awesomeness='3']",
            ),
            (
                ElementTag(
                    tag="a",
                    attributes=[
                        AttributeTag("class", value="menu"),
                        AttributeTag("class", value="menu"),
                    ],
                ),
                "a[class='menu']",
            ),
            (ElementTag(tag="a", attributes=[AttributeTag("class")]), "a[class]"),
            (
                ElementTag(
                    tag="a", attributes=[AttributeTag("class", value="widget menu")]
                ),
                "a[class='widget menu']",
            ),
        ],
        ids=[
            "only_attribute",
            "only_multiple_attributes",
            "tag_and_attributes",
            "tag_and_re_attributes",
            "duplicated_attributes",
            "tag_and_any_value_attribute",
            "attribute_value_with_whitespace",
        ],
    )
    def test_selector_is_correct(self, tag: ElementTag, selector: str):
        """Tests if css selector for ElementTag is constructed as expected."""
        assert tag.selector == selector

    @pytest.mark.parametrize(
        argnames="tags",
        argvalues=[
            (ElementTag("a"), ElementTag("a")),
            (
                ElementTag("a", attributes=[AttributeTag("class", value="widget")]),
                ElementTag("a", attributes=[AttributeTag("class", value="widget")]),
            ),
            (
                ElementTag(attributes=[AttributeTag("class", value="widget")]),
                ElementTag(attributes=[AttributeTag("class", value="widget")]),
            ),
        ],
        ids=["without_attributes", "with_attributes", "without_tag"],
    )
    def test_equal_method_returns_true_for_the_same_parameters(
        self, tags: list[ElementTag]
    ):
        """Tests if __eq__ returns True if tags have the same init parameters."""
        assert tags[0] == tags[1]

    @pytest.mark.parametrize(
        argnames="tags",
        argvalues=[
            (ElementTag("a"), ElementTag("div")),
            (
                ElementTag("a", attributes=[AttributeTag("class", value="widget")]),
                ElementTag("a", attributes=[AttributeTag("class", value="menu")]),
            ),
            (
                ElementTag(attributes=[AttributeTag("class", value="widget")]),
                ElementTag(attributes=[AttributeTag("class", value="menu")]),
            ),
        ],
        ids=["without_attributes", "with_attributes", "without_tag"],
    )
    def test_equal_method_returns_false_for_the_different_parameters(
        self, tags: list[ElementTag]
    ):
        """Tests if __eq__ returns False if tags have different init parameters."""
        assert tags[0] != tags[1]

    def test_dunder_or_method_returns_selector_union_with_expected_tags(self):
        """
        Tests if __or__ method of SelectableSoup returns SoupUnionTag with
        expected tags that took part in logical disjunction.
        """
        tag_1 = ElementTag("a", attributes=[AttributeTag("class", value="widget")])
        tag_2 = ElementTag("div", attributes=[AttributeTag("class", value="menu")])
        union = tag_1.__or__(tag_2)
        assert union == SoupUnionTag(tag_1, tag_2)
        assert isinstance(union, SoupUnionTag)
        # checking python itself just to make sure syntactical sugar works
        assert union == (tag_1 | tag_2)

    def test_dunder_or_method_raises_exception_when_not_selectable_soup(self):
        """
        Tests if __or__ method of SelectableSoup raises TypeError when input parameter
        is not of SelectableSoup type.
        """
        tag_1 = ElementTag("a")

        with pytest.raises(TypeError):
            tag_1.__or__("element")  # type: ignore
