"""Module with unit tests for FirstOfType css tag selector."""

import pytest

from soupsavvy.tags.css.tag_selectors import FirstOfType
from soupsavvy.tags.exceptions import TagNotFoundException
from tests.soupsavvy.tags.conftest import find_body_element, strip, to_bs


@pytest.mark.css_selector
@pytest.mark.soup
class TestFirstOfType:
    """Class with unit tests for FirstOfType tag selector."""

    def test_selector_is_correct_without_tag(self):
        """Tests if selector property returns correct value without specifying tag."""
        assert FirstOfType().selector == ":first-of-type"

    def test_selector_is_correct_with_tag(self):
        """Tests if selector property returns correct value when specifying tag."""
        assert FirstOfType("div").selector == "div:first-of-type"

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
        tag = FirstOfType("span")
        result = tag.find(bs)
        assert result is None

    def test_find_returns_first_element_without_tag(self):
        """
        Tests if find method returns first element when tag is not specified.
        When first-of-type is passed without a tag, it returns all first elements
        of each type, so first found element is just the first element in the markup.
        """
        html = """
            <div><p>text 1</p></div>
            <span>
                <p>text 2</p>
            </span>
        """
        bs = find_body_element(to_bs(html))
        tag = FirstOfType()
        result = tag.find(bs)
        assert strip(str(result)) == strip("<div><p>text 1</p></div>")

    def test_find_returns_first_element_of_type_with_tag(self):
        """
        Tests if find method returns first element of type which name matches
        the specified tag. Even though div, span and p are first elements of
        their type relative to parent element, only first 'a' is returned as it matches
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
        tag = FirstOfType("a")
        result = tag.find(bs)
        assert strip(str(result)) == strip("<a>text 2</a>")

    def test_find_raises_exception_with_specified_tag_if_not_found_in_strict_mode(self):
        """
        Tests if find method raises TagNotFoundException
        if no element of type is found in strict mode when tag is specified.
        It only makes sense to test for exception when tag is specified,
        as there is always a first element of type otherwise.
        """
        html = """
            <div>
                <p>text 1</p>
                <div>Hello</div>
            </div>
            <span>Hello</span>
        """
        bs = find_body_element(to_bs(html))
        tag = FirstOfType("a")

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
        tag = FirstOfType("a")
        result = tag.find_all(bs)
        assert result == []

    def test_find_all_returns_all_first_of_type_without_tag(self):
        """
        Tests if find_all method returns all first elements of each type
        relative to their parent element when tag is not specified.
        """
        html = """
            <div><p>text 1</p></div>
            <span><p>text 2</p><p>text 3</p></span>
            <div>
                <p>text 4</p>
                <a>text 5</a>
                <div>Hello 1</div>
                <div>Hello 2</div>
            </div>
        """
        bs = find_body_element(to_bs(html))
        tag = FirstOfType()
        result = tag.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("<div><p>text 1</p></div>"),
            strip("<p>text 1</p>"),
            strip("<span><p>text 2</p><p>text 3</p></span>"),
            strip("<p>text 2</p>"),
            strip("<p>text 4</p>"),
            strip("<a>text 5</a>"),
            strip("<div>Hello 1</div>"),
        ]

    def test_find_all_returns_all_first_of_type_elements_with_tag(self):
        """
        Tests if find_all method returns all first elements of type which name matches
        the specified tag.
        """
        html = """
            <div><p>text 1</p></div>
            <span><p>text 2</p><p>text 3</p></span>
            <div>
                <p>text 4</p>
                <a>text 5</a>
                <div>Hello 1</div>
                <div>Hello 2</div>
            </div>
        """
        bs = find_body_element(to_bs(html))
        tag = FirstOfType("div")
        result = tag.find_all(bs)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("<div><p>text 1</p></div>"),
            strip("<div>Hello 1</div>"),
        ]
