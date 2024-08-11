"""Module with unit tests for OnlyChild css tag selector."""

import pytest

from soupsavvy.exceptions import TagNotFoundException
from soupsavvy.selectors.css.selectors import OnlyChild
from tests.soupsavvy.selectors.conftest import find_body_element, strip, to_bs


@pytest.mark.css
@pytest.mark.selector
class TestOnlyChild:
    """Class with unit tests for OnlyChild tag selector."""

    def test_selector_is_correct_without_tag(self):
        """Tests if selector property returns correct value without specifying tag."""
        assert OnlyChild().css == ":only-child"

    def test_selector_is_correct_with_tag(self):
        """Tests if selector property returns correct value when specifying tag."""
        assert OnlyChild("div").css == "div:only-child"

    def test_find_all_returns_all_tags_for_selector_without_tag_name(self):
        """Tests if find_all method returns all tags for selector without tag name."""
        text = """
            <div></div>
            <div><p>1</p></div>
            <div><p>Hello</p><a></a></div>
            <span><a><p>3</p><p></p></a></span>
            <div>
                <span><a>3</a></span>
                <span></span>
            </div>
        """
        bs = find_body_element(to_bs(text))
        selector = OnlyChild()
        result = selector.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<p>1</p>"""),
            strip("""<a><p>3</p><p></p></a>"""),
            strip("""<a>3</a>"""),
        ]

    def test_find_all_returns_all_tags_for_selector_with_tag_name(self):
        """Tests if find_all method returns all tags for selector with tag name."""
        text = """
            <div></div>
            <div><p>1</p></div>
            <div><p>Hello</p><a></a></div>
            <span><a><p>3</p><p></p></a></span>
            <div>
                <span><a>3</a></span>
                <span></span>
            </div>
        """
        bs = find_body_element(to_bs(text))
        selector = OnlyChild("a")
        result = selector.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a><p>3</p><p></p></a>"""),
            strip("""<a>3</a>"""),
        ]

    def test_find_returns_first_tag_matching_selector(self):
        """Tests if find method returns first tag matching selector."""
        text = """
            <div></div>
            <div><p>1</p></div>
            <div><p>Hello</p><a></a></div>
            <span><a><p>3</p><p></p></a></span>
            <div>
                <span><a>3</a></span>
                <span></span>
            </div>
        """
        bs = find_body_element(to_bs(text))
        selector = OnlyChild()
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<p>1</p>""")

    def test_find_returns_none_if_no_match_and_strict_false(self):
        """
        Tests if find returns None if no element matches the selector
        and strict is False.
        """
        text = """
            <div></div>
            <div>
                <p class="widget"></p>
                <a>Hello</a>
            </div>
            <span><p>Hello</p><a></a></span>
        """
        bs = find_body_element(to_bs(text))
        selector = OnlyChild()
        result = selector.find(bs)
        assert result is None

    def test_find_raises_exception_if_no_match_and_strict_true(self):
        """
        Tests if find raises TagNotFoundException if no element matches the selector
        and strict is True.
        """
        text = """
            <div></div>
            <div>
                <p class="widget"></p>
                <a>Hello</a>
            </div>
            <span><p>Hello</p><a></a></span>
        """
        bs = find_body_element(to_bs(text))
        selector = OnlyChild()

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_all_returns_empty_list_when_no_match(self):
        """Tests if find returns an empty list if no element matches the selector."""
        text = """
            <div></div>
            <div>
                <p class="widget"></p>
                <a>Hello</a>
            </div>
            <span><p>Hello</p><a></a></span>
        """
        bs = find_body_element(to_bs(text))
        selector = OnlyChild()
        result = selector.find_all(bs)
        assert result == []

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        text = """
            <div><a>Not child</a></div>
        """
        bs = find_body_element(to_bs(text))
        selector = OnlyChild()
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<div><a>Not child</a></div>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div><a>Not child</a></div>
            <div></div>
        """
        bs = find_body_element(to_bs(text))
        selector = OnlyChild()
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <div><a>Not child</a></div>
            <div></div>
        """
        bs = find_body_element(to_bs(text))
        selector = OnlyChild()

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True, recursive=False)

    def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
        self,
    ):
        """
        Tests if find_all returns an empty list if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div><a>Not child</a></div>
            <div></div>
        """
        bs = find_body_element(to_bs(text))
        selector = OnlyChild()
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <div><a>Not child</a></div>
        """
        bs = find_body_element(to_bs(text))
        selector = OnlyChild()
        result = selector.find_all(bs, recursive=False)
        # at most one element can be returned
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div><a>Not child</a></div>""")
        ]

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <div></div>
            <div><p>1</p></div>
            <div><p>Hello</p><a></a></div>
            <span><a><p>3</p><p></p></a></span>
            <div>
                <span><a>3</a></span>
                <span></span>
            </div>
        """
        bs = find_body_element(to_bs(text))
        selector = OnlyChild()
        result = selector.find_all(bs, limit=2)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<p>1</p>"""),
            strip("""<a><p>3</p><p></p></a>"""),
        ]
