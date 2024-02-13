"""Testing module for SoupUnionTag class."""

import pytest

from soupsavvy.tags.base import SoupUnionTag
from soupsavvy.tags.components import AttributeTag, ElementTag
from soupsavvy.tags.exceptions import NotSelectableSoupException, TagNotFoundException

from .conftest import strip, to_bs


@pytest.fixture(scope="session")
def mock_soup_union() -> SoupUnionTag:
    """
    Fixture that mocks SoupUnionTag with three Tags:
    * first matching all 'a' elements with 'class' attribute equal to 'widget'
    * second matching all 'div' elements with 'class' attribute equal to 'menu'
    * third matching all elements with 'awesomeness' attribute which value contains a digit.

    Returns
    -------
    SoupUnionTag
        Mocked SoupUnionTag used for testing purposes.
    """
    tag_1 = ElementTag("a", attributes=[AttributeTag("class", value="widget")])
    tag_2 = ElementTag("div", attributes=[AttributeTag("class", value="menu")])
    tag_3 = AttributeTag(name="awesomeness", pattern=r"\d")
    union = SoupUnionTag(tag_1, tag_2, tag_3)
    return union


@pytest.mark.soup
class TestSoupUnionTag:
    """Class for SoupUnionTag unit test suite."""

    def test_init_raises_exception_if_at_least_one_argument_is_not_selectable_soup(
        self,
    ):
        """
        Tests if init raises a NotSelectableSoupException exception if at least one
        of the positional parameters is not an instance of SelectableSoup.
        """
        tag_1 = ElementTag("a", attributes=[AttributeTag("class", value="widget")])

        with pytest.raises(NotSelectableSoupException):
            SoupUnionTag(tag_1, "string")  # type: ignore

    def test_soup_union_is_instanciated_with_correct_tags_attribute(self):
        """
        Tests if tags attribute of SoupUnionTag is asigned properly is a list
        containing all Tags provided in init.
        """
        tag_1 = ElementTag("a", attributes=[AttributeTag("class", value="widget")])
        tag_2 = ElementTag("div", attributes=[AttributeTag("class", value="menu")])

        union = SoupUnionTag(tag_1, tag_2)

        assert isinstance(union.tags, list)
        assert union.tags == [tag_1, tag_2]

    def test_soup_union_is_instanciated_with_more_than_two_arguments(self):
        """
        Tests if tags attribute of SoupUnionTag is asigned properly is a list
        containing all Tags provided in init. Init can take any number of positional
        arguments above 2 that are SelectableSoup.
        In this case testing arguments of mixed types: ElementTag and AttributeTag.
        """
        tag_1 = ElementTag("a", attributes=[AttributeTag("class", value="widget")])
        tag_2 = ElementTag("div", attributes=[AttributeTag("class", value="menu")])
        tag_3 = AttributeTag(name="class", value="dropdown")

        union = SoupUnionTag(tag_1, tag_2, tag_3)

        assert isinstance(union.tags, list)
        assert union.tags == [tag_1, tag_2, tag_3]

    @pytest.mark.parametrize(
        argnames="markup",
        argvalues=[
            """<a class="widget"></a>""",
            """<div class="menu"></div>""",
            """<i awesomeness="3"></i>""",
        ],
        ids=["a", "div", "attribute"],
    )
    def test_soup_finds_element_of_any_matching_tag(
        self, markup: str, mock_soup_union: SoupUnionTag
    ):
        """
        Tests if find returns Tag for elements matching any of SoupUnionTag tags.
        """
        bs = to_bs(markup)
        result = mock_soup_union.find(bs)
        assert str(result) == strip(markup)

    def test_find_returns_none_if_no_element_matches_the_tags(
        self, mock_soup_union: SoupUnionTag
    ):
        """Tests if find method returns None if no element matches provided tags."""
        markup = """
            <a class="menu"></a>
            <div class="widget"></div>
            <i awesomeness="widget"></i>
        """
        bs = to_bs(markup)
        assert mock_soup_union.find(bs) is None

    def test_find_raises_exception_if_no_element_matches_the_tags_in_strict_mode(
        self, mock_soup_union: SoupUnionTag
    ):
        """
        Tests if find method raises TagNotFoundException if no element
        matches provided tags in strict mode.
        """
        markup = """
            <a class="menu"></a>
            <div class="widget"></div>
            <i class="widget"></i>
            <b awesomeness="widget"></b>
        """
        bs = to_bs(markup)

        with pytest.raises(TagNotFoundException):
            mock_soup_union.find(bs, strict=True)

    def test_finds_all_returns_a_list_of_all_matching_elements(
        self, mock_soup_union: SoupUnionTag
    ):
        """
        Tests find_all returns a list of all elements that match any of provided tags.
        """
        markup = """
            <a class="widget"></a>
            <div class="widget"></div>
            <div class="menu"></div>
            <a class="menu"></a>
            <i awesomeness="italics 5"></i>
            <b awesomeness="bold"></b>
        """
        bs = to_bs(markup)
        result = mock_soup_union.find_all(bs)
        assert isinstance(result, list)
        expected = [
            strip("""<a class="widget"></a>"""),
            strip("""<div class="menu"></div>"""),
            strip("""<i awesomeness="italics 5"></i>"""),
        ]
        assert list(map(str, result)) == expected

    def test_finds_all_returns_empty_list_if_no_element_matches(
        self, mock_soup_union: SoupUnionTag
    ):
        """
        Tests find_all returns an empty list if no element matches any of provided tags.
        """
        markup = """
            <a class="menu"></a>
            <div class="widget"></div>
            <b awesomeness="bold"></b>
        """
        bs = to_bs(markup)
        result = mock_soup_union.find_all(bs)
        assert isinstance(result, list)
        assert len(result) == 0

    def test_union_consisting_of_unions_covers_all_tags(self):
        """
        Tests if SoupUnionTag constructed from SoupUnionTags matches all elements
        that match any of Unions.
        """
        markup = """
            <a></a>
            <span></span>
            <div></div>
            <b></b>
            <img></img>
            <i></i>
        """
        bs = to_bs(markup)
        union = SoupUnionTag(
            SoupUnionTag(ElementTag("a"), ElementTag("div")),
            SoupUnionTag(ElementTag("b"), ElementTag("i")),
        )
        result = union.find_all(bs)
        expected = [
            strip("<a></a>"),
            strip("<div></div>"),
            strip("<b></b>"),
            strip("<i></i>"),
        ]
        assert list(map(str, result)) == expected
