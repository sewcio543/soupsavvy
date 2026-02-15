"""Unit tests for operations specific to browser context."""

import math
import time
from dataclasses import dataclass
from typing import Any, cast
from unittest.mock import patch

import pytest

import soupsavvy.exceptions as exc
from soupsavvy.base import ElementAction
from soupsavvy.interfaces import IBrowser, IElement
from soupsavvy.operations.browser import (
    ApplyTo,
    Click,
    Condition,
    Find,
    FindAll,
    Navigate,
    SendKeys,
    WaitImplicitly,
    WaitUntil,
)
from soupsavvy.operations.general import OperationPipeline
from tests.soupsavvy.conftest import (
    MockDivSelector,
    MockIntOperation,
    MockLinkSelector,
    MockTextOperation,
    ToElement,
    strip,
)

FAIL = "fail"
FAILED_ERROR = "Action failed"

MOCK_TEXT = "mock-element"
MOCK_ELEMENT = cast(IElement, MOCK_TEXT)


def mock_time_sleep(seconds: float) -> None:
    """Mock time.sleep to avoid actual waiting during tests."""
    pass


class MockBrowserException(Exception):
    """Custom exception for MockBrowser to simulate browser errors."""


class MockBrowser(IBrowser):
    """Mock browser that records interactions for testing."""

    def __init__(self, browser=None, *args, **kwargs):
        super().__init__(browser, *args, **kwargs)
        self.visited_urls = []
        self.clicked_elements = []
        self.sent_keys = []
        self.body: IElement | None = None

    def navigate(self, url: str) -> None:
        if url == FAIL:
            raise MockBrowserException(FAILED_ERROR)

        self.visited_urls.append(url)

    def click(self, element: IElement) -> None:
        if element == FAIL:
            raise MockBrowserException(FAILED_ERROR)

        self.clicked_elements.append(element)

    def send_keys(self, element: IElement, value: str, clear: bool = True) -> None:
        if element == FAIL:
            raise MockBrowserException(FAILED_ERROR)

        self.sent_keys.append((element, value, clear))

    def get_document(self) -> IElement:
        if self.body is None:
            raise MockBrowserException("No document set in MockBrowser")

        return self.body

    def get_current_url(self) -> str:
        return self.visited_urls[-1] if self.visited_urls else "about:blank"

    def close(self) -> None:
        pass


@pytest.fixture(scope="function")
def mock_browser() -> MockBrowser:
    """Fixture that provides a fresh MockBrowser instance for each test."""
    return MockBrowser()


class MockAction(ElementAction):
    """Mock action that records interactions for testing."""

    def __init__(self, arg=None) -> None:
        self.interactions: list[tuple[IBrowser, IElement]] = []
        self.arg = arg

    def _execute(self, browser: IBrowser, element: IElement) -> None:
        if element == FAIL:
            raise MockBrowserException(FAILED_ERROR)

        self.interactions.append((browser, element))

    def __eq__(self, x: object) -> bool:
        if not isinstance(x, MockAction):
            return NotImplemented

        return self.arg == x.arg


class ErrorSelector(MockLinkSelector):
    """Mock selector that always return element that triggers failed action."""

    def find_all(
        self, tag: IElement, recursive: bool = True, limit=None
    ) -> list[IElement]:
        return [cast(IElement, FAIL)]


@pytest.mark.operation
@pytest.mark.browser
class TestNavigate:
    """Tests suite for the Navigate operation."""

    def test_navigate_executes_browser_navigation(self, mock_browser: MockBrowser):
        """
        Test that Navigate calls browser.navigate() with the correct URL.
        It should also return the browser instance and set the url attribute.
        """
        url = "https://example.com"
        op = Navigate(url)
        assert op.url == url

        result = op.execute(mock_browser)

        assert mock_browser.visited_urls == [url]
        assert result is mock_browser

    def test_navigate_propagates_browser_exception(self, mock_browser: MockBrowser):
        """
        Test that Navigate propagates exceptions from browser.navigate().
        It eventually raises FailedOperationExecution,
        as it's handled by BaseOperation execute method.
        """
        op = Navigate(FAIL)

        with pytest.raises(exc.FailedOperationExecution, match=FAILED_ERROR):
            op.execute(mock_browser)

        assert mock_browser.visited_urls == []

    def test_raises_error_when_arg_is_not_browser(self):
        """
        Test that Navigate raises NotBrowserException
        when the argument is not an instance of IBrowser.
        """
        op = Navigate("https://example.com")

        with pytest.raises(exc.NotBrowserException):
            op.execute("not a browser")  # type: ignore

    def test_navigate_multiple_calls(self, mock_browser: MockBrowser):
        """Test that multiple calls to browser.navigate are recorded correctly."""
        op1 = Navigate("https://example.com")
        op2 = Navigate("https://openai.com")

        op1.execute(mock_browser)
        op1.execute(mock_browser)
        op2.execute(mock_browser)

        assert mock_browser.visited_urls == [
            "https://example.com",
            "https://example.com",
            "https://openai.com",
        ]

    def test_equality_true(self):
        """Test equality for Navigate operations with the same URL."""
        op1 = Navigate("https://example.com")
        op2 = Navigate("https://example.com")
        assert op1 == op2

    def test_equality_false(self):
        """Test inequality for Navigate operations with different URLs."""
        op1 = Navigate("https://example.com")
        op2 = Navigate("https://openai.com")
        assert op1 != op2

    def test_navigate_equality_with_different_type(self):
        """Test comparison with a non-Navigate object."""
        op = Navigate("https://example.com")
        assert op.__eq__("not a Navigate") is NotImplemented


@pytest.mark.browser
class TestClick:
    """Tests suite for the Click action."""

    def test_click_executes_action_on_provided_element(self, mock_browser: MockBrowser):
        """
        Test that Click performs action on provided element.
        execute method should return None as this is not browser operation but action.
        """
        op = Click()

        result = op.execute(browser=mock_browser, element=MOCK_ELEMENT)  # type: ignore[func-returns-value]

        assert result is None
        assert mock_browser.clicked_elements == [MOCK_TEXT]

    def test_click_executes_multiple_calls(self, mock_browser: MockBrowser):
        """Test that multiple Click actions are executed correctly."""
        op1 = Click()
        op2 = Click()

        mock_2 = cast(IElement, "Hello")

        op1.execute(browser=mock_browser, element=MOCK_ELEMENT)
        op1.execute(browser=mock_browser, element=MOCK_ELEMENT)
        op2.execute(browser=mock_browser, element=mock_2)

        assert mock_browser.clicked_elements == [MOCK_TEXT, MOCK_TEXT, "Hello"]

    def test_click_propagates_browser_exception(self, mock_browser: MockBrowser):
        """Test that Click propagates exceptions from the browser."""
        op = Click()

        with pytest.raises(MockBrowserException, match=FAILED_ERROR):
            op.execute(browser=mock_browser, element=cast(IElement, FAIL))

        assert mock_browser.clicked_elements == []

    def test_equality_true(self):
        """Test equality for multiple Click operations."""
        op1 = Click()
        op2 = Click()
        assert op1 == op2

    def test_click_equality_with_different_type(self):
        """Test comparison with a non-Click object."""
        op = Click()
        assert op.__eq__("not a Click") is NotImplemented


@pytest.mark.browser
class TestSendKeys:
    """Tests suite for the SendKeys action."""

    @pytest.mark.parametrize("clear", [True, False], ids=["clear", "no-clear"])
    def test_sendkeys_executes_action_on_provided_element(
        self, clear: bool, mock_browser: MockBrowser
    ):
        """
        Test that SendKeys performs the send keys action on provided element.
        execute method should return None as this is not browser operation but action.
        Attributes value and clear should be set correctly.
        """
        value = "test input"

        op = SendKeys(value, clear=clear)

        assert op.value == value
        assert op.clear == clear

        result = op.execute(browser=mock_browser, element=MOCK_ELEMENT)  # type: ignore[func-returns-value]

        assert result is None
        assert mock_browser.sent_keys == [(MOCK_ELEMENT, value, clear)]

    def test_sendkeys_propagates_browser_exception(self, mock_browser: MockBrowser):
        """Test that SendKeys propagates exceptions from the browser."""
        op = SendKeys("test input")

        with pytest.raises(MockBrowserException, match=FAILED_ERROR):
            op.execute(browser=mock_browser, element=cast(IElement, FAIL))

        assert mock_browser.sent_keys == []

    def test_sendkeys_executes_multiple_calls(self, mock_browser: MockBrowser):
        """Test that multiple SendKeys actions are executed correctly."""
        op1 = SendKeys("first input", clear=True)
        op2 = SendKeys("second input", clear=False)

        mock2 = cast(IElement, "Hello")

        op1.execute(browser=mock_browser, element=MOCK_ELEMENT)
        op1.execute(browser=mock_browser, element=mock2)
        op2.execute(browser=mock_browser, element=MOCK_ELEMENT)

        assert mock_browser.sent_keys == [
            (MOCK_ELEMENT, "first input", True),
            (mock2, "first input", True),
            (MOCK_ELEMENT, "second input", False),
        ]

    def test_equality_true(self):
        """Test equality for SendKeys operations with the same value and clear."""
        op1 = SendKeys("test input", clear=True)
        op2 = SendKeys("test input", clear=True)
        assert op1 == op2

    @pytest.mark.parametrize(
        "operations",
        [
            (SendKeys("input", clear=True), SendKeys("input", clear=False)),
            (SendKeys("input1", clear=True), SendKeys("input2", clear=True)),
        ],
        ids=["different-clear", "different-value"],
    )
    def test_equality_false(self, operations: tuple[SendKeys, SendKeys]):
        """Test inequality for SendKeys operations with different values."""
        op1, op2 = operations
        assert op1 != op2

    def test_sendkeys_equality_with_different_type(self):
        """Test comparison with a non-SendKeys object."""
        op = SendKeys("test input")
        assert op.__eq__("not a SendKeys") is NotImplemented


@pytest.mark.operation
class TestWaitImplicitly:
    """
    Tests suite for the WaitImplicitly operation.
    This is not a browser specific operation, as it does not interact with the browser
    context instance, but it's mostly used in browser workflows.
    """

    @pytest.mark.parametrize(
        "arg",
        [MockBrowser(), "any argument", None],
        ids=["browser", "string", "none"],
    )
    def test_waitimplicitly_executes_browser_wait(self, arg):
        """Test that WaitImplicitly calls time.sleep() with the correct timeout."""
        op = WaitImplicitly(0.01)

        with patch("time.sleep", side_effect=mock_time_sleep) as mock_sleep:
            result = op.execute(arg)

            mock_sleep.assert_called_once_with(0.01)
            assert result is arg

    def test_can_be_used_with_any_argument(self):
        """
        Test that WaitImplicitly can be used with any argument,
        as it does not matter and is simply ignored.
        """
        op = WaitImplicitly(0.01)

        with patch("time.sleep", side_effect=mock_time_sleep) as mock_sleep:
            result = op.execute("any argument")

            mock_sleep.assert_called_once_with(0.01)
            assert result == "any argument"

    def test_equality_true(self):
        """Test equality for WaitImplicitly operations with the same timeout."""
        op1 = WaitImplicitly(10)
        op2 = WaitImplicitly(10)
        assert op1 == op2

    def test_equality_false(self):
        """Test inequality for WaitImplicitly operations with different timeouts."""
        op1 = WaitImplicitly(10)
        op2 = WaitImplicitly(20)
        assert op1 != op2

    def test_waitimplicitly_equality_with_different_type(self):
        """Test comparison with a non-WaitImplicitly object."""
        op = WaitImplicitly(10)
        assert op.__eq__("not a WaitImplicitly") is NotImplemented


@pytest.mark.operation
@pytest.mark.browser
class TestApplyTo:
    """Tests suite for the ApplyTo operation."""

    def test_applyto_executes_action_on_found_element(
        self, to_element: ToElement, mock_browser: MockBrowser
    ):
        """
        Test that ApplyTo finds the element and performs the action.
        execute method should return the browser instance.
        Attributes selector and action should be set correctly.
        """
        text = """
            <a href="https://example.com">Example Link</a>
        """
        element = to_element(text)
        expected = element.find_all("a")[0]

        mock_browser.body = element

        selector = MockLinkSelector()
        action = MockAction()

        op = ApplyTo(selector=selector, action=action)

        assert op.selector is selector
        assert op.action is action

        result = op.execute(mock_browser)

        assert result is mock_browser
        assert action.interactions == [(mock_browser, expected)]

    def test_applyto_propagates_action_exception(
        self, to_element: ToElement, mock_browser: MockBrowser
    ):
        """
        Test that ApplyTo propagates exceptions from the action.
        It eventually raises FailedOperationExecution,
        as it's handled by BaseOperation execute method.
        """
        text = """
            <a href="https://example.com">Example Link</a>
        """
        element = to_element(text)
        mock_browser.body = element

        selector = ErrorSelector()
        action = MockAction()
        op = ApplyTo(selector=selector, action=action)

        with pytest.raises(exc.FailedOperationExecution, match=FAILED_ERROR):
            op.execute(mock_browser)

        assert action.interactions == []

    def test_applyto_raises_when_selector_does_not_find_element(
        self, to_element: ToElement, mock_browser: MockBrowser
    ):
        """
        Test that ApplyTo raises FailedOperationExecution
        when the selector does not find matching element.
        """
        text = """
            <div>No links here</div>
        """
        element = to_element(text)
        mock_browser.body = element

        selector = MockLinkSelector()
        action = MockAction()

        op = ApplyTo(selector=selector, action=action)

        with pytest.raises(exc.FailedOperationExecution):
            op.execute(mock_browser)

        assert action.interactions == []

    def test_equality_true(self):
        """Test equality for ApplyTo operations with the same selector and action."""
        selector = MockLinkSelector()
        action = MockAction()

        op1 = ApplyTo(selector=selector, action=action)
        op2 = ApplyTo(selector=selector, action=action)

        assert op1 == op2

    @pytest.mark.parametrize(
        "operations",
        [
            (
                ApplyTo(MockLinkSelector(), MockAction()),
                ApplyTo(MockLinkSelector(), MockAction(arg="different")),
            ),
            (
                ApplyTo(MockLinkSelector(), MockAction()),
                ApplyTo(MockDivSelector(), MockAction()),
            ),
        ],
    )
    def test_equality_false(self, operations: tuple[ApplyTo, ApplyTo]):
        """Test inequality for ApplyTo operations with different selector or action."""
        op1, op2 = operations
        assert op1 != op2

    def test_applyto_equality_with_different_type(self):
        """Test comparison with a non-ApplyTo object."""
        op = ApplyTo(selector=MockLinkSelector(), action=MockAction())
        assert op.__eq__("not an ApplyTo") is NotImplemented


@pytest.mark.operation
@pytest.mark.browser
class TestFind:
    """Tests suite for the Find operation."""

    @pytest.mark.parametrize("strict", [False, True], ids=["non-strict", "strict"])
    def test_returns_element_that_matches_selector(
        self, mock_browser: MockBrowser, to_element: ToElement, strict: bool
    ):
        """
        Test that Find execute method returns the element found by the selector,
        both when strict is True and False.
        """
        op = Find(MockLinkSelector(), strict=strict)
        assert op.selector == MockLinkSelector()

        text = """
            <div><a href="https://example.com">Example Link</a></div>
        """
        element = to_element(text)
        mock_browser.body = element

        result = op.execute(mock_browser)
        assert strip(str(result)) == strip(
            """<a href="https://example.com">Example Link</a>"""
        )

    def test_returns_none_if_element_not_found_in_non_strict_mode(
        self, mock_browser: MockBrowser, to_element: ToElement
    ):
        """
        Test that Find returns None when the selector does not find any element
        and strict is set to False.
        """
        op = Find(MockLinkSelector())
        assert op.selector == MockLinkSelector()

        text = """
            <div><span>Example Link</span></div>
        """
        element = to_element(text)
        mock_browser.body = element

        result = op.execute(mock_browser)
        assert result is None

    def test_raises_error_if_element_not_found_in_strict_mode(
        self, mock_browser: MockBrowser, to_element: ToElement
    ):
        """
        Test that Find raises FailedOperationExecution
        when the selector does not find any element and strict is set to True.
        It raises FailedOperationExecution instead of TagNotFoundException
        which is intercepted, because it's handled by BaseOperation execute method.
        """
        op = Find(MockLinkSelector(), strict=True)

        text = """
            <div><span>Example Link</span></div>
        """
        element = to_element(text)
        mock_browser.body = element

        with pytest.raises(exc.FailedOperationExecution):
            op.execute(mock_browser)

    def test_returns_transformed_value_when_pipeline_is_used(
        self, mock_browser: MockBrowser, to_element: ToElement
    ):
        """
        Test that Find returns the transformed value
        when a selection pipeline was executed without errors.
        """
        sel = MockLinkSelector() | MockTextOperation() | MockIntOperation()
        op = Find(sel)

        text = """
            <div><a href="https://example.com">123</a></div>
        """
        element = to_element(text)
        mock_browser.body = element

        result = op.execute(mock_browser)
        assert result == 123

    def test_raises_error_if_operation_failed(
        self, mock_browser: MockBrowser, to_element: ToElement
    ):
        """
        Test that Find raises FailedOperationExecution
        when the operation in the selection pipeline fails on the found element.
        """
        sel = MockLinkSelector() | MockTextOperation() | MockIntOperation()
        op = Find(sel)

        text = """
            <div><a href="https://example.com">Example Link</a></div>
        """
        element = to_element(text)
        mock_browser.body = element

        with pytest.raises(exc.FailedOperationExecution):
            op.execute(mock_browser)

    def test_find_raises_error_if_arg_not_selector(self):
        """
        Test that Find raises NotTagSearcherException
        when initialized with invalid selector.
        """
        with pytest.raises(exc.NotTagSearcherException):
            Find("string")  # type: ignore

    def test_raises_error_when_arg_is_not_browser(self):
        """
        Test that Find raises NotBrowserException
        when the argument is not an instance of IBrowser.
        """
        op = Find(MockLinkSelector())

        with pytest.raises(exc.NotBrowserException):
            op.execute("not a browser")  # type: ignore

    def test_equality_true(self):
        """Test equality for Find operations with the same selector."""
        op1 = Find(MockLinkSelector())
        op2 = Find(MockLinkSelector())
        assert op1 == op2

    def test_equality_false(self):
        """Test inequality for Find operations with different selectors."""
        op1 = Find(MockLinkSelector())
        op2 = Find(MockDivSelector())
        assert op1 != op2

    def test_find_equality_with_different_type(self):
        """Test comparison with a non-Find object."""
        op = Find(MockLinkSelector())
        assert op.__eq__("not a Find") is NotImplemented


@pytest.mark.operation
@pytest.mark.browser
class TestFindAll:
    """Tests suite for the FindAll operation."""

    def test_returns_element_that_matches_selector(
        self, mock_browser: MockBrowser, to_element: ToElement
    ):
        """
        Test that FindAll execute method returns list of elements found by the selector.
        """
        op = FindAll(MockLinkSelector())
        assert op.selector == MockLinkSelector()

        text = """
            <a href="https://example.com">Example Link</a>
            <span>Other Element</span>
            <a>Hello</a>
        """
        element = to_element(text)
        mock_browser.body = element

        result = op.execute(mock_browser)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a href="https://example.com">Example Link</a>"""),
            strip("""<a>Hello</a>"""),
        ]

    def test_returns_empty_list_when_no_elements_found(
        self, mock_browser: MockBrowser, to_element: ToElement
    ):
        """
        Test that FindAll returns an empty list
        when the selector does not find any element.
        """
        op = FindAll(MockLinkSelector())

        text = """
            <span>Other Element</span>
            <div>No links here</div>
        """
        element = to_element(text)
        mock_browser.body = element

        result = op.execute(mock_browser)
        assert result == []

    def test_returns_up_to_limit_elements_when_specified(
        self, mock_browser: MockBrowser, to_element: ToElement
    ):
        """
        Test that FindAll returns up to 'limit' elements
        when the limit parameter is specified.
        """
        op = FindAll(MockLinkSelector(), limit=2)

        text = """
            <a href="https://example.com">Example Link</a>
            <span>Other Element</span>
            <a>Hello</a>
            <a>World</a>
        """
        element = to_element(text)
        mock_browser.body = element

        result = op.execute(mock_browser)

        assert list(map(lambda x: strip(str(x)), result)) == [
            strip("""<a href="https://example.com">Example Link</a>"""),
            strip("""<a>Hello</a>"""),
        ]

    def test_returns_transformed_values_when_pipeline_is_used(
        self, mock_browser: MockBrowser, to_element: ToElement
    ):
        """
        Test that FindAll returns the transformed values
        when a selection pipeline was executed without errors.
        """
        sel = MockLinkSelector() | MockTextOperation() | MockIntOperation()
        op = FindAll(sel)

        text = """
            <a href="https://example.com">123</a>
            <span>Other Element</span>
            <a>67</a>
        """
        element = to_element(text)
        mock_browser.body = element

        result = op.execute(mock_browser)
        assert result == [123, 67]

    def test_raises_error_if_operation_failed(
        self, mock_browser: MockBrowser, to_element: ToElement
    ):
        """
        Test that FindAll raises FailedOperationExecution
        when the operation in the selection pipeline fails on the found element.
        """
        sel = MockLinkSelector() | MockTextOperation() | MockIntOperation()
        op = FindAll(sel)

        text = """
            <a href="https://example.com">123</a>
            <span>Other Element</span>
            <a>Not number</a>
        """
        element = to_element(text)
        mock_browser.body = element

        with pytest.raises(exc.FailedOperationExecution):
            op.execute(mock_browser)

    def test_find_raises_error_if_arg_not_selector(self):
        """
        Test that FindAll raises NotTagSearcherException
        when initialized with invalid selector.
        """
        with pytest.raises(exc.NotTagSearcherException):
            FindAll("string")  # type: ignore

    def test_raises_error_when_arg_is_not_browser(self):
        """
        Test that FindAll raises NotBrowserException
        when the argument is not an instance of IBrowser.
        """
        op = FindAll(MockLinkSelector())

        with pytest.raises(exc.NotBrowserException):
            op.execute("not a browser")  # type: ignore

    def test_equality_true(self):
        """Test equality for FindAll operations with the same selector."""
        op1 = FindAll(MockLinkSelector())
        op2 = FindAll(MockLinkSelector())
        assert op1 == op2

    def test_equality_false(self):
        """Test inequality for FindAll operations with different selectors."""
        op1 = FindAll(MockLinkSelector())
        op2 = FindAll(MockDivSelector())
        assert op1 != op2

    def test_find_equality_with_different_type(self):
        """Test comparison with a non-FindAll object."""
        op = FindAll(MockLinkSelector())
        assert op.__eq__("not a FindAll") is NotImplemented


@pytest.mark.operation
@pytest.mark.integration
@pytest.mark.browser
class TestBrowserIntegration:
    """
    Tests suite with integration tests for chaining multiple browser operations
    (OperationPipeline) and executing them with browser.
    """

    def test_operations_can_be_chained(self):
        """
        Test that multiple browser operations can be chained together
        which results in OperationPipeline instance.
        """
        op1 = Navigate("https://example.com")
        op2 = WaitImplicitly(0.01)
        op3 = ApplyTo(selector=MockLinkSelector(), action=Click())
        op4 = ApplyTo(
            selector=MockDivSelector(), action=SendKeys("test input", clear=True)
        )

        chained_op = op1 | op2 | op3 | op4
        assert isinstance(chained_op, OperationPipeline)
        assert chained_op.operations == [op1, op2, op3, op4]

    def test_operations_are_executed_in_pipeline(
        self, to_element: ToElement, mock_browser: MockBrowser
    ):
        """
        Test that multiple browser operations can be executed in a pipeline
        in correct order.
        """
        text = """
            <div><a href="https://example.com">Example Link</a></div>
        """
        element = to_element(text)
        link = element.find_all("a")[0]
        mock_browser.body = element

        op1 = Navigate("https://example.com")
        action = MockAction()
        op2 = ApplyTo(selector=MockLinkSelector(), action=action)
        pipe = op1 | op2
        result = pipe.execute(mock_browser)

        assert result is mock_browser
        assert mock_browser.visited_urls == ["https://example.com"]
        assert action.interactions == [(mock_browser, link)]

    def test_find_integrates_with_operations_and_pipe_returns_value(
        self, to_element: ToElement, mock_browser: MockBrowser
    ):
        """
        Test that Find operation integrates correctly in a pipeline
        and returns the found element.
        """
        text = """
            <div><a href="https://example.com">Example Link</a></div>
        """
        element = to_element(text)
        mock_browser.body = element

        op1 = Navigate("https://example.com")
        op2 = Find(MockLinkSelector())
        pipe = op1 | op2
        result = pipe.execute(mock_browser)

        assert strip(str(result)) == strip(
            """<a href="https://example.com">Example Link</a>"""
        )
        assert mock_browser.visited_urls == ["https://example.com"]

    def test_findall_integrates_with_operations_and_pipe_returns_list(
        self, to_element: ToElement, mock_browser: MockBrowser
    ):
        """
        Test that FindAll operation integrates correctly in a pipeline
        and returns the found elements.
        """
        text = """
            <a href="https://example.com">123</a>
            <span>Other Element</span>
            <a>67</a>
        """
        element = to_element(text)
        mock_browser.body = element

        op1 = Navigate("https://example.com")
        op2 = FindAll(MockLinkSelector() | MockTextOperation() | MockIntOperation())
        pipe = op1 | op2
        result = pipe.execute(mock_browser)

        assert result == [123, 67]
        assert mock_browser.visited_urls == ["https://example.com"]

    def test_pipe_raises_error_when_browser_operation_after_find(
        self, to_element: ToElement, mock_browser: MockBrowser
    ):
        """
        Test that OperationPipeline raises FailedOperationExecution
        when a browser operation is chained after Find operation,
        which is not passthrough operation (does not return browser instance)
        and should be the last in the pipeline.
        """
        text = """
            <a href="https://example.com">123</a>
            <span>Other Element</span>
            <a>67</a>
        """
        element = to_element(text)
        mock_browser.body = element

        op1 = Navigate("https://example.com")
        op2 = FindAll(MockLinkSelector())
        pipe = op1 | op2 | op1

        with pytest.raises(exc.FailedOperationExecution):
            pipe.execute(mock_browser)

    def test_raises_error_when_chained_with_non_operation(self):
        """
        Test that chaining a browser operation with a non-browser operation
        raises NotOperationException.
        """
        op1 = Navigate("https://example.com")

        with pytest.raises(exc.NotOperationException):
            _ = op1 | "not an operation"

    @pytest.mark.parametrize(
        "operations",
        [
            Navigate("https://example.com") | WaitImplicitly(0.01),
            WaitImplicitly(0.01) | ApplyTo(MockLinkSelector(), Click()),
        ],
    )
    def test_raises_error_when_arg_is_not_browser(self, operations: OperationPipeline):
        """
        Test that OperationPipeline raises FailedOperationExecution
        when the argument is not an instance of IBrowser.
        It does not matter which operation in the pipeline is browser specific.
        """
        with pytest.raises(exc.FailedOperationExecution):
            operations.execute("not a browser")

    def test_wait_until_breaks_execution_if_returns_false(
        self, to_element: ToElement, mock_browser: MockBrowser
    ):
        """
        Test that WaitUntil operation breaks the execution of the pipeline
        if the condition returns False, and the subsequent operations are not executed.
        """
        mock_browser.body = to_element("""<a>67</a>""")

        wait_op = WaitUntil(Condition(lambda: False), timeout=0.01)
        op1 = Navigate("https://example.com")
        op2 = FindAll(MockDivSelector() | MockTextOperation() | MockIntOperation())
        pipe = op1 | wait_op | op2

        with pytest.raises(exc.FailedOperationExecution):
            pipe.execute(mock_browser)

        assert mock_browser.visited_urls == ["https://example.com"]

    def test_wait_until_yields_control_if_returns_true(
        self, to_element: ToElement, mock_browser: MockBrowser
    ):
        """
        Test that WaitUntil operation yields control to the next operations
        in the pipeline if the condition returns True,
        and the subsequent operations are executed.
        """
        text = """<a>67</a><a>123</a><div>Other</div>"""
        element = to_element(text)
        mock_browser.body = element

        wait_op = WaitUntil(Condition(lambda: True), timeout=0.01)

        op1 = Navigate("https://example.com")
        op2 = FindAll(MockLinkSelector() | MockTextOperation() | MockIntOperation())
        pipe = op1 | wait_op | op2

        result = pipe.execute(mock_browser)

        assert result == [67, 123]
        assert mock_browser.visited_urls == ["https://example.com"]

    def test_wait_until_retries_until_condition_is_met(
        self, to_element: ToElement, mock_browser: MockBrowser
    ):
        """
        Test that WaitUntil operation retries the condition check until it returns True.
        This simulates waiting for an element to appear on the page.
        """
        text = """<div>Other</div>"""
        element = to_element(text)
        mock_browser.body = element

        COUNT = 0

        def condition(browser: MockBrowser) -> bool:
            nonlocal COUNT

            if COUNT == 2:
                mock_browser.body = to_element(
                    """<a>67</a><a>123</a><div>Other</div>"""
                )
            else:
                COUNT += 1
                mock_browser.navigate(f"WAITING {COUNT}")

            return MockLinkSelector().find(browser.get_document()) is not None

        wait_op = WaitUntil(
            # higher timeout to allow elements to be converted and found by the selector
            Condition(condition, params={"browser": mock_browser}),
            timeout=0.1,
        )

        op1 = Navigate("https://example.com")
        op2 = FindAll(MockLinkSelector() | MockTextOperation() | MockIntOperation())
        pipe = op1 | wait_op | op2

        result = pipe.execute(mock_browser)

        assert result == [67, 123]
        assert mock_browser.visited_urls == [
            "https://example.com",
            "WAITING 1",
            "WAITING 2",
        ]


@dataclass(frozen=True)
class FunctionCall:
    params: dict
    result: Any


@pytest.fixture(scope="function")
def calls() -> list[FunctionCall]:
    """Fixture for collecting function calls."""
    return []


def mock_predicate(x: bool, y: bool) -> bool:
    result = x and y
    return result


class MockPredicateClass:
    def __call__(self, x: bool, y: bool) -> bool:
        return True


@pytest.mark.browser
class TestCondition:
    """Test suite for base Condition class."""

    @pytest.mark.parametrize(
        argnames="x, y, expected",
        argvalues=[
            (True, True, True),
            (True, False, False),
            (False, False, False),
        ],
    )
    def test_check_method_works_as_expected_with_predicate(
        self, x: bool, y: bool, expected: bool, calls: list[FunctionCall]
    ):
        """
        Tests if check method works correctly when predicate function is provided
        and all required parameters are passed. Function should be called only once
        with correct parameters.
        """

        def predicate(x: bool, y: bool) -> bool:
            result = x and y
            calls.append(FunctionCall(params={"x": x, "y": y}, result=result))
            return result

        condition = Condition(predicate, params={"x": x, "y": y})
        result = condition.check()

        assert isinstance(result, bool)
        assert result is expected
        assert calls == [FunctionCall(params={"x": x, "y": y}, result=expected)]

    def test_parameters_can_be_skipped_if_function_does_not_accept_any(
        self, calls: list[FunctionCall]
    ):
        """
        Tests if check method works properly
        when function does not accept any parameters.
        In this case, params are not required.
        """

        def predicate() -> bool:
            calls.append(FunctionCall(params={}, result=True))
            return True

        condition = Condition(predicate)
        result = condition.check()

        assert result is True
        assert calls == [FunctionCall(params={}, result=True)]

    def test_parameters_can_be_skipped_if_function_only_accepts_find_params(
        self, calls: list[FunctionCall]
    ):
        """
        Tests if check method works properly when function only accepts
        find parameters. In this case, params are not required.
        """

        def predicate(tag, strict: bool) -> bool:
            calls.append(
                FunctionCall(params={"tag": tag, "strict": strict}, result=False)
            )
            return False

        condition = Condition(predicate)
        result = condition.check(tag="string", strict=True)  # type: ignore

        assert result is False
        assert calls == [
            FunctionCall(params={"tag": "string", "strict": True}, result=False)
        ]

    @pytest.mark.parametrize(
        argnames="func",
        argvalues=[lambda x, y: True, mock_predicate, MockPredicateClass()],
        ids=["lambda", "function", "callable-class"],
    )
    def test_any_callable_can_be_used_as_predicate(self, func):
        """
        Tests if check method works correctly when any callable
        (lambda, function, callable class) is provided as predicate.
        """
        condition = Condition(func, params={"x": True, "y": True})
        result = condition.check()
        assert result is True

    @pytest.mark.parametrize(
        argnames="x, y, expected",
        argvalues=[
            (1, 1, 2),
            (1, -1, 0),
        ],
    )
    def test_check_method_works_as_expected_with_function_returning_non_boolean(
        self, x: bool, y: bool, expected: bool, calls: list[FunctionCall]
    ):
        """
        Tests if check method works correctly when function returning non-boolean
        value is provided. Result returned by the function should be cast to boolean.
        """

        def func(x: Any, y: Any) -> int:
            result = x + y
            calls.append(FunctionCall(params={"x": x, "y": y}, result=result))
            return result

        condition = Condition(func, params={"x": x, "y": y})
        result = condition.check()

        assert isinstance(result, bool)
        assert result is bool(expected)
        assert calls == [FunctionCall(params={"x": x, "y": y}, result=expected)]

    def test_raises_error_when_arguments_missing(self):
        """
        Tests if check method raises InvalidParametersBinding
        when required arguments are missing.
        """

        def func(x: Any, y: Any) -> bool:
            return True

        with pytest.raises(exc.InvalidParametersBinding):
            Condition(func, params={"x": 1})

    def test_raises_error_when_invalid_arguments_provided(self):
        """
        Tests if check method raises InvalidParametersBinding
        when invalid arguments are provided. One of the arguments
        does not correspond to any parameter in the function signature.
        """

        def func(x: Any, y: Any) -> bool:
            return True

        with pytest.raises(exc.InvalidParametersBinding):
            Condition(func, params={"x": 1, "y": 2, "z": 3})

    def test_handles_keyword_arguments_when_defined_by_function(
        self, calls: list[FunctionCall]
    ):
        """
        Tests if extra parameters are bound to **kwargs
        when function defines keyword arguments. Positional arguments can be defined
        in function signature as well, but are internally ignored.
        The name does not have to be standard **kwargs,
        any valid identifier is accepted.
        """

        def func(x: bool, y: int, *args, **keywords) -> bool:
            calls.append(
                FunctionCall(
                    params={"x": x, "y": y, "keywords": keywords, "args": args},
                    result=True,
                )
            )
            return True

        condition = Condition(func, params={"x": 1, "y": 2, "z": 3, "i": 4})
        result = condition.check()

        assert result is True
        assert calls == [
            FunctionCall(
                params={"x": 1, "y": 2, "keywords": {"z": 3, "i": 4}, "args": ()},
                result=True,
            )
        ]

    def test_passes_when_arguments_with_defaults_are_skipped(
        self, calls: list[FunctionCall]
    ):
        """
        Tests if check method works correctly when some arguments
        have default values and are skipped in params.
        """

        def predicate(x: bool, y: bool = True) -> bool:
            result = x and y
            calls.append(FunctionCall(params={"x": x, "y": y}, result=result))
            return result

        condition = Condition(predicate, params={"x": True})
        result = condition.check()

        assert result is True
        assert calls == [FunctionCall(params={"x": True, "y": True}, result=True)]

    def test_default_arguments_are_overridden_by_params(
        self, calls: list[FunctionCall]
    ):
        """
        Tests if default arguments are correctly overridden by params
        provided to Condition.
        """

        def predicate(x: bool, y: bool = False) -> bool:
            result = x and y
            calls.append(FunctionCall(params={"x": x, "y": y}, result=result))
            return result

        condition = Condition(predicate, params={"x": True, "y": True})

        result = condition.check()
        assert result is True
        assert calls == [FunctionCall(params={"x": True, "y": True}, result=True)]

    def test_find_arguments_are_handled_separately(self, calls: list[FunctionCall]):
        """
        Tests if find arguments (tag, strict, recursive) are skipped on initialization
        and handled separately in check method where they are passed into
        partial function.
        """

        def predicate(
            tag: bool, strict: bool, recursive: bool, x: bool, y: bool
        ) -> bool:
            result = x and y and strict and recursive and tag
            calls.append(
                FunctionCall(
                    params={
                        "x": x,
                        "y": y,
                        "strict": strict,
                        "recursive": recursive,
                        "tag": tag,
                    },
                    result=result,
                )
            )
            return result

        condition = Condition(predicate, params={"x": True, "y": True})
        result = condition.check(tag=True, strict=True, recursive=False)  # type: ignore

        assert result is False
        assert calls == [
            FunctionCall(
                params={
                    "x": True,
                    "y": True,
                    "strict": True,
                    "recursive": False,
                    "tag": True,
                },
                result=False,
            )
        ]

    def test_find_arguments_are_not_overridden_when_provided_in_init(
        self, calls: list[FunctionCall]
    ):
        """
        Tests if find arguments (tag, strict, recursive) provided in Condition
        initialization are not overridden by those provided in check method.
        Bound parameters take precedence.
        """
        calls = []

        def predicate(strict: bool, x: bool, y: bool) -> bool:
            result = x and y and strict
            calls.append(
                FunctionCall(params={"x": x, "y": y, "strict": strict}, result=result)
            )
            return result

        condition = Condition(predicate, params={"x": True, "y": True, "strict": True})
        result = condition.check(strict=False)

        assert result is True
        assert calls == [
            FunctionCall(params={"x": True, "y": True, "strict": True}, result=True)
        ]

    def test_find_arguments_are_provided_as_default_if_not_in_init(
        self, calls: list[FunctionCall]
    ):
        """
        Tests if find arguments (tag, strict, recursive) are not provided
        in initialization nor in check method, they take default values
        defined in check method signature.
        """

        def predicate(tag, strict: bool, recursive: bool, x: bool, y: bool) -> bool:
            result = x and y and strict and recursive and tag
            calls.append(
                FunctionCall(
                    params={
                        "x": x,
                        "y": y,
                        "strict": strict,
                        "recursive": recursive,
                        "tag": tag,
                    },
                    result=result,
                )
            )
            return result

        condition = Condition(predicate, params={"x": True, "y": True})
        result = condition.check()

        assert result is False
        assert calls == [
            FunctionCall(
                params={
                    "x": True,
                    "y": True,
                    "strict": False,
                    "recursive": True,
                    "tag": None,
                },
                result=False,
            )
        ]

    def test_two_conditions_are_equal(self):
        """
        Tests if two Condition instances with the same predicate and params
        provided at initialization are equal.
        """
        condition1 = Condition(mock_predicate, params={"x": True, "y": True})
        condition2 = Condition(mock_predicate, params={"x": True, "y": True})
        assert condition1 == condition2

    def test_two_conditions_are_not_equal_if_provided_parameters_are_different(self):
        """
        Tests if two Condition instances with the same function but different params
        provided at initialization are not equal.
        """
        condition1 = Condition(mock_predicate, params={"x": True, "y": True})
        condition2 = Condition(mock_predicate, params={"x": True, "y": False})
        assert condition1 != condition2

    def test_two_conditions_are_not_equal_if_predicates_are_different(self):
        """
        Tests if two Condition instances with different predicate functions
        are always not equal.
        """
        condition1 = Condition(mock_predicate, params={"x": True, "y": True})
        condition2 = Condition(lambda x, y: x and y, params={"x": True, "y": True})
        assert condition1 != condition2

    def test_two_conditions_are_not_equal_if_other_is_not_condition_instance(self):
        """
        Tests if Condition instance is not equal to an object of different type.
        Condition in such case should return NotImplemented
        """
        condition1 = Condition(mock_predicate, params={"x": True, "y": True})
        condition2 = mock_predicate

        assert condition1.__eq__(condition2) is NotImplemented
        assert condition1 != condition2

    @pytest.mark.integration
    def test_condition_works_with_selector_to_confirm_presence_of_element(
        self, to_element: ToElement
    ):
        """
        Test that Condition can be used with a selector
        to confirm presence of an element in the provided tag.
        """
        text = """
        <div>
            <span>Other Element</span>
            <a href="https://example.com">123</a>
        </div>
        """
        element = to_element(text)
        selector = MockLinkSelector()
        condition = Condition(lambda tag: selector.find(tag) is not None)
        result = condition.check(tag=element)
        assert result is True

    @pytest.mark.integration
    def test_condition_works_with_selector_to_confirm_presence_of_element_with_params(
        self, to_element: ToElement
    ):
        """
        Test that Condition can be used with a selector to check attribute
        value of the found element by passing additional parameters.
        """
        text = """
        <div>
            <span>Other Element</span>
            <a href="https://example.com">123</a>
        </div>
        """

        def predicate(tag, href: str, strict: bool) -> bool:
            selected = MockLinkSelector().find(tag, strict=strict)
            assert selected is not None
            real_href = selected.get_attribute("href")
            assert real_href is not None
            return real_href.strip("/") == href  # playwright adds trailing slash

        element = to_element(text)

        condition = Condition(predicate, params={"href": "https://example.com"})
        result = condition.check(tag=element)
        assert result is True

        condition2 = Condition(predicate, params={"href": "https://example123.com"})
        result = condition2.check(tag=element)
        assert result is False


@pytest.mark.operation
@pytest.mark.browser
class TestWaitUntil:
    """Tests suite for the WaitUntil operation."""

    DEFAULT_TIMEOUT = 10
    DEFAULT_CONDITION_EXECUTION_TIME = 1
    MOCK_CONDITION = Condition(lambda: False)

    class MockBool:
        def __init__(self, value: bool, revert_after: int = 1) -> None:
            self.value = value
            self.revert_after = revert_after
            self.counter = 0

        def revert(self):
            if self.counter >= self.revert_after:
                self.value = not self.value

            self.counter += 1

    class Counter:
        def __init__(self):
            self.count = 0

        def increment(self):
            self.count += 1

    def test_initialization_saves_attributes(self):
        """
        Test that WaitUntil initialization correctly saves the provided attributes
        if all of them are valid.
        """
        condition = Condition(lambda: True)
        wait_op = WaitUntil(
            condition=condition,
            timeout=self.DEFAULT_TIMEOUT,
            poll_frequency=0.0001,
            strict=True,
            recursive=False,
            ignored_exceptions=[ValueError, KeyError],
        )

        assert wait_op.condition is condition
        assert wait_op.timeout == self.DEFAULT_TIMEOUT
        assert wait_op.poll_frequency == 0.0001
        assert wait_op.strict is True
        assert wait_op.recursive is False
        assert wait_op.ignored_exceptions == [ValueError, KeyError]

    def test_initialization_raises_error_if_timeout_or_poll_frequency_negative(self):
        """
        Test that WaitUntil initialization raises an error
        if the timeout or poll frequency is negative.
        """
        with pytest.raises(ValueError):
            WaitUntil(condition=Condition(lambda: True), timeout=-1)

        with pytest.raises(ValueError):
            WaitUntil(condition=Condition(lambda: True), poll_frequency=-0.1)

    def test_initialization_raises_error_if_poll_frequency_greater_than_timeout(self):
        """
        Test that WaitUntil initialization raises an error
        if the poll frequency is greater than the timeout.
        """
        with pytest.raises(ValueError):
            WaitUntil(
                condition=Condition(lambda: True),
                timeout=self.DEFAULT_TIMEOUT,
                poll_frequency=self.DEFAULT_TIMEOUT * 2,
            )

    def test_sets_poll_frequency_to_default_if_not_provided(self):
        """
        Test that WaitUntil initialization sets poll frequency to default value
        if it's not provided. The default is timeout / 10.
        """
        wait_op = WaitUntil(
            condition=Condition(lambda: True), timeout=self.DEFAULT_TIMEOUT
        )
        assert math.isclose(wait_op.poll_frequency, self.DEFAULT_TIMEOUT / 10)

    def test_checks_the_condition_and_raises_exception_if_fails(
        self, mock_browser: MockBrowser
    ):
        """
        Test that WaitUntil operation checks the condition
        and raises an exception if the condition is not met.
        """
        mock_browser.body = MOCK_ELEMENT
        current_time = 0.0

        def fake_monotonic() -> float:
            return current_time

        def fake_sleep(seconds: float):
            nonlocal current_time
            current_time += seconds

        def condition_func():
            nonlocal current_time
            current_time += self.DEFAULT_CONDITION_EXECUTION_TIME
            return False

        condition = Condition(condition_func)
        wait_op = WaitUntil(condition=condition, timeout=self.DEFAULT_TIMEOUT)

        with patch("time.monotonic", side_effect=fake_monotonic):
            with patch("time.sleep", side_effect=fake_sleep):
                with pytest.raises(exc.FailedOperationExecution):
                    wait_op.execute(mock_browser)

    @pytest.mark.parametrize(
        argnames="execution_time, pool_frequency, expected_calls",
        argvalues=[
            (1, 2, 4),  # timeout is checked before sleeping
            (
                2,
                9,
                2,
            ),  # waiting time excedes timeout, it is still executed one more time
            (
                4,
                2,
                2,
            ),  # when after execution time is exactly at the timeout, it should not be executed again
            (
                11,
                1,
                1,
            ),  # when execution time is greater than timeout, it should be executed only once
        ],
        ids=[
            "execution_time_1_pool_frequency_2",
            "execution_time_2_pool_frequency_9",
            "execution_time_4_pool_frequency_2",
            "execution_time_11_pool_frequency_1",
        ],
    )
    def test_handles_retries_as_expected(
        self,
        mock_browser: MockBrowser,
        pool_frequency: float,
        execution_time: float,
        expected_calls: int,
    ):
        """
        Test that WaitUntil operation handles retries as expected based on the provided
        execution time of the condition and the poll frequency.
        """
        mock_browser.body = MOCK_ELEMENT
        COUNTER = self.Counter()
        current_time = 0.0

        def fake_monotonic() -> float:
            return current_time

        def fake_sleep(seconds: float):
            nonlocal current_time
            current_time += seconds

        def condition_func():
            nonlocal current_time
            current_time += execution_time
            COUNTER.increment()
            return False

        with patch("time.monotonic", side_effect=fake_monotonic):
            with patch("time.sleep", side_effect=fake_sleep):

                condition = Condition(condition_func)
                wait_op = WaitUntil(
                    condition=condition,
                    timeout=self.DEFAULT_TIMEOUT,
                    poll_frequency=pool_frequency,
                )
                with pytest.raises(exc.FailedOperationExecution):
                    wait_op.execute(mock_browser)

        assert COUNTER.count == expected_calls

    def test_passes_when_condition_is_met(self, mock_browser: MockBrowser):
        """
        Test that WaitUntil operation passes and returns the browser instance
        when the condition is met within the timeout.
        """
        mock_browser.body = MOCK_ELEMENT

        condition = Condition(lambda: True)
        wait_op = WaitUntil(condition=condition, timeout=self.DEFAULT_TIMEOUT)
        result = wait_op.execute(mock_browser)
        assert result is mock_browser

    @pytest.mark.parametrize(
        "strict, recursive",
        [(True, False), (False, True), (False, False)],
        ids=[
            "strict_true_recursive_false",
            "strict_false_recursive_true",
            "strict_false_recursive_false",
        ],
    )
    def test_execute_passes_strict_and_recursive_args_to_to_condition_and_fails(
        self, mock_browser: MockBrowser, strict: bool, recursive: bool
    ):
        """
        Test that execute method of correctly passes strict and recursive arguments
        to the condition and the condition is evaluated with those arguments.
        In this case, condition fails.
        """
        mock_browser.body = MOCK_ELEMENT
        current_time = 0.0

        def fake_monotonic() -> float:
            return current_time

        def fake_sleep(seconds: float):
            nonlocal current_time
            current_time += seconds

        def condition_func(strict: bool, recursive: bool):
            nonlocal current_time
            current_time += self.DEFAULT_CONDITION_EXECUTION_TIME
            return strict and recursive

        condition = Condition(condition_func)
        wait_op = WaitUntil(
            condition=condition,
            timeout=self.DEFAULT_TIMEOUT,
            strict=strict,
            recursive=recursive,
        )

        with patch("time.monotonic", side_effect=fake_monotonic):
            with patch("time.sleep", side_effect=fake_sleep):
                with pytest.raises(exc.FailedOperationExecution):
                    wait_op.execute(mock_browser)

    def test_execute_passes_strict_and_recursive_args_to_to_condition_and_passes(
        self, mock_browser: MockBrowser
    ):
        """
        Test that execute method of correctly passes strict and recursive arguments
        to the condition and the condition is evaluated with those arguments.
        In this case, condition passes.
        """
        mock_browser.body = MOCK_ELEMENT

        condition = Condition(lambda strict, recursive: strict and recursive)
        wait_op = WaitUntil(
            condition=condition,
            timeout=self.DEFAULT_TIMEOUT,
            strict=True,
            recursive=True,
        )

        result = wait_op.execute(mock_browser)
        assert result is mock_browser

    @pytest.mark.parametrize(
        argnames="retries",
        argvalues=[1, 3, 5],
        ids=["1 retry", "3 retries", "5 retries"],
    )
    def test_execute_passes_with_function_returning_first_false_then_true(
        self, mock_browser: MockBrowser, retries: int
    ):
        """
        Test that execute method correctly handles retries and condition
        that returns False on the first call and True on the second call.
        """
        mock_browser.body = MOCK_ELEMENT
        MOCK_COUNTER = self.Counter()
        current_time = 0.0

        def fake_monotonic() -> float:
            return current_time

        def fake_sleep(seconds: float):
            nonlocal current_time
            current_time += seconds

        def condition_func():
            nonlocal current_time
            current_time += self.DEFAULT_CONDITION_EXECUTION_TIME

            MOCK_COUNTER.increment()
            return MOCK_COUNTER.count > retries

        condition = Condition(condition_func)
        wait_op = WaitUntil(condition=condition, timeout=self.DEFAULT_TIMEOUT)

        with patch("time.monotonic", side_effect=fake_monotonic):
            with patch("time.sleep", side_effect=fake_sleep):
                result = wait_op.execute(mock_browser)

        assert result is mock_browser
        assert MOCK_COUNTER.count == retries + 1

    def test_execute_ignores_specified_exceptions(self, mock_browser: MockBrowser):
        """
        Test that execute method correctly ignores specified exceptions
        and retries until condition is met.
        """
        mock_browser.body = MOCK_ELEMENT
        RETRIES = 3
        MOCK_COUNTER = self.Counter()
        current_time = 0.0

        def fake_monotonic() -> float:
            return current_time

        def fake_sleep(seconds: float):
            nonlocal current_time
            current_time += seconds

        def condition_func():
            nonlocal current_time
            current_time += self.DEFAULT_CONDITION_EXECUTION_TIME

            MOCK_COUNTER.increment()

            if MOCK_COUNTER.count < RETRIES:
                raise ValueError("Condition not met yet")

            return True

        condition = Condition(condition_func)
        wait_op = WaitUntil(
            condition=condition,
            timeout=self.DEFAULT_TIMEOUT,
            ignored_exceptions=[ValueError],
        )

        with patch("time.monotonic", side_effect=fake_monotonic):
            with patch("time.sleep", side_effect=fake_sleep):
                result = wait_op.execute(mock_browser)

        assert result is mock_browser
        assert MOCK_COUNTER.count == 3

    def test_execute_ignores_specified_until_timeout_and_raises_error(
        self, mock_browser: MockBrowser
    ):
        """
        Test that execute method correctly ignores specified exceptions
        and retries until timeout is reached,
        after which it raises FailedOperationExecution.
        """
        mock_browser.body = MOCK_ELEMENT
        current_time = 0.0

        def fake_monotonic() -> float:
            return current_time

        def fake_sleep(seconds: float):
            nonlocal current_time
            current_time += seconds

        def condition_func():
            nonlocal current_time
            current_time += self.DEFAULT_CONDITION_EXECUTION_TIME
            raise ValueError("Condition will never be met mf")

        condition = Condition(condition_func)
        wait_op = WaitUntil(
            condition=condition,
            timeout=self.DEFAULT_TIMEOUT,
            ignored_exceptions=[ValueError],
        )

        with patch("time.monotonic", side_effect=fake_monotonic):
            with patch("time.sleep", side_effect=fake_sleep):
                with pytest.raises(exc.FailedOperationExecution):
                    wait_op.execute(mock_browser)

    def test_execute_raises_error_when_arg_is_not_browser(self):
        """
        Test that execute method raises NotBrowserException
        when the argument is not an instance of IBrowser.
        """
        condition = Condition(lambda: True)
        wait_op = WaitUntil(condition=condition)

        with pytest.raises(exc.NotBrowserException):
            wait_op.execute("not a browser")  # type: ignore

    def test_equality_returns_not_implemented_when_other_is_not_wait_until(self):
        """
        Test that WaitUntil equality method returns NotImplemented
        when the other object is not an instance of WaitUntil.
        """
        condition = Condition(lambda: True)
        wait_op = WaitUntil(condition=condition)

        assert wait_op.__eq__("not a WaitUntil") is NotImplemented

    def test_wait_until_equality_true(self):
        """
        Test equality for WaitUntil operations with the same condition.
        All attributes must be the same.
        """
        condition = Condition(lambda: True)
        op1 = WaitUntil(
            condition=condition,
            timeout=self.DEFAULT_TIMEOUT,
            poll_frequency=0.0001,
            strict=True,
            recursive=False,
        )
        op2 = WaitUntil(
            condition=condition,
            timeout=self.DEFAULT_TIMEOUT,
            poll_frequency=0.0001,
            strict=True,
            recursive=False,
        )
        assert op1 == op2

    def test_equal_if_ignored_exceptions_are_in_different_order(self):
        """
        Test if two WaitUntil operations with the same condition
        and the same ignored exceptions (regardless of order) are equal.
        """
        condition = Condition(lambda: True)
        op1 = WaitUntil(
            condition=condition,
            ignored_exceptions=[ValueError, TypeError, KeyError],
        )
        op2 = WaitUntil(
            condition=condition,
            ignored_exceptions=[TypeError, ValueError, KeyError],
        )
        assert op1 == op2

    @pytest.mark.parametrize(
        argnames="params",
        argvalues=[
            (
                WaitUntil(condition=MOCK_CONDITION),
                WaitUntil(condition=Condition(lambda: True)),
            ),
            (
                WaitUntil(condition=MOCK_CONDITION, timeout=0.01),
                WaitUntil(condition=MOCK_CONDITION, timeout=0.02),
            ),
            (
                WaitUntil(condition=MOCK_CONDITION, timeout=0.01, poll_frequency=0.004),
                WaitUntil(condition=MOCK_CONDITION, timeout=0.01, poll_frequency=0.005),
            ),
            (
                WaitUntil(condition=MOCK_CONDITION, timeout=0.01, poll_frequency=None),
                WaitUntil(condition=MOCK_CONDITION, timeout=0.01, poll_frequency=0.005),
            ),
            (
                WaitUntil(condition=MOCK_CONDITION, strict=True),
                WaitUntil(condition=MOCK_CONDITION, strict=False),
            ),
            (
                WaitUntil(condition=MOCK_CONDITION, recursive=True),
                WaitUntil(condition=MOCK_CONDITION, recursive=False),
            ),
            (
                WaitUntil(condition=MOCK_CONDITION, ignored_exceptions=[ValueError]),
                WaitUntil(condition=MOCK_CONDITION, ignored_exceptions=[TypeError]),
            ),
        ],
        ids=[
            "different conditions",
            "different timeouts",
            "different poll frequencies",
            "default vs provided poll frequency",
            "different strict",
            "different recursive",
            "different ignored exceptions",
        ],
    )
    def test_wait_until_equality_false(self, params: tuple[WaitUntil, WaitUntil]):
        """
        Test inequality for WaitUntil operations with different parameters.
        Any difference in attributes should result in inequality.
        """
        op1, op2 = params
        assert op1 != op2

    @pytest.mark.edge_case
    def test_condition_args_take_precedence_over_wait_until_args(
        self, mock_browser: MockBrowser
    ):
        """
        Test that when the same arguments (strict, recursive)
        are provided in both Condition and WaitUntil,
        the arguments provided in Condition take precedence
        and are used in condition evaluation.
        """
        mock_browser.body = MOCK_ELEMENT

        condition = Condition(
            lambda strict, recursive: strict and recursive,
            params={"strict": True, "recursive": True},
        )
        wait_op = WaitUntil(
            condition=condition,
            timeout=self.DEFAULT_TIMEOUT,
            strict=False,
            recursive=False,
        )

        result = wait_op.execute(mock_browser)
        assert result is mock_browser
