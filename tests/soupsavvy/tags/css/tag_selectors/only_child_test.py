"""Module with unit tests for OnlyChild css tag selector."""

import pytest

from soupsavvy.tags.css.tag_selectors import OnlyChild
from soupsavvy.tags.exceptions import TagNotFoundException
from tests.soupsavvy.tags.conftest import find_body_element, strip, to_bs


@pytest.mark.css_selector
@pytest.mark.soup
class TestOnlyChild:
    """Class with unit tests for OnlyChild tag selector."""

    def test_selector_is_correct_without_tag(self):
        """Tests if selector property returns correct value without specifying tag."""
        assert OnlyChild().selector == ":only-child"

    def test_selector_is_correct_with_tag(self):
        """Tests if selector property returns correct value when specifying tag."""
        assert OnlyChild("div").selector == "div:only-child"

    def test_finds_returns_none_if_no_only_child_without_tag(self):
        """
        Tests if find method returns None if no only child is found
        when tag is not specified and strict mode is not enabled.
        """
        html = """
            <div>
                <p>text</p>
                <p>text</p>
            </div>
            <div></div>
        """
        bs = find_body_element(to_bs(html))
        tag = OnlyChild()
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
        tag = OnlyChild("span")
        result = tag.find(bs)
        assert result is None

    def test_find_returns_none_if_no_only_child_with_tag(self):
        """
        Tests if find method returns None if no only child is found
        when tag is specified and strict mode is not enabled.
        Only child is skipped when its name does not match the tag,
        as in this case for 'p'.
        """
        # p is the only child, but selector has specified div tag
        html = """
            <div>
                <p>text</p>
            </div>
            <div></div>
        """
        bs = find_body_element(to_bs(html))
        tag = OnlyChild("div")
        result = tag.find(bs)
        assert result is None

    def test_find_returns_first_only_child_without_tag(self):
        """
        Tests if find method returns first only child when tag is not specified.
        """
        html = """
            <div>
                <p>text 1</p>
            </div>
            <span>
                <p>text 2</p>
            </span>
        """
        bs = find_body_element(to_bs(html))
        tag = OnlyChild()
        result = tag.find(bs)
        assert str(result) == strip("<p>text 1</p>")

    def test_find_returns_first_only_child_with_tag(self):
        """
        Tests if find method returns first only child which name matches
        the specified tag. Even though p is the only child, it is skipped
        because it does not match the specified tag.
        """
        html = """
            <div>
                <p>text 1</p>
            </div>
            <span>
                <a>text 2</a>
            </span>
        """
        bs = find_body_element(to_bs(html))
        tag = OnlyChild("a")
        result = tag.find(bs)
        assert str(result) == strip("<a>text 2</a>")

    def test_find_raises_exception_without_specified_tag_if_not_found_in_strict_mode(
        self,
    ):
        """
        Tests if find method raises TagNotFoundException
        if no only child is found in strict mode when tag is not specified.
        """
        html = """
            <div>
                <p>text 1</p>
                <p>text 2</p>
            </div>
            <span>Hello</span>
        """
        bs = find_body_element(to_bs(html))
        tag = OnlyChild()

        with pytest.raises(TagNotFoundException):
            tag.find(bs, strict=True)

    def test_find_raises_exception_with_specified_tag_if_not_found_in_strict_mode(self):
        """
        Tests if find method raises TagNotFoundException
        if no only child is found in strict mode when tag is specified.
        """
        html = """
            <div>
                <p>text 1</p>
                <div>Hello</div>
            </div>
            <span>Hello</span>
        """
        bs = find_body_element(to_bs(html))
        tag = OnlyChild("div")

        with pytest.raises(TagNotFoundException):
            tag.find(bs, strict=True)

    def test_find_all_returns_empty_list_if_no_only_child_without_tag(self):
        """
        Tests if find_all method returns empty list
        if no only child is found, when tag is not specified.
        """
        html = """
            <div>
                <p>text 1</p>
                <p>text 2</p>
            </div>
            <div></div>
        """
        bs = find_body_element(to_bs(html))
        tag = OnlyChild()
        result = tag.find_all(bs)
        assert result == []

    def test_find_all_returns_empty_list_if_no_only_child_with_tag(self):
        """
        Tests if find_all method returns empty list if no only child is found
        when tag is specified. Only child is skipped when
        its name does not match the tag, as in this case for 'p'.
        """
        html = """
            <div>
                <p>text 1</p>
            </div>
            <div></div>
        """
        bs = find_body_element(to_bs(html))
        tag = OnlyChild("div")
        result = tag.find_all(bs)
        assert result == []

    def test_find_all_returns_all_only_children_without_tag(self):
        """
        Tests if find_all method returns all only children
        when tag is not specified.
        """
        html = """
            <div>
                <p>text 1</p>
            </div>
            <span>
                <div><p>text 2</p></div>
            </span>
        """
        bs = find_body_element(to_bs(html))
        tag = OnlyChild()
        result = tag.find_all(bs)
        assert list(map(str, result)) == [
            strip("<p>text 1</p>"),
            strip("<div><p>text 2</p></div>"),
            strip("<p>text 2</p>"),
        ]

    def test_find_all_returns_all_only_children_with_tag(self):
        """
        Tests if find_all method returns all only children
        which name matches the specified tag.
        """
        html = """
            <div><div><p>text 2</p></div></div>
        """
        bs = find_body_element(to_bs(html))
        tag = OnlyChild("div")
        result = tag.find_all(bs)
        assert list(map(str, result)) == [
            strip("<div><div><p>text 2</p></div></div>"),
            strip("<div><p>text 2</p></div>"),
        ]
