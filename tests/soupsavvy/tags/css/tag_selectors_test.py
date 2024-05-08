"""Module with unit tests for css tag selectors."""

import pytest

from soupsavvy.tags.css.exceptions import InvalidCSSSelector
from soupsavvy.tags.css.tag_selectors import (
    Empty,
    FirstChild,
    LastChild,
    NthChild,
    OnlyChild,
)
from soupsavvy.tags.exceptions import TagNotFoundException
from tests.soupsavvy.tags.conftest import find_body_element, strip, to_bs


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
        assert str(result) == strip("<div><p>text</p></div>")

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
        assert str(result) == strip("<a>text 3</a>")

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
        assert list(map(str, result)) == [
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

        assert list(map(str, result)) == [
            strip("<div><p>text 1</p></div>"),
            strip("<div>Hello 2</div>"),
        ]


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
        so no nth child is found.
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
        assert str(result) == strip("<p>text 2</p>")

    def test_find_returns_first_nth_child_with_tag(self):
        """
        Tests if find method returns first nth child which name matches
        the specified tag. Even though 'p' and 'span' are the second child, they are skipped
        because they do not match the specified tag.
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
        assert str(result) == strip("<div>Hello 2</div>")

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
        Tests if find method raises InvalidCSSSelector exception
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
        assert list(map(str, result)) == [
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

        assert list(map(str, result)) == [
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
            </div>
            <span><p>text 3</p><p>text 4</p></span>
        """
        bs = find_body_element(to_bs(html))
        tag = NthChild(n)

        result = tag.find_all(bs)
        assert list(map(str, result)) == [
            strip("<p>text 2</p>"),
            strip("<span><p>text 3</p><p>text 4</p></span>"),
            strip("<p>text 4</p>"),
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
            </div>
        """
        bs = find_body_element(to_bs(html))
        tag = NthChild(n)

        result = tag.find_all(bs)
        assert list(map(str, result)) == [
            strip("<span><p>text 1</p><p>text 2</p></span>"),
            strip("<p>text 1</p>"),
            strip("<p>text 3</p>"),
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
        assert list(map(str, result)) == [
            strip("<span><p>text 1</p><p>text 2</p></span>"),
            strip("<p>text 1</p>"),
            strip("<p>text 3</p>"),
        ]
