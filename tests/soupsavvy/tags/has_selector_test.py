"""Testing module for ChildCombinator class."""

import pytest

from soupsavvy.tags.components import HasSelector
from soupsavvy.tags.exceptions import NotSelectableSoupException, TagNotFoundException

from .conftest import MockDivSelector, MockLinkSelector, find_body_element, strip, to_bs


@pytest.mark.soup
class TestHasSelector:
    """Class for HasSelector unit test suite."""

    def test_raises_exception_when_invalid_input(self):
        """
        Tests if HasSelector raises NotSelectableSoupException when invalid input is provided.
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
        matches a single selector.
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
        result = selector.find_all(bs, recursive=False)

        assert list(map(str, result)) == [
            strip("""<div><a>1</a><a>Duplicate</a></div>"""),
            strip("""<span><p></p><a>2</a></span>"""),
            strip("""<div><a>3</a></div>"""),
            strip("""<div><span><a>4</a></span></div>"""),
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

    # def test_find_returns_first_matching_child_if_recursive_false(self):
    #     """
    #     Tests if find returns first matching child element if recursive is False.
    #     In this case first 'p' element matches the selector, but it's not a child
    #     of body element, so it's not returned.
    #     """
    #     text = """
    #         <div>
    #             <a href="github">
    #                 <p>Hello 1</p>
    #             </a>
    #         </div>
    #         <a class="github">Hello 2</a>
    #         <p>Hello 3</p>
    #         <a class="github"><p>Text</p></a>
    #     """
    #     bs = find_body_element(to_bs(text))
    #     tag = ChildCombinator(
    #         TagSelector("a"),
    #         TagSelector("p"),
    #     )
    #     result = tag.find(bs, recursive=False)
    #     assert str(result) == strip("""<p>Text</p>""")

    # def test_find_returns_none_if_recursive_false_and_no_matching_child(self):
    #     """
    #     Tests if find returns None if no child element matches the selector
    #     and recursive is False.
    #     """
    #     text = """
    #         <div>
    #             <a href="github">
    #                 <p>Hello 1</p>
    #             </a>
    #         </div>
    #         <a class="github">Hello 2</a>
    #         <p>Hello 3</p>
    #     """
    #     bs = find_body_element(to_bs(text))
    #     tag = ChildCombinator(
    #         TagSelector("a"),
    #         TagSelector("p"),
    #     )
    #     result = tag.find(bs, recursive=False)
    #     assert result is None

    # def test_find_raises_exception_with_recursive_false_and_strict_mode(self):
    #     """
    #     Tests if find raises TagNotFoundException if no child element
    #     matches the selector, when recursive is False and strict is True.
    #     """
    #     text = """
    #         <div>
    #             <a href="github">
    #                 <p>Hello 1</p>
    #             </a>
    #         </div>
    #         <a class="github">Hello 2</a>
    #         <p>Hello 3</p>
    #     """
    #     bs = find_body_element(to_bs(text))
    #     tag = ChildCombinator(
    #         TagSelector("a"),
    #         TagSelector("p"),
    #     )

    #     with pytest.raises(TagNotFoundException):
    #         tag.find(bs, strict=True, recursive=False)

    # def test_find_all_returns_all_matching_children_when_recursive_false(self):
    #     """
    #     Tests if find_all returns all matching children if recursive is False.
    #     It returns only matching children of the body element.
    #     """
    #     text = """
    #         <a class="link">
    #             <div class="link"></div>
    #             <p>Text 1</p>
    #         </a>
    #         <a>
    #             <div>
    #                 <span class="widget">Hello 1</span>
    #             </div>
    #             <p>Text 2</p>
    #         </a>
    #         <div>
    #             <a>
    #                 <span>Hello 2</span>
    #                 <p>Text 3</p>
    #             </a>
    #         </div>
    #     """
    #     bs = find_body_element(to_bs(text))
    #     tag = ChildCombinator(
    #         TagSelector("a"),
    #         TagSelector("p"),
    #     )
    #     results = tag.find_all(bs, recursive=False)

    #     assert list(map(str, results)) == [
    #         strip("""<p>Text 1</p>"""),
    #         strip("""<p>Text 2</p>"""),
    #     ]

    # def test_find_all_returns_empty_list_if_none_matching_children_when_recursive_false(
    #     self,
    # ):
    #     """
    #     Tests if find_all returns an empty list if no child element matches the selector
    #     and recursive is False.
    #     """
    #     text = """
    #         <div>
    #             <a href="github">
    #                 <p>Hello 1</p>
    #             </a>
    #         </div>
    #         <a class="github">Hello 2</a>
    #         <p>Hello 3</p>
    #     """
    #     bs = find_body_element(to_bs(text))
    #     tag = ChildCombinator(
    #         TagSelector("a"),
    #         TagSelector("p"),
    #     )

    #     results = tag.find_all(bs, recursive=False)
    #     assert results == []

    # def test_find_all_returns_only_x_elements_when_limit_is_set(self):
    #     """
    #     Tests if find_all returns only x elements when limit is set.
    #     In this case only 2 first in order elements are returned.
    #     """
    #     text = """
    #         <a class="link">
    #             <div class="link"></div>
    #             <p>Text 1</p>
    #         </a>
    #         <div>
    #             <a>
    #                 <span>Hello 1</span>
    #                 <p>Text 2</p>
    #             </a>
    #         </div>
    #         <a>
    #             <div>
    #                 <span class="widget">Hello 2</span>
    #             </div>
    #             <p>Text 3</p>
    #         </a>
    #     """
    #     bs = find_body_element(to_bs(text))
    #     tag = ChildCombinator(
    #         TagSelector("a"),
    #         TagSelector("p"),
    #     )
    #     results = tag.find_all(bs, limit=2)

    #     assert list(map(str, results)) == [
    #         strip("""<p>Text 1</p>"""),
    #         strip("""<p>Text 2</p>"""),
    #     ]

    # def test_find_all_returns_only_x_elements_when_limit_is_set_and_recursive_false(
    #     self,
    # ):
    #     """
    #     Tests if find_all returns only x elements when limit is set and recursive
    #     is False. In this case only 2 first in order children matching
    #     the selector are returned.
    #     """
    #     text = """
    #         <a class="link">
    #             <div class="link"></div>
    #             <p>Text 1</p>
    #         </a>
    #         <div>
    #             <a>
    #                 <span>Hello 1</span>
    #                 <p>Text 2</p>
    #             </a>
    #         </div>
    #         <a>
    #             <div>
    #                 <span class="widget">Hello 2</span>
    #             </div>
    #             <p>Text 3</p>
    #             <p>Text 4</p>
    #         </a>
    #     """
    #     bs = find_body_element(to_bs(text))
    #     tag = ChildCombinator(
    #         TagSelector("a"),
    #         TagSelector("p"),
    #     )
    #     results = tag.find_all(bs, recursive=False, limit=2)

    #     assert list(map(str, results)) == [
    #         strip("""<p>Text 1</p>"""),
    #         strip("""<p>Text 3</p>"""),
    #     ]
