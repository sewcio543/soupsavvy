"""Module with unit tests for LastOfType css tag selector."""

import pytest

from soupsavvy.tags.css.tag_selectors import LastOfType
from soupsavvy.tags.exceptions import TagNotFoundException
from tests.soupsavvy.tags.conftest import find_body_element, strip, to_bs


class TestLastOfType:
    """Class with unit tests for LastOfType tag selector."""

    def test_selector_is_correct_without_tag(self):
        """Tests if selector property returns correct value without specifying tag."""
        assert LastOfType().selector == ":last-of-type"

    def test_selector_is_correct_with_tag(self):
        """Tests if selector property returns correct value when specifying tag."""
        assert LastOfType("div").selector == "div:last-of-type"

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
        tag = LastOfType("span")
        result = tag.find(bs)
        assert result is None

    def test_find_returns_last_element_without_tag(self):
        """
        Tests if find method returns last element when tag is not specified.
        When last-of-type is passed without a tag, it returns all last elements
        of each type, so first found element is just the last element in the markup.
        """
        html = """
            <div>text 1</div>
            <span>text 2</span>
            <span>text 3</span>
            <div>text 4</div>
        """
        bs = find_body_element(to_bs(html))
        tag = LastOfType()
        result = tag.find(bs)
        assert str(result) == strip("<span>text 3</span>")

    def test_find_returns_last_element_of_type_with_tag(self):
        """
        Tests if find method returns last element of type which name matches
        the specified tag. Even though div, span and p are last elements of
        their type relative to parent element, only last 'a' is returned as it matches
        the specified tag.
        """
        html = """
            <div>
                <p>text 1</p>
            </div>
            <span>
                <a>text 2</a>
                <a>text 3</a>
            </span>
        """
        bs = find_body_element(to_bs(html))
        tag = LastOfType("a")
        result = tag.find(bs)
        assert str(result) == strip("<a>text 3</a>")

    def test_find_raises_exception_with_specified_tag_if_not_found_in_strict_mode(self):
        """
        Tests if find method raises TagNotFoundException
        if no element of type is found in strict mode when tag is specified.
        It only makes sense to test for exception when tag is specified,
        as there is always a last element of type otherwise.
        """
        html = """
            <div>
                <p>text 1</p>
                <div>Hello</div>
            </div>
            <span>Hello</span>
        """
        bs = find_body_element(to_bs(html))
        tag = LastOfType("a")

        with pytest.raises(TagNotFoundException):
            tag.find(bs, strict=True)

    def test_find_all_returns_empty_list_if_no_elements_of_type(self):
        """
        Tests if find_all method returns empty list if no elements of specified
        type are found.
        """
        html = """
            <div>
                <p>text 1</p>
            </div>
            <span></span>
        """
        bs = find_body_element(to_bs(html))
        tag = LastOfType("a")
        result = tag.find_all(bs)
        assert result == []

    def test_find_all_returns_all_last_of_type_without_tag(self):
        """
        Tests if find_all method returns all last elements of each type
        relative to their parent element when tag is not specified.
        """
        html = """
            <span><p>text 1</p><p>text 2</p></span>
            <div>
                <p>text 3</p>
                <a>text 4</a>
                <div>Hello 1</div>
                <div>Hello 2</div>
            </div>
            <div><p>text 5</p></div>
        """
        bs = find_body_element(to_bs(html))
        tag = LastOfType()
        result = tag.find_all(bs)
        assert list(map(str, result)) == [
            strip("<span><p>text 1</p><p>text 2</p></span>"),
            strip("<p>text 2</p>"),
            strip("<p>text 3</p>"),
            strip("<a>text 4</a>"),
            strip("<div>Hello 2</div>"),
            strip("<div><p>text 5</p></div>"),
            strip("<p>text 5</p>"),
        ]

    def test_find_all_returns_all_last_of_type_elements_with_tag(self):
        """
        Tests if find_all method returns all last elements of type which name matches
        the specified tag.
        """
        html = """
            <span><p>text 1</p><p>text 2</p></span>
            <div>
                <p>text 3</p>
                <a>text 4</a>
                <div>Hello 1</div>
                <div>Hello 2</div>
            </div>
            <div><p>text 5</p></div>
        """
        bs = find_body_element(to_bs(html))
        tag = LastOfType("div")
        result = tag.find_all(bs)

        assert list(map(str, result)) == [
            strip("<div>Hello 2</div>"),
            strip("<div><p>text 5</p></div>"),
        ]
