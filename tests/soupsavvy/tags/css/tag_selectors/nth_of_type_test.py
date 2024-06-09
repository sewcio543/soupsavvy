"""Module with unit tests for NthOfType css tag selector."""

import pytest

from soupsavvy.tags.css.exceptions import InvalidCSSSelector
from soupsavvy.tags.css.tag_selectors import NthOfType
from soupsavvy.tags.exceptions import TagNotFoundException
from tests.soupsavvy.tags.conftest import find_body_element, strip, to_bs


@pytest.mark.css_selector
@pytest.mark.soup
class TestNthOfType:
    """Class with unit tests for NthOfType tag selector."""

    def test_selector_is_correct_without_tag(self):
        """
        Tests if selector property returns correct value without specifying tag.
        In case of NthOfType n is a required parameter and is passed into
        selector string as a parameter of :nth-of-type() pseudo-class.
        """
        assert NthOfType(n="2n").selector == ":nth-of-type(2n)"

    def test_passing_invalid_n_does_not_raise_exception_on_init(self):
        """
        Tests if passing invalid n parameter into NthOfType does not raise
        exception on initialization. Invalid n parameter will raise exception
        when find method is called.
        """
        tag = NthOfType(n="soupsavvy")
        assert tag.selector == ":nth-of-type(soupsavvy)"

    def test_selector_is_correct_with_tag(self):
        """Tests if selector property returns correct value when specifying tag."""
        assert NthOfType(n="2n", tag="div").selector == "div:nth-of-type(2n)"

    @pytest.mark.parametrize(argnames="n", argvalues=["2n", "2n+2", "2"])
    def test_finds_returns_none_if_no_nth_of_type_without_tag(self, n: str):
        """
        Tests if find method returns None if no nth child of type relative to parent
        element is found and tag is not specified. In this case, there are only
        one child of specific type per parent element.
        """
        html = """
            <div>
                <p>text 1</p>
                <a>text 2</a>
            </div>
            <span>
                <p>text 1</p>
            </span>
        """
        bs = find_body_element(to_bs(html))
        tag = NthOfType(n)
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
        tag = NthOfType(n="1", tag="span")
        result = tag.find(bs)
        assert result is None

    def test_find_returns_none_if_no_nth_of_type_with_tag(self):
        """
        Tests if find method returns None if no nth-of-type(2) element is found
        when tag is specified. Nth child is skipped when its name does not match
        the tag 'div', as in this case for 'p'.
        """
        html = """
            <div>
                <div>Hello</p>
                <p>text 1</p>
                <p>text 2</p>
            </div>
            <span></span>
        """
        bs = find_body_element(to_bs(html))
        tag = NthOfType(n="2", tag="div")
        result = tag.find(bs)
        assert result is None

    def test_find_returns_first_nth_of_type_without_tag(self):
        """
        Tests if find method returns first nth-of-type when tag is not specified.
        """
        html = """
            <div>
                <p>text 1</p>
                <a>text 2</a>
            </div>
            <span>
                <p>text 3</p>
                <p>text 4</p>
            </span>
        """
        bs = find_body_element(to_bs(html))
        tag = NthOfType("2")
        result = tag.find(bs)
        assert str(result) == strip("<p>text 4</p>")

    def test_find_returns_first_nth_of_type_with_tag(self):
        """
        Tests if find method returns first nth-of-type which
        name matches the specified tag. In this case 'p' is the matching element,
        but it is skipped as it does not match the specified tag 'div'.
        """
        html = """
            <div>
                <div>Hello 1</div>
                <p>text 1</p>
                <p>text 2</p>
            </div>
            <span>
                <div>Hello 2</div>
                <div>Hello 3</div>
            </span>
        """
        bs = find_body_element(to_bs(html))
        tag = NthOfType(n="2", tag="div")
        result = tag.find(bs)
        assert str(result) == strip("<div>Hello 3</div>")

    def test_find_raises_exception_without_specified_tag_if_not_found_in_strict_mode(
        self,
    ):
        """
        Tests if find method raises TagNotFoundException
        if no nth-of-type is found in strict mode when tag is not specified.
        """
        html = """
            <div>
                <p>text 1</p>
                <a>text 2</a>
            </div>
            <span>Hello</span>
        """
        bs = find_body_element(to_bs(html))
        tag = NthOfType("2")

        with pytest.raises(TagNotFoundException):
            tag.find(bs, strict=True)

    def test_find_raises_exception_with_specified_tag_if_not_found_in_strict_mode(self):
        """
        Tests if find method raises TagNotFoundException
        if no nth-of-type is found in strict mode when tag is specified.
        """
        html = """
            <div>
                <p>text 1</p>
                <p>text 2</p>
                <div>Hello</div>
            </div>
            <span>Hello</span>
        """
        bs = find_body_element(to_bs(html))
        tag = NthOfType(n="2", tag="div")

        with pytest.raises(TagNotFoundException):
            tag.find(bs, strict=True)

    def test_find_and_find_all_raise_exception_with_invalid_selector(self):
        """
        Tests if find and find_all methods raise InvalidCSSSelector exception
        if invalid n parameter is passed into the selector.
        """
        html = """<div></div>"""
        bs = find_body_element(to_bs(html))
        tag = NthOfType("2x+1")

        with pytest.raises(InvalidCSSSelector):
            tag.find(bs)

        with pytest.raises(InvalidCSSSelector):
            tag.find_all(bs)

    def test_find_all_returns_empty_list_if_no_nth_of_type_without_tag(self):
        """
        Tests if find_all method returns empty list
        if no nth-of-type element is found and tag is not specified.
        """
        html = """
            <div>
                <p>text 1</p>
                <a>text 2</a>
            </div>
            <span>
                <a>text 3</a>
            </span>
        """
        bs = find_body_element(to_bs(html))
        tag = NthOfType("2")
        result = tag.find_all(bs)
        assert result == []

    def test_find_all_returns_empty_list_if_no_nth_of_type_with_tag(self):
        """
        Tests if find_all method returns empty list if no nth-of-type element
        is found and tag is specified. In this case 'p' and 'a' match
        the selector nth-of-type(2), but they are skipped as they do not match
        the specified tag 'div'.
        """
        html = """
            <div>
                <p>text 1</p>
                <p>text 2</p>
            </div>
            <span>
                <p>text 3</p>
                <a>text 4</a>
                <a>text 5</a>
            </span>
        """
        bs = find_body_element(to_bs(html))
        tag = NthOfType(n="2", tag="div")
        result = tag.find_all(bs)
        assert result == []

    def test_find_all_returns_all_nth_of_type_without_tag(self):
        """
        Tests if find_all method returns all nth-of-type children
        when tag is not specified.
        """
        html = """
            <div>
                <p>text 1</p>
                <p>text 2</p>
            </div>
            <span>
                <p>text 3</p>
                <a>text 4</a>
                <a>text 5</a>
            </span>
            <span>Hello</span>
        """
        bs = find_body_element(to_bs(html))
        tag = NthOfType("2")

        result = tag.find_all(bs)
        assert list(map(str, result)) == [
            strip("<p>text 2</p>"),
            strip("<a>text 5</a>"),
            strip("<span>Hello</span>"),
        ]

    def test_find_all_returns_all_nth_of_type_with_tag(self):
        """
        Tests if find_all method returns all nth-of-type children
        which name matches the specified tag.
        """
        html = """
            <div>
                <p>text 1</p><p>text 2</p>
                <p>text 3</p><p>text 4</p>
            </div>
            <span>
                <p>text 5</p>
                <a>text 6</a>
                <p>text 7</p>
                <a>text 8</a>
            </span>
            <span>Hello</span>
        """
        bs = find_body_element(to_bs(html))
        tag = NthOfType(n="2n", tag="p")
        result = tag.find_all(bs)

        assert list(map(str, result)) == [
            strip("<p>text 2</p>"),
            strip("<p>text 4</p>"),
            strip("<p>text 7</p>"),
        ]

    @pytest.mark.parametrize(argnames="n", argvalues=["even", "2n"])
    def test_find_all_returns_all_even_tags_with_matching_selectors(self, n: str):
        """
        Tests if find_all method returns all nth-of-type children
        when n is set to selector that would select even children.
        """
        html = """
            <a>Link</a>
            <div>
                <p>text 1</p>
                <p>text 2</p>
                <p>text 3</p>
            </div>
            <span><p>text 4</p><p>text 5</p></span>
            <span>Hello</span>
        """
        bs = find_body_element(to_bs(html))
        tag = NthOfType(n)
        result = tag.find_all(bs)

        assert list(map(str, result)) == [
            strip("<p>text 2</p>"),
            strip("<p>text 5</p>"),
            strip("<span>Hello</span>"),
        ]

    @pytest.mark.parametrize(argnames="n", argvalues=["odd", "2n+1"])
    def test_find_all_returns_all_odd_tags_with_matching_selectors(self, n: str):
        """
        Tests if find_all method returns all nth-of-type children
        when n is set to selector that would select odd children.
        """
        html = """
            <div>Hello</div>
            <div>
                <p>text 1</p>
                <p>text 2</p>
                <p>text 3</p>
            </div>
            <span>Hello</span>
            <span><p>text 4</p><p>text 5</p></span>
        """
        bs = find_body_element(to_bs(html))
        tag = NthOfType(n)
        result = tag.find_all(bs)

        assert list(map(str, result)) == [
            strip("<div>Hello</div>"),
            strip("<p>text 1</p>"),
            strip("<p>text 3</p>"),
            strip("<span>Hello</span>"),
            strip("<p>text 4</p>"),
        ]

    def test_selector_works_with_whitespaces_the_same_way(self):
        """
        Tests if find_all method returns all nth children when provided selector
        with whitespaces. It should work the same way as without whitespaces.
        Parsing is delegated to soupsieve library.
        """
        html = """
            <div>Hello</div>
            <div>
                <p>text 1</p>
                <p>text 2</p>
            </div>
            <span>Hello 1</span>
            <span>Hello 2</span>
        """
        bs = find_body_element(to_bs(html))
        tag = NthOfType(" 2n +  1")
        result = tag.find_all(bs)

        assert list(map(str, result)) == [
            strip("<div>Hello</div>"),
            strip("<p>text 1</p>"),
            strip("<span>Hello 1</span>"),
        ]
