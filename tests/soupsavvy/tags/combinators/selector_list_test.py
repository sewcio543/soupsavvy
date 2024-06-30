"""Testing module for SelectorList class."""

import pytest

from soupsavvy.tags.combinators import SelectorList
from soupsavvy.tags.components import AttributeSelector, TagSelector
from soupsavvy.tags.exceptions import NotSoupSelectorException, TagNotFoundException
from tests.soupsavvy.tags.conftest import find_body_element, strip, to_bs


@pytest.fixture(scope="session")
def mock_soup_union() -> SelectorList:
    """
    Fixture that mocks SelectorList with three Tags:
    * first matching all 'a' elements with 'class' attribute equal to 'widget'
    * second matching all 'div' elements with 'class' attribute equal to 'menu'
    * third matching all elements with 'awesomeness' attribute which value contains a digit.

    Returns
    -------
    SelectorList
        Mocked SelectorList used for testing purposes.
    """
    tag_1 = TagSelector("a", attributes=[AttributeSelector("class", value="widget")])
    tag_2 = TagSelector("div", attributes=[AttributeSelector("class", value="menu")])
    tag_3 = AttributeSelector(name="awesomeness", value=r"\d", re=True)
    union = SelectorList(tag_1, tag_2, tag_3)
    return union


@pytest.mark.soup
@pytest.mark.combinator
class TestSelectorList:
    """Class for SelectorList unit test suite."""

    def test_init_raises_exception_if_at_least_one_argument_is_not_soup_selector(
        self,
    ):
        """
        Tests if init raises a NotSoupSelectorException exception if at least one
        of the positional parameters is not an instance of SoupSelector.
        """
        tag_1 = TagSelector(
            "a", attributes=[AttributeSelector("class", value="widget")]
        )

        with pytest.raises(NotSoupSelectorException):
            SelectorList(tag_1, "string")  # type: ignore

    def test_soup_union_is_instantiated_with_correct_tags_attribute(self):
        """
        Tests if tags attribute of SelectorList is assigned properly is a list
        containing all Tags provided in init.
        """
        tag_1 = TagSelector(
            "a", attributes=[AttributeSelector("class", value="widget")]
        )
        tag_2 = TagSelector(
            "div", attributes=[AttributeSelector("class", value="menu")]
        )

        union = SelectorList(tag_1, tag_2)

        assert isinstance(union.selectors, list)
        assert union.selectors == [tag_1, tag_2]

    def test_soup_union_is_instantiated_with_more_than_two_arguments(self):
        """
        Tests if tags attribute of SelectorList is assigned properly is a list
        containing all Tags provided in init. Init can take any number of positional
        arguments above 2 that are SoupSelector.
        In this case testing arguments of mixed types: ElementTag and AttributeTag.
        """
        tag_1 = TagSelector(
            "a", attributes=[AttributeSelector("class", value="widget")]
        )
        tag_2 = TagSelector(
            "div", attributes=[AttributeSelector("class", value="menu")]
        )
        tag_3 = AttributeSelector(name="class", value="dropdown")

        union = SelectorList(tag_1, tag_2, tag_3)

        assert isinstance(union.selectors, list)
        assert union.selectors == [tag_1, tag_2, tag_3]

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
        self, markup: str, mock_soup_union: SelectorList
    ):
        """
        Tests if find returns Tag for elements matching any of SelectorList tags.
        """
        bs = to_bs(markup)
        result = mock_soup_union.find(bs)
        assert strip(str(result)) == strip(markup)

    def test_find_returns_none_if_no_element_matches_the_tags(
        self, mock_soup_union: SelectorList
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
        self, mock_soup_union: SelectorList
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
        self, mock_soup_union: SelectorList
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
        assert list(map(lambda x: strip(str(x)), result)) == expected

    def test_finds_all_returns_empty_list_if_no_element_matches(
        self, mock_soup_union: SelectorList
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
        assert result == []

    def test_union_consisting_of_unions_covers_all_tags(self):
        """
        Tests if SelectorList constructed from SelectorLists matches all elements
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
        union = SelectorList(
            SelectorList(TagSelector("a"), TagSelector("div")),
            SelectorList(TagSelector("b"), TagSelector("i")),
        )
        result = union.find_all(bs)
        expected = [
            strip("<a></a>"),
            strip("<div></div>"),
            strip("<b></b>"),
            strip("<i></i>"),
        ]
        assert list(map(lambda x: strip(str(x)), result)) == expected

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        In this case first 'a' and 'p' elements mach, but they are not direct children
        of body element, so they are not returned.
        """
        text = """
            <div>
                <a href="github">Hello 1</a>
                <p>Hello 2</p>
            </div>
            <a href="github">Hello 3</a>
            <p>Hello 4</p>
        """
        bs = find_body_element(to_bs(text))
        tag = SelectorList(
            TagSelector(tag="a"),
            TagSelector(tag="p"),
        )
        result = tag.find(bs, recursive=False)

        assert strip(str(result)) == strip("""<a href="github">Hello 3</a>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div>
                <a href="github">Hello 1</a>
                <p>Hello 2</p>
            </div>
        """
        bs = find_body_element(to_bs(text))
        tag = SelectorList(
            TagSelector(tag="a"),
            TagSelector(tag="p"),
        )
        result = tag.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <div>
                <a href="github">Hello 1</a>
                <p>Hello 2</p>
            </div>
        """
        bs = find_body_element(to_bs(text))
        tag = SelectorList(
            TagSelector(tag="a"),
            TagSelector(tag="p"),
        )

        with pytest.raises(TagNotFoundException):
            tag.find(bs, strict=True, recursive=False)

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <p>Empty</p>
            <div>
                <a href="github">Hello 1</a>
                <p>Hello 2</p>
            </div>
            <a href="github">Hello 3</a>
            <p>Hello 4</p>
            <span></span>
        """
        bs = find_body_element(to_bs(text))
        tag = SelectorList(
            TagSelector(tag="a"),
            TagSelector(tag="p"),
        )
        results = tag.find_all(bs, recursive=False)

        assert list(map(lambda x: strip(str(x)), results)) == [
            strip("""<a href="github">Hello 3</a>"""),
            strip("""<p>Empty</p>"""),
            strip("""<p>Hello 4</p>"""),
        ]

    def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
        self,
    ):
        """
        Tests if find_all returns an empty list if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div>
                <a href="github">Hello 1</a>
                <p>Hello 2</p>
            </div>
        """
        bs = find_body_element(to_bs(text))
        tag = SelectorList(
            TagSelector(tag="a"),
            TagSelector(tag="p"),
        )

        results = tag.find_all(bs, recursive=False)
        assert results == []

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 3 first in order elements are returned.
        Union does not return found elements in the order they appear in
        the document, but in the order they are found, so first all 'a' elements
        are returned, then 'p' elements.
        """
        text = """
            <p>Empty</p>
            <span>
                <a href="github">Hello 1</a>
            </span>
            <p>Hello 2</p>
            <a>Hello 3</a>
        """
        bs = find_body_element(to_bs(text))
        tag = SelectorList(
            TagSelector(tag="a"),
            TagSelector(tag="p"),
        )
        results = tag.find_all(bs, limit=3)

        assert list(map(lambda x: strip(str(x)), results)) == [
            strip("""<a href="github">Hello 1</a>"""),
            strip("""<a>Hello 3</a>"""),
            strip("""<p>Empty</p>"""),
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
            <p>Empty</p>
            <span>
                <a href="github">Hello 1</a>
            </span>
            <p>Hello 2</p>
            <a>Hello 3</a>
        """
        bs = find_body_element(to_bs(text))
        tag = SelectorList(
            TagSelector(tag="a"),
            TagSelector(tag="p"),
        )
        results = tag.find_all(bs, recursive=False, limit=2)

        assert list(map(lambda x: strip(str(x)), results)) == [
            strip("""<a>Hello 3</a>"""),
            strip("""<p>Empty</p>"""),
        ]

    def test_find_all_does_not_duplicate_if_tag_matches_multiple_selectors(
        self,
    ):
        """
        Tests if find_all does not duplicate elements if they match multiple selectors.
        """
        text = """
            <a href="github">Hello 1</a>
            <a class="widget">Hello 2</a>
        """
        bs = find_body_element(to_bs(text))
        tag = SelectorList(
            TagSelector(tag="a"),
            AttributeSelector("class", "widget"),
        )
        results = tag.find_all(bs)

        assert list(map(lambda x: strip(str(x)), results)) == [
            strip("""<a href="github">Hello 1</a>"""),
            strip("""<a class="widget">Hello 2</a>"""),
        ]
