"""Module with unit tests for FirstChild css tag selector."""

import pytest

from soupsavvy.tags.css.tag_selectors import FirstChild
from soupsavvy.tags.exceptions import TagNotFoundException
from tests.soupsavvy.tags.conftest import find_body_element, strip, to_bs


@pytest.mark.css_selector
@pytest.mark.soup
class TestFirstChild:
    """Class with unit tests for FirstChild tag selector."""

    def test_selector_is_correct_without_tag(self):
        """Tests if selector property returns correct value without specifying tag."""
        assert FirstChild().selector == ":first-child"

    def test_selector_is_correct_with_tag(self):
        """Tests if selector property returns correct value when specifying tag."""
        assert FirstChild("a").selector == "a:first-child"

    def test_finds_always_return_first_element_without_tag(self):
        """
        Tests if find method returns first child when tag is not specified.
        It should never return None when tag is not specified,
        as there is always a first child,
        so tests for None or raising exception are not needed.
        """
        html = """
            <div><p>text</p></div>
            <div></div>
        """
        bs = find_body_element(to_bs(html))
        tag = FirstChild()
        result = tag.find(bs)
        assert strip(str(result)) == strip("<div><p>text</p></div>")

    def test_find_returns_none_if_no_first_child_with_specified_tag(self):
        """
        Tests if find method returns None if specified tag is not present
        as the first child in the tag markup. In this case, 'span' and 'p' (first children)
        are not matching specified tag 'div'.
        """
        html = """
            <span>
                <p>text</p>
                <div>text</div>
            </span>
            <div></div>
        """
        bs = find_body_element(to_bs(html))
        tag = FirstChild("div")
        result = tag.find(bs)
        assert result is None

    def test_find_returns_none_if_tag_not_present(self):
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
        tag = FirstChild("span")
        result = tag.find(bs)
        assert result is None

    def test_find_returns_first_first_child_with_tag(self):
        """
        Tests if find method returns first first child that matches the specified tag.
        Even though p is the first child, it is skipped because
        it does not match the specified tag. First 'a' tag which is first child
        of parent should be selected.
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
        tag = FirstChild("a")
        result = tag.find(bs)
        assert strip(str(result)) == strip("<a>text 3</a>")

    def test_find_raises_exception_if_not_found_in_strict_mode(self):
        """
        Tests if find method raises TagNotFoundException
        if no first child is found in strict mode. It only makes sense
        to test for exception when tag is specified, as there is always
        a first child when tag is not specified.
        """
        html = """
            <div>
                <p>text 1</p>
                <p>text 2</p>
            </div>
            <span>Hello</span>
        """
        bs = find_body_element(to_bs(html))
        tag = FirstChild("span")

        with pytest.raises(TagNotFoundException):
            tag.find(bs, strict=True)

    def test_find_all_returns_empty_list_if_no_first_child_with_tag(self):
        """
        Tests if find_all method returns empty list if no first child is found
        when tag is specified. First child is skipped when
        its name does not match the tag.
        """
        html = """
            <span><p>text 1</p></span>
            <div>
                <a>text 2</a>
                <div>Hello 1</div>
            </div>
        """
        bs = find_body_element(to_bs(html))
        tag = FirstChild("div")
        result = tag.find_all(bs)
        assert result == []

    def test_find_all_returns_all_first_children_without_tag(self):
        """
        Tests if find_all method returns all first children when tag is not specified.
        """
        html = """
            <div><p>text 1</p></div>
            <span>
                <div><p>text 2</p><p>text 3</p></div>
            </span>
        """
        bs = find_body_element(to_bs(html))
        tag = FirstChild()
        result = tag.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("<div><p>text 1</p></div>"),
            strip("<p>text 1</p>"),
            strip("<div><p>text 2</p><p>text 3</p></div>"),
            strip("<p>text 2</p>"),
        ]

    def test_find_all_returns_all_first_children_with_tag(self):
        """
        Tests if find_all method returns all first children which name matches
        the specified tag.
        """
        html = """
            <div><p>text 1</p></div>
            <div>
                <a>text 2</a>
                <div>Hello 1</div>
            </div>
            <div>
                <div>Hello 2</div>
                <a>text 3</a>
            </div>
        """
        bs = find_body_element(to_bs(html))
        tag = FirstChild("div")
        result = tag.find_all(bs)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("<div><p>text 1</p></div>"),
            strip("<div>Hello 2</div>"),
        ]
