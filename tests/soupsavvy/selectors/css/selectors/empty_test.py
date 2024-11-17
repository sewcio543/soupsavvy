"""Module with unit tests for Empty css selector."""

import pytest

from soupsavvy.exceptions import TagNotFoundException
from soupsavvy.selectors.css.selectors import Empty
from tests.soupsavvy.conftest import ToElement, strip


@pytest.mark.css
@pytest.mark.selector
class TestEmpty:
    """Class with unit tests for Empty selector."""

    def test_css_selector_is_correct(self):
        """Tests if css property returns correct value."""
        assert Empty().css == ":empty"

    def test_find_all_returns_all_elements_matching_selector(
        self, to_element: ToElement
    ):
        """Tests if find_all method returns all elements matching selector."""
        text = """
            <div>Hello</div>
            <div></div>
            <div>
                <p>text 1</p>
                <p class="empty"></p>
            </div>
            <a class="widget"></a>
            <span><a>Hello</a></span>
        """
        bs = to_element(text)
        selector = Empty()
        result = selector.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div></div>"""),
            strip("""<p class="empty"></p>"""),
            strip("""<a class="widget"></a>"""),
        ]

    def test_find_returns_first_element_matching_selector(self, to_element: ToElement):
        """Tests if find method returns first element matching selector."""
        text = """
            <div></div>
            <span><a></a></span>
            <a class="widget"></a>
            <br/>
        """
        bs = to_element(text)
        selector = Empty()
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<div></div>""")

    def test_find_returns_none_if_no_match_and_strict_false(
        self, to_element: ToElement
    ):
        """
        Tests if find returns None if no element matches the selector
        and strict is False.
        """
        text = """
            <div>Hello</div>
            <a><p>Hello</p></a>
            <span><a>Hello</a></span>
            <div>
                <p>text 1</p>
                <p>text 2</p>
            </div>
        """
        bs = to_element(text)
        selector = Empty()
        result = selector.find(bs)
        assert result is None

    def test_find_raises_exception_if_no_match_and_strict_true(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find raises TagNotFoundException if no element matches the selector
        and strict is True.
        """
        text = """
            <div>Hello</div>
            <a><p>Hello</p></a>
            <span><a>Hello</a></span>
            <div>
                <p>text 1</p>
                <p>text 2</p>
            </div>
        """
        bs = to_element(text)
        selector = Empty()

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_all_returns_empty_list_when_no_match(self, to_element: ToElement):
        """Tests if find returns an empty list if no element matches the selector."""
        text = """
            <div>Hello</div>
            <a><p>Hello</p></a>
            <span><a>Hello</a></span>
            <div>
                <p>text 1</p>
                <p>text 2</p>
            </div>
        """
        bs = to_element(text)
        selector = Empty()
        result = selector.find_all(bs)
        assert result == []

    def test_find_returns_first_matching_child_if_recursive_false(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        text = """
            <div>Hello</div>
            <div>
                <p>text 1</p>
                <p class="empty"></p>
            </div>
            <div></div>
            <span><a>Hello</a></span>
            <a class="widget"></a>
        """
        bs = to_element(text)
        selector = Empty()
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<div></div>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div>Hello</div>
            <div>
                <p>text 1</p>
                <p class="empty"></p>
                <img src="picture.jpg"/>
            </div>
            <span><a>Hello</a></span>
        """
        bs = to_element(text)
        selector = Empty()
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <div>Hello</div>
            <div>
                <p>text 1</p>
                <p class="empty"></p>
                <img src="picture.jpg"/>
            </div>
            <span><a>Hello</a></span>
        """
        bs = to_element(text)
        selector = Empty()

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True, recursive=False)

    def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find_all returns an empty list if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div>Hello</div>
            <div>
                <p>text 1</p>
                <p class="empty"></p>
                <img src="picture.jpg"/>
            </div>
            <span><a>Hello</a></span>
        """
        bs = to_element(text)
        selector = Empty()
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_all_matching_children_when_recursive_false(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <div>Hello</div>
            <div>
                <p>text 1</p>
                <p class="empty"></p>
            </div>
            <div></div>
            <span><a>Hello</a></span>
            <a class="widget"></a>
            <p class="empty"></p>
        """
        bs = to_element(text)
        selector = Empty()
        result = selector.find_all(bs, recursive=False)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div></div>"""),
            strip("""<a class="widget"></a>"""),
            strip("""<p class="empty"></p>"""),
        ]

    def test_find_all_returns_only_x_elements_when_limit_is_set(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <div>Hello</div>
            <div></div>
            <div>
                <p>text 1</p>
                <p class="empty"></p>
            </div>
            <a class="widget"></a>
            <span><a>Hello</a></span>
            <img src="picture.jpg"/>
            <br/>
        """
        bs = to_element(text)
        selector = Empty()
        result = selector.find_all(bs, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div></div>"""),
            strip("""<p class="empty"></p>"""),
        ]

    def test_find_all_returns_only_x_elements_when_limit_is_set_and_recursive_false(
        self,
        to_element: ToElement,
    ):
        """
        Tests if find_all returns only x elements when limit is set and recursive
        is False. In this case only 2 first in order children matching
        the selector are returned.
        """
        text = """
            <div>Hello</div>
            <div>
                <p>text 1</p>
                <p class="empty"></p>
            </div>
            <div></div>
            <span><a>Hello</a></span>
            <a class="widget"></a>
            <img src="picture.jpg"/>
        """
        bs = to_element(text)
        selector = Empty()
        result = selector.find_all(bs, recursive=False, limit=2)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div></div>"""),
            strip("""<a class="widget"></a>"""),
        ]
