"""Module with unit tests for Empty css tag selector."""

import pytest

from soupsavvy.tags.css.tag_selectors import Empty
from soupsavvy.tags.exceptions import TagNotFoundException
from tests.soupsavvy.tags.conftest import find_body_element, strip, to_bs


class TestEmptyChild:
    """Class with unit tests for EmptyChild tag selector."""

    def test_selector_is_correct_without_tag(self):
        """Tests if selector property returns correct value without specifying tag."""
        assert Empty().selector == ":empty"

    def test_selector_is_correct_with_tag(self):
        """Tests if selector property returns correct value when specifying tag."""
        assert Empty("div").selector == "div:empty"

    def test_find_returns_none_if_no_empty_element_without_tag(self):
        """
        Tests if find method returns None if no empty tag is found, if tag has any children
        or text it's considered not empty.
        Find method should return None if not-strict mode is enabled.
        """
        html = """
            <div>Hello</div>
            <div><a>soupsavvy</a></div>
        """
        bs = find_body_element(to_bs(html))
        tag = Empty()
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
        tag = Empty("span")
        result = tag.find(bs)
        assert result is None

    def test_find_returns_none_if_no_empty_element_with_tag(self):
        """
        Tests if find method returns None if no empty tag is found
        when tag is specified, but no empty one of this name is found
        and find is run in not-strict mode.
        """
        # p is the empty tag, but selector has specified div tag
        html = """
            <div><p></p></div>
            <div><a>Hello</a></div>
        """
        bs = find_body_element(to_bs(html))
        tag = Empty("div")
        result = tag.find(bs)
        assert result is None

    def test_find_returns_first_empty_element_without_tag(self):
        """
        Tests if find method returns first empty tag when tag is not specified.
        """
        html = """
            <div>
                <p>text 1</p>
            </div>
            <div></div>
            <span></span>
        """
        bs = find_body_element(to_bs(html))
        tag = Empty()
        result = tag.find(bs)
        assert str(result) == strip("<div></div>")

    def test_find_returns_first_empty_element_with_tag(self):
        """
        Tests if find method returns first empty tag which name matches
        the specified tag. Even though div is the empty tag, it is skipped
        because it does not match the specified tag 'span'.
        """
        html = """
            <div></div>
            <span></span>
        """
        bs = find_body_element(to_bs(html))
        tag = Empty("span")
        result = tag.find(bs)
        assert str(result) == strip("<span></span>")

    def test_find_raises_exception_without_tag_if_not_found_in_strict_mode(self):
        """
        Tests if find method raises TagNotFoundException
        if no empty tag is found in strict mode when tag is not specified.
        """
        html = """
            <div>
                <p>text 1</p>
                <p>text 2</p>
            </div>
            <span>Hello</span>
        """
        bs = find_body_element(to_bs(html))
        tag = Empty()

        with pytest.raises(TagNotFoundException):
            tag.find(bs, strict=True)

    def test_find_raises_exception_with_tag_if_not_found_in_strict_mode(self):
        """
        Tests if find method raises TagNotFoundException
        if no empty tag is found in strict mode when tag is specified.
        """
        html = """
            <div>
                <p>text 1</p>
                <p>text 2</p>
            </div>
            <span></span>
        """
        bs = find_body_element(to_bs(html))
        tag = Empty("p")

        with pytest.raises(TagNotFoundException):
            tag.find(bs, strict=True)

    def test_find_all_return_empty_list_if_no_empty_element_without_tag(self):
        """
        Tests if find_all method returns empty list
        if no empty tag is found, when tag is not specified.
        """
        html = """
            <div>
                <p>text 1</p>
                <p>text 2</p>
            </div>
            <div>Hello</div>
        """
        bs = find_body_element(to_bs(html))
        tag = Empty()
        result = tag.find_all(bs)
        assert result == []

    def test_find_all_return_empty_list_if_no_empty_element_with_tag(self):
        """
        Tests if find_all method returns empty list if no empty tag is found
        when tag is specified. Empty tag is skipped when its name does not match
        the tag, as in this case for 'span'.
        """
        html = """
            <div>
                <p>text 1</p>
                <p>text 2</p>
            </div>
            <span></span>
            <div>Hello</div>
        """
        bs = find_body_element(to_bs(html))
        tag = Empty("div")
        result = tag.find_all(bs)
        assert result == []

    def test_find_all_return_all_empty_elements_without_tag(self):
        """
        Tests if find_all method returns all empty tags, when tag is not specified.
        """
        html = """
            <div>
                <p></p>
            </div>
            <span></span>
            <span>
                <div><p>text 2</p></div>
            </span>
        """
        bs = find_body_element(to_bs(html))
        tag = Empty()
        result = tag.find_all(bs)
        assert list(map(str, result)) == [
            strip("<p></p>"),
            strip("""<span></span>"""),
        ]

    def test_find_all_return_all_empty_elements_with_tag(self):
        """
        Tests if find_all method returns all empty tags which name matches
        the specified tag.
        """
        html = """
            <div></div>
            <span></span>
            <span>  </span>
            <div></div>
            <div>Hello</div>
        """
        bs = find_body_element(to_bs(html))
        tag = Empty("div")
        result = tag.find_all(bs)
        assert list(map(str, result)) == [
            strip("<div></div>"),
            strip("<div></div>"),
        ]

    def test_self_closing_tag_is_always_empty(self):
        """
        Tests if self closing tag like ex. image always matches the Empty tag.
        Closing tags do not allow children or text.
        """
        html = """
            <img src="picture.jpg"/>
            <div>Hello</div>
        """
        bs = find_body_element(to_bs(html))
        tag = Empty()
        result = tag.find(bs)
        assert str(result) == strip("""<img src="picture.jpg"/>""")
