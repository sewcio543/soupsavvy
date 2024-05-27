"""Module with unit tests for LastChild css tag selector."""

import pytest

from soupsavvy.tags.css.tag_selectors import LastChild
from soupsavvy.tags.exceptions import TagNotFoundException
from tests.soupsavvy.tags.conftest import find_body_element, strip, to_bs


@pytest.mark.css_selector
@pytest.mark.soup
class TestLastChild:
    """Class with unit tests for LastChild tag selector."""

    def test_selector_is_correct_without_tag(self):
        """Tests if selector property returns correct value without specifying tag."""
        assert LastChild().selector == ":last-child"

    def test_selector_is_correct_with_tag(self):
        """Tests if selector property returns correct value when specifying tag."""
        assert LastChild("a").selector == "a:last-child"

    def test_finds_always_return_last_element_without_tag(self):
        """
        Tests if find method returns last child when tag is not specified.
        It should never return None when tag is not specified,
        as there is always a last child,
        so tests for None or raising exception are not needed.
        """
        html = """
            <div><p>text</p></div>
            <div>Hello</div>
        """
        bs = find_body_element(to_bs(html))
        tag = LastChild()
        result = tag.find(bs)
        assert str(result) == strip("<p>text</p>")

    def test_find_returns_none_if_no_last_child_with_specified_tag(self):
        """
        Tests if find method returns None if specified tag is not present
        as the last child in the tag markup. In this case, 'div' and 'a' (last children)
        are not matching specified tag 'span'.
        """
        html = """
            <span>
                <p>text</p>
                <a>text</a>
            </span>
            <div></div>
        """
        bs = find_body_element(to_bs(html))
        tag = LastChild("span")
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
        tag = LastChild("span")
        result = tag.find(bs)
        assert result is None

    def test_find_returns_first_last_child_with_tag(self):
        """
        Tests if find method returns first last child that matches the specified tag.
        Even though p and span are the last children, they are skipped because
        they do not match the specified tag. Last 'a' tag which is last child
        of parent should be selected.
        """
        html = """
            <div>
                <a>text 1</a>
                <p>text 2</p>
            </div>
            <span>
                <p>text 3</p>
                <a>text 4</a>
            </span>
        """
        bs = find_body_element(to_bs(html))
        tag = LastChild("a")
        result = tag.find(bs)
        assert str(result) == strip("<a>text 4</a>")

    def test_find_raises_exception_if_not_found_in_strict_mode(self):
        """
        Tests if find method raises TagNotFoundException
        if no last child is found in strict mode. It only makes sense
        to test for exception when tag is specified, as there is always
        a last child when tag is not specified.
        """
        html = """
            <div>
                <p>text 1</p>
                <p>text 2</p>
            </div>
            <span>Hello</span>
        """
        bs = find_body_element(to_bs(html))
        tag = LastChild("div")

        with pytest.raises(TagNotFoundException):
            tag.find(bs, strict=True)

    def test_find_all_returns_empty_list_if_no_last_child_with_tag(self):
        """
        Tests if find_all method returns empty list if no last child is found
        when tag is specified. Last child is skipped when
        its name does not match the tag.
        """
        html = """
            <span><p>text 1</p></span>
            <div>
                <div>Hello 1</div>
                <a>text 2</a>
            </div>
            <a>text 3</a>
        """
        bs = find_body_element(to_bs(html))
        tag = LastChild("div")
        result = tag.find_all(bs)
        assert result == []

    def test_find_all_returns_all_last_children_without_tag(self):
        """
        Tests if find_all method returns all last children when tag is not specified.
        """
        html = """
            <span>
                <div><p>text 1</p><p>text 2</p></div>
            </span>
            <div><p>text 3</p></div>
        """
        bs = find_body_element(to_bs(html))
        tag = LastChild()
        result = tag.find_all(bs)
        assert list(map(str, result)) == [
            strip("<div><p>text 1</p><p>text 2</p></div>"),
            strip("<p>text 2</p>"),
            strip("<div><p>text 3</p></div>"),
            strip("<p>text 3</p>"),
        ]

    def test_find_all_returns_all_last_children_with_tag(self):
        """
        Tests if find_all method returns all last children which name matches
        the specified tag.
        """
        html = """
            <div>
                <a>text 1</a>
                <div>Hello 1</div>
            </div>
            <div>
                <div>Hello 2</div>
                <a>text 2</a>
            </div>
            <div><p>text 3</p></div>
        """
        bs = find_body_element(to_bs(html))
        tag = LastChild("div")
        result = tag.find_all(bs)

        assert list(map(str, result)) == [
            strip("<div>Hello 1</div>"),
            strip("<div><p>text 3</p></div>"),
        ]
