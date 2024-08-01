"""Module with unit tests for NthChild css tag selector."""

import pytest

from soupsavvy.exceptions import InvalidCSSSelector, TagNotFoundException
from soupsavvy.tags.css.tag_selectors import NthChild
from tests.soupsavvy.tags.conftest import find_body_element, strip, to_bs


@pytest.mark.css_selector
@pytest.mark.soup
class TestNthChild:
    """Class with unit tests for NthChild tag selector."""

    def test_selector_is_correct_without_tag(self):
        """
        Tests if selector property returns correct value without specifying tag.
        """
        assert NthChild(n="2n").selector == ":nth-child(2n)"

    def test_selector_is_correct_with_tag(self):
        """Tests if selector property returns correct value when specifying tag."""
        assert NthChild(n="2n", tag="div").selector == "div:nth-child(2n)"

    def test_find_all_returns_all_tags_for_selector_without_tag_name(self):
        """Tests if find_all method returns all tags for selector without tag name."""
        text = """
            <div></div>
            <a class="widget">1</a>
            <div>
                <p>Hello</p>
                <p class="widget">2</p>
                <a>Hello</a>
                <span><a>3</a><p>4</p></span>
            </div>
            <div>5</div>
        """
        bs = find_body_element(to_bs(text))
        selector = NthChild("2n")
        result = selector.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="widget">1</a>"""),
            strip("""<p class="widget">2</p>"""),
            strip("""<span><a>3</a><p>4</p></span>"""),
            strip("""<p>4</p>"""),
            strip("""<div>5</div>"""),
        ]

    def test_find_all_returns_all_tags_for_selector_with_tag_name(self):
        """Tests if find_all method returns all tags for selector with tag name."""
        text = """
            <div></div>
            <a class="widget">Not p</a>
            <div>
                <p>Hello</p>
                <p class="widget">1</p>
                <a>Hello</a>
                <span><a></a><p>2</p></span>
            </div>
            <div>Not p</div>
        """
        bs = find_body_element(to_bs(text))
        selector = NthChild("2n", tag="p")
        result = selector.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<p class="widget">1</p>"""),
            strip("""<p>2</p>"""),
        ]

    def test_find_returns_first_tag_matching_selector(self):
        """Tests if find method returns first tag matching selector."""
        text = """
            <div></div>
            <div>1</div>
            <div>
                <a></a>
                <p><a>2</a></p>
                <span></span>
            </div>
            <span>3</span>
            <a class="widget"></a>
            <div><a></a><p>45</p></div>
        """
        bs = to_bs(text)
        selector = NthChild("2n")
        result = selector.find(bs)
        assert strip(str(result)) == strip("""<div>1</div>""")

    def test_find_returns_none_if_no_match_and_strict_false(self):
        """
        Tests if find returns None if no element matches the selector
        and strict is False.
        """
        text = """
            <div></div>
            <div><p></p><a></a></div>
        """
        bs = to_bs(text)
        selector = NthChild("3n")
        result = selector.find(bs)
        assert result is None

    def test_find_raises_exception_if_no_match_and_strict_true(self):
        """
        Tests if find raises TagNotFoundException if no element matches the selector
        and strict is True.
        """
        text = """
            <div></div>
            <div><p></p><a></a></div>
        """
        bs = to_bs(text)
        selector = NthChild("3n")

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True)

    def test_find_all_returns_empty_list_when_no_match(self):
        """Tests if find returns an empty list if no element matches the selector."""
        text = """
            <div></div>
            <div><p></p><a></a></div>
        """
        bs = to_bs(text)
        selector = NthChild("3n")
        result = selector.find_all(bs)
        assert result == []

    def test_find_returns_first_matching_child_if_recursive_false(self):
        """
        Tests if find returns first matching child element if recursive is False.
        """
        text = """
            <div>
                <a></a>
                <p><a>Not child</a></p>
                <span></span>
            </div>
            <div>1</div>
            <div></div>
            <span>2</span>
            <a class="widget"></a>
            <div><a></a><p>34</p></div>
        """
        bs = find_body_element(to_bs(text))
        selector = NthChild("2n")
        result = selector.find(bs, recursive=False)
        assert strip(str(result)) == strip("""<div>1</div>""")

    def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
        """
        Tests if find returns None if no child element matches the selector
        and recursive is False.
        """
        text = """
            <div><p></p><a></a><p>Not child</p></div>
            <div></div>
        """
        bs = find_body_element(to_bs(text))
        selector = NthChild("3n")
        result = selector.find(bs, recursive=False)
        assert result is None

    def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
        """
        Tests if find raises TagNotFoundException if no child element
        matches the selector, when recursive is False and strict is True.
        """
        text = """
            <div><p></p><a></a><p>Not child</p></div>
            <div></div>
        """
        bs = find_body_element(to_bs(text))
        selector = NthChild("3n")

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
            <div><p></p><a></a><p>Not child</p></div>
            <div></div>
        """
        bs = find_body_element(to_bs(text))
        selector = NthChild("3n")
        result = selector.find_all(bs, recursive=False)
        assert result == []

    def test_find_all_returns_all_matching_children_when_recursive_false(self):
        """
        Tests if find_all returns all matching children if recursive is False.
        It returns only matching children of the body element.
        """
        text = """
            <div>
                <a></a>
                <p><a>Not child</a></p>
                <span></span>
            </div>
            <div>1</div>
            <div></div>
            <span>2</span>
            <a class="widget"></a>
            <div><a>3</a><p>Not child</p></div>
        """
        bs = find_body_element(to_bs(text))
        selector = NthChild("2n")
        result = selector.find_all(bs, recursive=False)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div>1</div>"""),
            strip("""<span>2</span>"""),
            strip("""<div><a>3</a><p>Not child</p></div>"""),
        ]

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <div></div>
            <a class="widget">1</a>
            <div>
                <p>Hello</p>
                <p class="widget">2</p>
                <a>Hello</a>
                <span><a>3</a><p>4</p></span>
            </div>
            <div>5</div>
        """
        bs = to_bs(text)
        selector = NthChild("2n")
        result = selector.find_all(bs, limit=2)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a class="widget">1</a>"""),
            strip("""<p class="widget">2</p>"""),
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
                <a></a>
                <p><a>Not child</a></p>
                <span></span>
            </div>
            <div>1</div>
            <div></div>
            <span>2</span>
            <a class="widget"></a>
            <div><a>3</a><p>Not child</p></div>
        """
        bs = find_body_element(to_bs(text))
        selector = NthChild("2n")
        result = selector.find_all(bs, recursive=False, limit=2)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<div>1</div>"""),
            strip("""<span>2</span>"""),
        ]

    def test_init_raise_exception_with_invalid_selector(self):
        """
        Tests if init raise InvalidCSSSelector exception
        if invalid n parameter is passed into the selector.
        """
        with pytest.raises(InvalidCSSSelector):
            NthChild("2x+1")

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
                <p>text 3</p>
                <p>text 4</p>
            </div>
            <span><p>text 5</p><p>text 6</p></span>
        """
        bs = find_body_element(to_bs(html))
        tag = NthChild(n)

        result = tag.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("<p>text 2</p>"),
            strip("<p>text 4</p>"),
            strip("<span><p>text 5</p><p>text 6</p></span>"),
            strip("<p>text 6</p>"),
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
                <p>text 5</p>
            </div>
        """
        bs = find_body_element(to_bs(html))
        tag = NthChild(n)

        result = tag.find_all(bs)
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("<span><p>text 1</p><p>text 2</p></span>"),
            strip("<p>text 1</p>"),
            strip("<p>text 3</p>"),
            strip("<p>text 5</p>"),
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
        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("<span><p>text 1</p><p>text 2</p></span>"),
            strip("<p>text 1</p>"),
            strip("<p>text 3</p>"),
        ]

    @pytest.mark.parametrize(
        argnames="nth, expected",
        argvalues=[
            ("2n", [2, 4, 6]),
            ("2n+1", [1, 3, 5]),
            ("-n+3", [1, 2, 3]),
            ("even", [2, 4, 6]),
            ("odd", [1, 3, 5]),
            ("3", [3]),
            ("-3n", []),
            ("-3n+10", [1, 4]),
        ],
    )
    def test_returns_elements_based_on_nth_selector_and_tag(
        self, nth: str, expected: list[int]
    ):
        """
        Tests if find_all returns all elements with specified tag name
        matching various nth selectors.
        """
        text = """
            <div class="widget">1</div>
            <div class="widget">2</div>
            <div class="widget">3</div>
            <div class="widget">4</div>
            <div class="widget">5</div>
            <div class="widget">6</div>
            <a>Hello</a>
            <span>Hello</span>
            <p></p>
        """
        bs = find_body_element(to_bs(text))
        selector = NthChild(nth, tag="div")
        results = selector.find_all(bs)

        assert list(map(lambda x: strip(str(x)), results)) == [
            f"""<div class="widget">{i}</div>""" for i in expected
        ]

    @pytest.mark.parametrize(
        argnames="nth, expected",
        argvalues=[
            ("2n", [2, 4, 6]),
            ("2n+1", [1, 3, 5]),
            ("-n+3", [1, 2, 3]),
            ("even", [2, 4, 6]),
            ("odd", [1, 3, 5]),
            ("3", [3]),
            ("-3n", []),
            ("-3n+10", [1, 4]),
        ],
    )
    def test_returns_elements_based_on_nth_selector(
        self, nth: str, expected: list[int]
    ):
        """Tests if find_all returns all elements matching various nth selectors."""
        text = """
            <div class="widget">1</div>
            <div class="widget">2</div>
            <div class="widget">3</div>
            <div class="widget">4</div>
            <div class="widget">5</div>
            <div class="widget">6</div>
        """
        bs = find_body_element(to_bs(text))
        selector = NthChild(nth)
        results = selector.find_all(bs)

        assert list(map(lambda x: strip(str(x)), results)) == [
            f"""<div class="widget">{i}</div>""" for i in expected
        ]
