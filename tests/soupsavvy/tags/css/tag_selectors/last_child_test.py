"""Module with unit tests for LastChild css tag selector."""

import pytest

from soupsavvy.exceptions import TagNotFoundException
from soupsavvy.tags.css.tag_selectors import LastChild
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
        assert LastChild("div").selector == "div:last-child"

    def test_find_all_returns_all_tags_for_selector_without_tag_name(self):
        """Tests if find_all method returns all tags for selector without tag name."""
        text = """
            <div></div>
            <div>
                <p></p>
                <p class="widget">1<a></a><a>2</a></p>
            </div>
            <span><a class="menu">34</a></span>
        """
        bs = find_body_element(to_bs(text))
        selector = LastChild()
        result = selector.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<p class="widget">1<a></a><a>2</a></p>"""),
            strip("""<a>2</a>"""),
            strip("""<span><a class="menu">34</a></span>"""),
            strip("""<a class="menu">34</a>"""),
        ]

    def test_find_all_returns_all_tags_for_selector_with_tag_name(self):
        """Tests if find_all method returns all tags for selector with tag name."""
        text = """
            <div></div>
            <div>
                <div><a></a><div>1</div></div>
                <div class="menu">2</div>
            </div>
            <div>
                <p>Hello</p>
                <span class="widget">
                    <a class="widget"></a>
                    <div>3</div>
                </span>
            </div>
            <span><a></a></span>
            <div><a>4</a></div>
        """
        bs = find_body_element(to_bs(text))
        selector = LastChild("div")
        result = selector.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div>1</div>"""),
            strip("""<div class="menu">2</div>"""),
            strip("""<div>3</div>"""),
            strip("""<div><a>4</a></div>"""),
        ]

    def test_find_returns_first_tag_matching_selector(self):
        """Tests if find method returns first tag matching selector."""
        text = """
            <div>Hello</div>
            <div>
                <a>Hello</a>
                <p class="widget"></p>
                <a>1</a>
            </div>
            <span><a>2</a></span>
            <a class="widget">Hello</a>
            <div><a>Hello</a><a><p>3</p></a></div>
        """
        bs = to_bs(text)
        selector = LastChild("a")
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<a>1</a>""")

    def test_find_returns_none_if_no_match_and_strict_false(self):
        """
        Tests if find returns None if no element matches the selector
        and strict is False.
        """
        text = """
            <div></div>
            <div>
                <a>Hello</a>
                <p class="widget"></p>
            </div>
            <a class="widget"></a>
            <span><a></a><p>Hello</p></span>
        """
        bs = to_bs(text)
        selector = LastChild("a")
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
                <a>Hello</a>
                <p class="widget"></p>
            </div>
            <a class="widget"></a>
            <span><a></a><p>Hello</p></span>
        """
        bs = to_bs(text)
        selector = LastChild("a")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_all_returns_empty_list_when_no_match(self):
        """Tests if find returns an empty list if no element matches the selector."""
        text = """
            <div></div>
            <div>
                <a>Hello</a>
                <p class="widget"></p>
            </div>
            <a class="widget"></a>
            <span><a></a><p>Hello</p></span>
        """
        bs = to_bs(text)
        selector = LastChild("a")
        result = selector.find_all(bs)
        assert result == []

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        text = """
            <div>Hello</div>
            <div>
                <a>Hello</a>
                <p class="widget"></p>
                <a>Not child</a>
            </div>
            <span><a>Not child</a></span>
            <a class="widget">Hello</a>
            <a>1</a>
        """
        bs = find_body_element(to_bs(text))
        selector = LastChild("a")
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<a>1</a>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div>Hello</div>
            <div>
                <a>Hello</a>
                <p class="widget"></p>
                <a>Not child</a>
            </div>
            <a class="widget">Hello</a>
            <span><a>Not child</a></span>
        """
        bs = find_body_element(to_bs(text))
        selector = LastChild("a")
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <div>Hello</div>
            <div>
                <a>Hello</a>
                <p class="widget"></p>
                <a>Not child</a>
            </div>
            <a class="widget">Hello</a>
            <span><a>Not child</a></span>
        """
        bs = find_body_element(to_bs(text))
        selector = LastChild("a")

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
            <div>Hello</div>
            <div>
                <a>Hello</a>
                <p class="widget"></p>
                <a>Not child</a>
            </div>
            <a class="widget">Hello</a>
            <span><a>Not child</a></span>
        """
        bs = find_body_element(to_bs(text))
        selector = LastChild("a")
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <div>Hello</div>
            <div>
                <a>Hello</a>
                <p class="widget"></p>
                <a>Not child</a>
            </div>
            <span><a>Not child</a></span>
            <a class="widget">Hello</a>
            <a>1</a>
        """
        bs = find_body_element(to_bs(text))
        selector = LastChild()
        result = selector.find_all(bs, recursive=False)
        # at most one element can be returned
        assert list(map(lambda x: strip(str(x)), result)) == [strip("""<a>1</a>""")]

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <div>Hello</div>
            <div>
                <a>Hello</a>
                <p class="widget"></p>
                <a>1</a>
            </div>
            <span><a>2</a></span>
            <a class="widget">Hello</a>
            <div><a>Hello</a><a><p>3</p></a></div>
        """
        bs = find_body_element(to_bs(text))
        selector = LastChild("a")
        result = selector.find_all(bs, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a>1</a>"""),
            strip("""<a>2</a>"""),
        ]
