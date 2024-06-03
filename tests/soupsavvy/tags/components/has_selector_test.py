"""Testing module for ChildCombinator class."""

import pytest

from soupsavvy.tags.components import HasSelector
from soupsavvy.tags.exceptions import NotSelectableSoupException, TagNotFoundException
from soupsavvy.tags.relative import RelativeChild
from tests.soupsavvy.tags.conftest import (
    MockDivSelector,
    MockLinkSelector,
    find_body_element,
    strip,
    to_bs,
)


@pytest.mark.soup
class TestHasSelector:
    """Class for HasSelector unit test suite."""

    def test_raises_exception_when_invalid_input(self):
        """
        Tests if HasSelector raises NotSelectableSoupException
        when invalid input is provided.
        It requires all selectors to be SelectableSoup instances.
        """
        with pytest.raises(NotSelectableSoupException):
            HasSelector(MockLinkSelector(), "p")  # type: ignore

    @pytest.mark.parametrize(
        argnames="recursive",
        argvalues=[True, False],
        ids=["recursive", "not_recursive"],
    )
    def test_find_returns_first_tag_that_has_element_matching_single_selector(
        self, recursive: bool
    ):
        """
        Tests if find method returns the first tag that has an descendant element that
        matches a single selector. In this case, recursive parameter is not relevant.
        """
        text = """
            <p>Don't have</p>
            <div>
                <span>Hello World</span>
            </div>
            <a>Don't have</a>
            <div><a>1</a></div>
        """
        bs = find_body_element(to_bs(text))
        selector = HasSelector(MockLinkSelector())
        result = selector.find(bs, recursive=recursive)
        assert str(result) == strip("""<div><a>1</a></div>""")

    @pytest.mark.parametrize(
        argnames="recursive",
        argvalues=[True, False],
        ids=["recursive", "not_recursive"],
    )
    def test_find_raises_exception_when_no_tags_matches_single_selector_in_strict_mode(
        self, recursive: bool
    ):
        """
        Tests if find method raises TagNotFoundException when no tag is found
        that has a descendant element matching a single selector in strict mode.
        """
        text = """
            <p>Don't have</p>
            <div>
                <span>Hello World</span>
            </div>
            <a>Don't have</a>
        """
        bs = find_body_element(to_bs(text))
        selector = HasSelector(MockLinkSelector())

        with pytest.raises(TagNotFoundException):
            selector.find(bs, strict=True, recursive=recursive)

    @pytest.mark.parametrize(
        argnames="recursive",
        argvalues=[True, False],
        ids=["recursive", "not_recursive"],
    )
    def test_find_returns_none_if_no_tags_matches_single_selector_in_not_strict_mode(
        self, recursive: bool
    ):
        """
        Tests if find method returns None when no tag is found that has a descendant
        element matching a single selector in not strict mode.
        """
        text = """
            <p>Don't have</p>
            <div>
                <span>Hello World</span>
            </div>
            <a>Don't have</a>
        """
        bs = find_body_element(to_bs(text))
        selector = HasSelector(MockLinkSelector())
        result = selector.find(bs, recursive=recursive)
        assert result is None

    def test_finds_all_tags_matching_single_selector_when_recursive_true(self):
        """
        Tests if find_all method returns all descendant tags of the body element
        that have descendant elements matching a single selector.
        """
        text = """
            <p>Don't have</p>
            <div><a>1</a><a>Duplicate</a></div>
            <div>
                <span>Hello World</span>
            </div>
            <span><p></p><a>2</a></span>
            <a>Don't have</a>
            <div><a>3</a></div>
            <div><span><a>4</a></span></div>
        """
        bs = find_body_element(to_bs(text))

        selector = HasSelector(MockLinkSelector())
        result = selector.find_all(bs, recursive=True)

        assert list(map(str, result)) == [
            strip("""<div><a>1</a><a>Duplicate</a></div>"""),
            strip("""<span><p></p><a>2</a></span>"""),
            strip("""<div><a>3</a></div>"""),
            strip("""<div><span><a>4</a></span></div>"""),
            strip("""<span><a>4</a></span>"""),
        ]

    def test_finds_all_tags_matching_single_selector_when_recursive_false(self):
        """
        Tests if find_all method returns all children tags of the body element
        that have descendant elements matching a single selector.
        """
        text = """
            <p>Don't have</p>
            <div>
                <span>Hello World</span>
            </div>
            <span><p></p><a>1</a></span>
            <a>Don't have</a>
            <div><a>2</a></div>
            <div><span><a>3</a></span></div>
        """
        bs = find_body_element(to_bs(text))

        selector = HasSelector(MockLinkSelector())
        result = selector.find_all(bs, recursive=False)

        assert list(map(str, result)) == [
            strip("""<span><p></p><a>1</a></span>"""),
            strip("""<div><a>2</a></div>"""),
            strip("""<div><span><a>3</a></span></div>"""),
        ]

    @pytest.mark.parametrize(
        argnames="recursive",
        argvalues=[True, False],
        ids=["recursive", "not_recursive"],
    )
    def test_find_all_returns_empty_list_if_no_tag_matches_single_selector(
        self, recursive: bool
    ):
        """
        Tests if find_all method returns an empty list when no tag is found
        that has a descendant element matching a single selector.
        """
        text = """
            <p>Don't have</p>
            <div>
                <span>Hello World</span>
            </div>
            <a>Don't have</a>
        """
        bs = find_body_element(to_bs(text))
        selector = HasSelector(MockLinkSelector())
        result = selector.find_all(bs, recursive=recursive)
        assert result == []

    def test_find_all_returns_only_x_elements_when_limit_is_set(self):
        """
        Tests if find_all returns only x elements when limit is set.
        In this case only 2 first in order elements are returned.
        """
        text = """
            <p>Don't have</p>
            <div>
                <span>Hello World</span>
            </div>
            <span><p></p><a>1</a></span>
            <a>Don't have</a>
            <div><a>2</a></div>
            <div><span><a>3</a></span></div>
        """
        bs = find_body_element(to_bs(text))

        selector = HasSelector(MockLinkSelector())
        result = selector.find_all(bs, limit=2)

        assert list(map(str, result)) == [
            strip("""<span><p></p><a>1</a></span>"""),
            strip("""<div><a>2</a></div>"""),
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
            <p>Don't have</p>
            <div><span><a>1</a></span></div>
            <div>
                <span>Hello World</span>
            </div>
            <div><a>2</a></div>
            <span><p></p><a>2</a></span>
            <a>Don't have</a>
        """
        bs = find_body_element(to_bs(text))

        selector = HasSelector(MockLinkSelector())
        result = selector.find_all(bs, limit=2, recursive=False)

        assert list(map(str, result)) == [
            strip("""<div><span><a>1</a></span></div>"""),
            strip("""<div><a>2</a></div>"""),
        ]

    def test_find_all_returns_all_tags_matching_at_least_one_selector(
        self,
    ):
        """
        Tests if find_all method returns all tags that have descendant elements
        matching at least one of the selectors, when multiple selectors are provided.
        """
        text = """
            <p>Don't have</p>
            <span><a>1</a></span>
            <div>
                <span>Hello World</span>
            </div>
            <span><div>2</div></span>
            <span><span><div>Have both</div><a></a></span></span>
            <a>Don't have</a>
        """
        bs = find_body_element(to_bs(text))

        selector = HasSelector(MockLinkSelector(), MockDivSelector())
        result = selector.find_all(bs)

        assert list(map(str, result)) == [
            strip("""<span><a>1</a></span>"""),
            strip("""<span><div>2</div></span>"""),
            strip("""<span><span><div>Have both</div><a></a></span></span>"""),
            strip("""<span><div>Have both</div><a></a></span>"""),
        ]

    @pytest.mark.integration
    def test_find_all_returns_all_tags_matching_relative_selector(
        self,
    ):
        """
        Tests if find_all method returns all tags that anchored to relative selector
        find at least one matching tag. In this case, only elements that have
        a link tag as a child are returned.
        """
        text = """
            <p>Don't have</p>
            <div>
                <span><a>1</a></span>
            </div>
            <span>
                <div>
                    <span><a>2</a></span>
                </div>
            </span>
            <a>Don't have</a>
        """
        bs = find_body_element(to_bs(text))

        selector = HasSelector(RelativeChild(MockLinkSelector()))
        result = selector.find_all(bs)

        assert list(map(str, result)) == [
            strip("""<span><a>1</a></span>"""),
            strip("""<span><a>2</a></span>"""),
        ]
