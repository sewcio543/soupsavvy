"""Module with unit tests for NthLastOfType css tag selector."""

from itertools import chain

import pytest

from soupsavvy.exceptions import InvalidCSSSelector, TagNotFoundException
from soupsavvy.selectors.css.selectors import NthLastOfType
from tests.soupsavvy.selectors.conftest import find_body_element, strip, to_bs


@pytest.mark.css
@pytest.mark.selector
class TestNthLastOfType:
    """Class with unit tests for NthLastOfType tag selector."""

    def test_css_selector_is_correct(self):
        """Tests if selector property returns correct value."""
        assert NthLastOfType("2n").css == ":nth-last-of-type(2n)"

    def test_find_all_returns_all_tags_for_selector_without_tag_name(self):
        """Tests if find_all method returns all tags for selector without tag name."""
        text = """
            <div></div>
            <a class="widget">1</a>
            <div>2</div>
            <a>Hello</a>
            <div>
                <p><a>3</a><span></span></p>
                <p class="widget">Hello</p>
                <a>Hello</a>
                <span><a>4</a><a></a></span>
            </div>
            <a>5</a>
            <a>Hello</a>
        """
        bs = find_body_element(to_bs(text))
        selector = NthLastOfType("2n")
        result = selector.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="widget">1</a>"""),
            strip("""<div>2</div>"""),
            strip("""<p><a>3</a><span></span></p>"""),
            strip("""<a>4</a>"""),
            strip("""<a>5</a>"""),
        ]

    def test_find_returns_first_tag_matching_selector(self):
        """Tests if find method returns first tag matching selector."""
        text = """
            <div></div>
            <a class="widget">1</a>
            <div>2</div>
            <a>Hello</a>
            <div>
                <p><a>3</a><span></span></p>
                <p class="widget">Hello</p>
                <a>Hello</a>
                <span><a>4</a><a></a></span>
            </div>
            <a>5</a>
            <a>Hello</a>
        """
        bs = to_bs(text)
        selector = NthLastOfType("2n")
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<a class="widget">1</a>""")

    def test_find_returns_none_if_no_match_and_strict_false(self):
        """
        Tests if find returns None if no element matches the selector
        and strict is False.
        """
        text = """
            <div>
                <a></a>
                <p><a></a></p>
            </div>
            <p></p>
            <a></a>
        """
        bs = to_bs(text)
        selector = NthLastOfType("2n")
        result = selector.find(bs)
        assert result is None

    def test_find_raises_exception_if_no_match_and_strict_true(self):
        """
        Tests if find raises TagNotFoundException if no element matches the selector
        and strict is True.
        """
        text = """
            <div>
                <a></a>
                <p><a></a></p>
            </div>
            <p></p>
            <a></a>
        """
        bs = to_bs(text)
        selector = NthLastOfType("2n")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_all_returns_empty_list_when_no_match(self):
        """Tests if find returns an empty list if no element matches the selector."""
        text = """
            <div>
                <a></a>
                <p><a></a></p>
            </div>
            <p></p>
            <a></a>
        """
        bs = to_bs(text)
        selector = NthLastOfType("2n")
        result = selector.find_all(bs)
        assert result == []

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        text = """
            <div>
                <p><a>Not child</a><span></span></p>
                <p class="widget">Hello</p>
                <a>Hello</a>
                <span><a>Not child</a><a></a></span>
            </div>
            <div>1</div>
            <a class="widget">2</a>
            <div>Hello</div>
            <a>Hello</a>
            <a>3</a>
            <a>Hello</a>
        """
        bs = find_body_element(to_bs(text))
        selector = NthLastOfType("2n")
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<div>1</div>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div>
                <a>Not child</a>
                <a></a>
            </div>
            <p></p>
            <a></a>
        """
        bs = find_body_element(to_bs(text))
        selector = NthLastOfType("2n")
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <div>
                <a>Not child</a>
                <a></a>
            </div>
            <p></p>
            <a></a>
        """
        bs = find_body_element(to_bs(text))
        selector = NthLastOfType("3n")

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
            <div>
                <a>Not child</a>
                <a></a>
            </div>
            <p></p>
            <a></a>
        """
        bs = find_body_element(to_bs(text))
        selector = NthLastOfType("3n")
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <div>
                <p><a>Not child</a><span></span></p>
                <p class="widget">Hello</p>
                <a>Hello</a>
                <span><a>Not child</a><a></a></span>
            </div>
            <div>1</div>
            <a class="widget">2</a>
            <div>Hello</div>
            <a>Hello</a>
            <a><p>3</p></a>
            <a>Hello</a>
        """
        bs = find_body_element(to_bs(text))
        selector = NthLastOfType("2n")
        result = selector.find_all(bs, recursive=False)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div>1</div>"""),
            strip("""<a class="widget">2</a>"""),
            strip("""<a><p>3</p></a>"""),
        ]

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <div></div>
            <a class="widget">1</a>
            <div>2</div>
            <a>Hello</a>
            <div>
                <p><a>3</a><span></span></p>
                <p class="widget">Hello</p>
                <a>Hello</a>
                <span><a>4</a><a></a></span>
            </div>
            <a>5</a>
            <a>Hello</a>
        """
        bs = to_bs(text)
        selector = NthLastOfType("2n")
        result = selector.find_all(bs, limit=2)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="widget">1</a>"""),
            strip("""<div>2</div>"""),
        ]

    def test_find_all_returns_only_x_elements_when_limit_is_set_and_recursive_false(
        self,
    ):
        """
        Tests if find_all returns only x elements when limit is set and recursive
        is False. In this case only 2 first in order children matching
        the selector are returned.
        """
        text = """
            <div>
                <p><a>Not child</a><span></span></p>
                <p class="widget">Hello</p>
                <a>Hello</a>
                <span><a>Not child</a><a></a></span>
            </div>
            <div>1</div>
            <a class="widget">2</a>
            <div>Hello</div>
            <a>Hello</a>
            <a>3</a>
            <a>Hello</a>
        """
        bs = find_body_element(to_bs(text))
        selector = NthLastOfType("2n")
        result = selector.find_all(bs, recursive=False, limit=2)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div>1</div>"""),
            strip("""<a class="widget">2</a>"""),
        ]

    def test_init_raise_exception_with_invalid_selector(self):
        """
        Tests if init raise InvalidCSSSelector exception
        if invalid n parameter is passed into the selector.
        """
        with pytest.raises(InvalidCSSSelector):
            NthLastOfType("2x+1")

    @pytest.mark.parametrize(
        argnames="nth, expected",
        argvalues=[
            ("2n", [1, 3, 5]),
            ("2n+1", [2, 4, 6]),
            # ignores whitespaces
            ("  2n  + 1", [2, 4, 6]),
            ("-n+3", [4, 5, 6]),
            ("even", [1, 3, 5]),
            ("odd", [2, 4, 6]),
            ("3", [4]),
            ("-3n", []),
            ("-3n+10", [3, 6]),
        ],
    )
    def test_returns_elements_based_on_nth_selector(
        self, nth: str, expected: list[int]
    ):
        """
        Tests if find_all returns all elements with specified tag name
        matching various nth selectors.
        """
        text = """
            <p>text 1</p>
            <a>text 1</a>
            <p>text 2</p>
            <a>text 2</a>
            <p>text 3</p>
            <a>text 3</a>
            <p>text 4</p>
            <a>text 4</a>
            <p>text 5</p>
            <a>text 5</a>
            <p>text 6</p>
            <a>text 6</a>
        """
        bs = find_body_element(to_bs(text))
        selector = NthLastOfType(nth)
        results = selector.find_all(bs)
        assert list(map(lambda x: strip(str(x)), results)) == list(
            chain.from_iterable(
                [(f"""<p>text {i}</p>""", f"""<a>text {i}</a>""") for i in expected]
            )
        )
