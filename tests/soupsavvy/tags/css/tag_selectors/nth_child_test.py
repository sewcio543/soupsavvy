"""Module with unit tests for NthChild css tag selector."""

import pytest

from soupsavvy.exceptions import InvalidCSSSelector, TagNotFoundException
from soupsavvy.tags.css.tag_selectors import NthChild
from tests.soupsavvy.tags.conftest import find_body_element, strip, to_bs


@pytest.mark.css_selector
@pytest.mark.soup
class TestNthChild:
    """Class with unit tests for NthChild tag selector."""

    def test_selector_is_correct_without_tag(self):
        """
        Tests if selector property returns correct value without specifying tag.
        In case of NthChild n is a required parameter and is passed into
        selector string as a parameter of :nth-child() pseudo-class.
        """
        assert NthChild(n="2n").selector == ":nth-child(2n)"

    def test_passing_invalid_n_does_not_raise_exception_on_init(self):
        """
        Tests if passing invalid n parameter into NthChild does not raise
        exception on initialization. Invalid n parameter will raise exception
        when find method is called.
        """
        tag = NthChild(n="soupsavvy")
        assert tag.selector == ":nth-child(soupsavvy)"

    def test_selector_is_correct_with_tag(self):
        """Tests if selector property returns correct value when specifying tag."""
        assert NthChild(n="2n", tag="div").selector == "div:nth-child(2n)"

    @pytest.mark.parametrize(argnames="n", argvalues=["3n", "3n+3", "3"])
    def test_finds_returns_none_if_no_nth_child_without_tag(self, n: str):
        """
        Tests if find method returns None if no nth child is found
        when tag is not specified and strict mode is not enabled.
        In this case n is set to values out of range of children, max depth is 2,
        so no nth child is not found.
        """
        html = """
            <div>
                <p>text 1</p>
                <p>text 2</p>
            </div>
            <div></div>
        """
        bs = find_body_element(to_bs(html))
        tag = NthChild(n)
        result = tag.find(bs)
        assert result is None

    def test_find_returns_none_if_tag_name_not_present(self):
        """
        Tests if find method returns None if specified tag is not present
        in the tag markup. In this case, 'span' is not present in the markup.
        """
        html = """
            <div>
                <p>text</p>
            </div>
            <div></div>
        """
        bs = find_body_element(to_bs(html))
        tag = NthChild(n="1", tag="span")
        result = tag.find(bs)
        assert result is None

    def test_find_returns_none_if_no_nth_child_with_tag(self):
        """
        Tests if find method returns None if no nth child (2) is found
        when tag is specified and strict mode is not enabled.
        Nth child is skipped when its name does not match the tag,
        as in this case for 'p' and 'a'.
        """
        html = """
            <div>
                <div>Hello</p>
                <p>text 1</p>
            </div>
            <a>text 2</a>
            <div></div>
        """
        bs = find_body_element(to_bs(html))
        tag = NthChild(n="2", tag="div")
        result = tag.find(bs)
        assert result is None

    def test_find_returns_first_nth_child_without_tag(self):
        """
        Tests if find method returns first nth child when tag is not specified.
        """
        html = """
            <div>
                <p>text 1</p>
                <p>text 2</p>
            </div>
            <span></span>
        """
        bs = find_body_element(to_bs(html))
        tag = NthChild("2")
        result = tag.find(bs)
        assert strip(str(result)) == strip("<p>text 2</p>")

    def test_find_returns_first_nth_child_with_tag(self):
        """
        Tests if find method returns first nth child which name matches
        the specified tag. Even though 'p' and 'span' are the second children,
        they are skipped because they do not match the specified tag.
        """
        html = """
            <div>
                <div>Hello</div>
                <p>text 1</p>
            </div>
            <span>
                <a>text 2</a>
                <div>Hello 2</div>
            </span>
        """
        bs = find_body_element(to_bs(html))
        tag = NthChild(n="2", tag="div")
        result = tag.find(bs)
        assert strip(str(result)) == strip("<div>Hello 2</div>")

    def test_find_raises_exception_without_specified_tag_if_not_found_in_strict_mode(
        self,
    ):
        """
        Tests if find method raises TagNotFoundException
        if no nth child is found in strict mode when tag is not specified.
        """
        html = """
            <div>
                <p>text 1</p>
                <p>text 2</p>
            </div>
            <span>Hello</span>
        """
        bs = find_body_element(to_bs(html))
        tag = NthChild("3")

        with pytest.raises(TagNotFoundException):
            tag.find(bs, strict=True)

    def test_find_raises_exception_with_specified_tag_if_not_found_in_strict_mode(self):
        """
        Tests if find method raises TagNotFoundException
        if no nth child is found in strict mode when tag is specified.
        """
        html = """
            <div>
                <p>text 1</p>
                <div>Hello</div>
            </div>
            <span>Hello</span>
        """
        bs = find_body_element(to_bs(html))
        tag = NthChild(n="2", tag="p")

        with pytest.raises(TagNotFoundException):
            tag.find(bs, strict=True)

    def test_find_and_find_all_raise_exception_with_invalid_selector(self):
        """
        Tests if find and find_all methods raise InvalidCSSSelector exception
        if invalid n parameter is passed into the selector.
        """
        html = """<div></div>"""
        bs = find_body_element(to_bs(html))
        tag = NthChild("2x+1")

        with pytest.raises(InvalidCSSSelector):
            tag.find(bs)

        with pytest.raises(InvalidCSSSelector):
            tag.find_all(bs)

    def test_find_all_returns_empty_list_if_no_nth_child_without_tag(self):
        """
        Tests if find_all method returns empty list
        if no nth child is found, when tag is not specified.
        """
        html = """
            <div>
                <p>text 1</p>
                <p>text 2</p>
            </div>
            <div></div>
        """
        bs = find_body_element(to_bs(html))
        tag = NthChild("3")
        result = tag.find_all(bs)
        assert result == []

    def test_find_all_returns_empty_list_if_no_nth_child_with_tag(self):
        """
        Tests if find_all method returns empty list if no nth child is found
        when tag is specified. Nth child is skipped when
        its name does not match the tag, as in this case for 'p'.
        """
        html = """
            <div>
                <p>text 1</p>
                <p>text 2</p>
            </div>
            <span></span>
        """
        bs = find_body_element(to_bs(html))
        tag = NthChild(n="2", tag="div")
        result = tag.find_all(bs)
        assert result == []

    def test_find_all_returns_all_nth_children_without_tag(self):
        """
        Tests if find_all method returns all nth children
        when tag is not specified.
        """
        html = """
            <div>
                <p>text 1</p>
                <p>text 2</p>
            </div>
            <span><p>text 3</p></span>
        """
        bs = find_body_element(to_bs(html))
        tag = NthChild("2")

        result = tag.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("<p>text 2</p>"),
            strip("<span><p>text 3</p></span>"),
        ]

    def test_find_all_returns_all_nth_children_with_tag(self):
        """
        Tests if find_all method returns all nth children
        which name matches the specified tag.
        """
        html = """
            <div>
                <p>text 1</p>
                <div>Hello 1</div>
            </div>
            <div>Hello 2</div>
        """
        bs = find_body_element(to_bs(html))
        tag = NthChild(n="2", tag="div")
        result = tag.find_all(bs)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("<div>Hello 1</div>"),
            strip("<div>Hello 2</div>"),
        ]

    @pytest.mark.parametrize(argnames="n", argvalues=["even", "2n"])
    def test_find_all_returns_all_even_tags_with_matching_selectors(self, n: str):
        """
        Tests if find_all method returns all nth children
        when n is set to selector that would select even children.
        """
        html = """
            <div>
                <p>text 1</p>
                <p>text 2</p>
                <p>text 3</p>
                <p>text 4</p>
            </div>
            <span><p>text 5</p><p>text 6</p></span>
        """
        bs = find_body_element(to_bs(html))
        tag = NthChild(n)

        result = tag.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("<p>text 2</p>"),
            strip("<p>text 4</p>"),
            strip("<span><p>text 5</p><p>text 6</p></span>"),
            strip("<p>text 6</p>"),
        ]

    @pytest.mark.parametrize(argnames="n", argvalues=["odd", "2n+1"])
    def test_find_all_returns_all_odd_tags_with_matching_selectors(self, n: str):
        """
        Tests if find_all method returns all nth children
        when n is set to selector that would select odd children.
        """
        html = """
            <span><p>text 1</p><p>text 2</p></span>
            <div>
                <p>text 3</p>
                <p>text 4</p>
                <p>text 5</p>
            </div>
        """
        bs = find_body_element(to_bs(html))
        tag = NthChild(n)

        result = tag.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("<span><p>text 1</p><p>text 2</p></span>"),
            strip("<p>text 1</p>"),
            strip("<p>text 3</p>"),
            strip("<p>text 5</p>"),
        ]

    def test_selector_works_with_whitespaces_the_same_way(self):
        """
        Tests if find_all method returns all nth children when provided selector
        with whitespaces. It should work the same way as without whitespaces.
        Parsing is delegated to soupsieve library.
        """
        html = """
            <span><p>text 1</p><p>text 2</p></span>
            <div>
                <p>text 3</p>
                <p>text 4</p>
            </div>
        """
        bs = find_body_element(to_bs(html))
        tag = NthChild(" 2n +  1")

        result = tag.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("<span><p>text 1</p><p>text 2</p></span>"),
            strip("<p>text 1</p>"),
            strip("<p>text 3</p>"),
        ]
