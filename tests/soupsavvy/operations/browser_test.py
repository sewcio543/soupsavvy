"""Unit tests for operations specific to browser context."""

from typing import cast
from unittest.mock import patch

import pytest

import soupsavvy.exceptions as exc
from soupsavvy.base import ElementAction
from soupsavvy.interfaces import IBrowser, IElement
from soupsavvy.operations.browser import (
    ApplyTo,
    Click,
    Navigate,
    SendKeys,
    WaitImplicitly,
)
from soupsavvy.operations.general import OperationPipeline
from tests.soupsavvy.conftest import MockBrowser as MockB
from tests.soupsavvy.conftest import MockDivSelector, MockLinkSelector, ToElement

FAIL = "fail"
FAILED_ERROR = "Action failed"

MOCK_TEXT = "mock-element"
MOCK_ELEMENT = cast(IElement, MOCK_TEXT)


class MockBrowser(MockB):
    """Mock browser that records interactions for testing."""

    def __init__(self, browser, *args, **kwargs):
        super().__init__(browser, *args, **kwargs)
        self.visited_urls = []
        self.clicked_elements = []
        self.sent_keys = []
        self.body: IElement | None = None

    def navigate(self, url: str) -> None:
        if url == FAIL:
            raise Exception(FAILED_ERROR)

        self.visited_urls.append(url)

    def click(self, element: IElement) -> None:
        if element == FAIL:
            raise Exception(FAILED_ERROR)

        self.clicked_elements.append(element)

    def send_keys(self, element: IElement, value: str, clear: bool = True) -> None:
        if element == FAIL:
            raise Exception(FAILED_ERROR)

        self.sent_keys.append((element, value, clear))

    def get_document(self) -> IElement:
        if self.body is None:
            raise Exception("No document set in MockBrowser")

        return self.body


class MockAction(ElementAction):
    """Mock action that records interactions for testing."""

    def __init__(self, arg=None) -> None:
        self.interactions = []
        self.arg = arg

    def _execute(self, browser: IBrowser, element: IElement) -> None:
        if element == FAIL:
            raise Exception(FAILED_ERROR)

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

    def test_navigate_executes_browser_navigation(self):
        """
        Test that Navigate calls browser.navigate() with the correct URL.
        It should also return the browser instance and set the url attribute.
        """
        url = "https://example.com"
        fake_browser = MockBrowser(...)
        op = Navigate(url)
        assert op.url == url

        result = op.execute(fake_browser)

        assert fake_browser.visited_urls == [url]
        assert result is fake_browser

    def test_navigate_propagates_browser_exception(self):
        """Test that Navigate propagates exceptions from browser.navigate()."""
        fake_browser = MockBrowser(...)
        op = Navigate(FAIL)

        with pytest.raises(Exception, match=FAILED_ERROR):
            op.execute(fake_browser)

        assert fake_browser.visited_urls == []

    def test_raises_error_when_arg_is_not_browser(self):
        """
        Test that Navigate raises NotBrowserException
        when the argument is not an instance of IBrowser.
        """
        op = Navigate("https://example.com")

        with pytest.raises(exc.NotBrowserException):
            op.execute("not a browser")  # type: ignore

    def test_navigate_multiple_calls(self):
        """Test that multiple calls to browser.navigate are recorded correctly."""
        fake_browser = MockBrowser(...)
        op1 = Navigate("https://example.com")
        op2 = Navigate("https://openai.com")

        op1.execute(fake_browser)
        op1.execute(fake_browser)
        op2.execute(fake_browser)

        assert fake_browser.visited_urls == [
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

    def test_click_executes_action_on_provided_element(self):
        """
        Test that Click performs action on provided element.
        execute method should return None as this is not browser operation but action.
        """
        fake_browser = MockBrowser(...)
        op = Click()

        result = op.execute(browser=fake_browser, element=MOCK_ELEMENT)

        assert result is None
        assert fake_browser.clicked_elements == [MOCK_TEXT]

    def test_click_executes_multiple_calls(self):
        """Test that multiple Click actions are executed correctly."""
        fake_browser = MockBrowser(...)
        op1 = Click()
        op2 = Click()

        mock_2 = cast(IElement, "Hello")

        op1.execute(browser=fake_browser, element=MOCK_ELEMENT)
        op1.execute(browser=fake_browser, element=MOCK_ELEMENT)
        op2.execute(browser=fake_browser, element=mock_2)

        assert fake_browser.clicked_elements == [MOCK_TEXT, MOCK_TEXT, "Hello"]

    def test_click_propagates_browser_exception(self):
        """Test that Click propagates exceptions from the browser."""
        fake_browser = MockBrowser(...)
        op = Click()

        with pytest.raises(Exception, match=FAILED_ERROR):
            op.execute(browser=fake_browser, element=cast(IElement, FAIL))

        assert fake_browser.clicked_elements == []

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
    def test_sendkeys_executes_action_on_provided_element(self, clear: bool):
        """
        Test that SendKeys performs the send keys action on provided element.
        execute method should return None as this is not browser operation but action.
        Attributes value and clear should be set correctly.
        """
        value = "test input"

        fake_browser = MockBrowser(...)
        op = SendKeys(value, clear=clear)

        assert op.value == value
        assert op.clear == clear

        result = op.execute(browser=fake_browser, element=MOCK_ELEMENT)

        assert result is None
        assert fake_browser.sent_keys == [(MOCK_ELEMENT, value, clear)]

    def test_sendkeys_propagates_browser_exception(self):
        """Test that SendKeys propagates exceptions from the browser."""
        fake_browser = MockBrowser(...)
        op = SendKeys("test input")

        with pytest.raises(Exception, match=FAILED_ERROR):
            op.execute(browser=fake_browser, element=cast(IElement, FAIL))

        assert fake_browser.sent_keys == []

    def test_sendkeys_executes_multiple_calls(self):
        """Test that multiple SendKeys actions are executed correctly."""
        fake_browser = MockBrowser(...)
        op1 = SendKeys("first input", clear=True)
        op2 = SendKeys("second input", clear=False)

        mock2 = cast(IElement, "Hello")

        op1.execute(browser=fake_browser, element=MOCK_ELEMENT)
        op1.execute(browser=fake_browser, element=mock2)
        op2.execute(browser=fake_browser, element=MOCK_ELEMENT)

        assert fake_browser.sent_keys == [
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
        [MockBrowser(...), "any argument", None],
        ids=["browser", "string", "none"],
    )
    def test_waitimplicitly_executes_browser_wait(self, arg):
        """Test that WaitImplicitly calls time.sleep() with the correct timeout."""
        op = WaitImplicitly(0.01)

        with patch("time.sleep") as mock_sleep:
            result = op.execute(arg)

            mock_sleep.assert_called_once_with(0.01)
            assert result is arg

    def test_can_be_used_with_any_argument(self):
        """
        Test that WaitImplicitly can be used with any argument,
        as it does not matter and is simply ignored.
        """
        op = WaitImplicitly(0.01)

        with patch("time.sleep") as mock_sleep:
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

    def test_applyto_executes_action_on_found_element(self, to_element: ToElement):
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

        fake_browser = MockBrowser(...)
        fake_browser.body = element

        selector = MockLinkSelector()
        action = MockAction()

        op = ApplyTo(selector=selector, action=action)

        assert op.selector is selector
        assert op.action is action

        result = op.execute(fake_browser)

        assert result is fake_browser
        assert action.interactions == [(fake_browser, expected)]

    def test_applyto_propagates_action_exception(self, to_element: ToElement):
        """Test that ApplyTo propagates exceptions from the action."""
        text = """
            <a href="https://example.com">Example Link</a>
        """
        element = to_element(text)

        fake_browser = MockBrowser(...)
        fake_browser.body = element

        selector = ErrorSelector()
        action = MockAction()

        op = ApplyTo(selector=selector, action=action)

        with pytest.raises(Exception, match=FAILED_ERROR):
            op.execute(fake_browser)

        assert action.interactions == []

    def test_applyto_raises_when_selector_does_not_find_element(
        self, to_element: ToElement
    ):
        """
        Test that ApplyTo raises FailedOperationExecution
        when the selector does not find matching element.
        """
        text = """
            <div>No links here</div>
        """
        element = to_element(text)

        fake_browser = MockBrowser(...)
        fake_browser.body = element

        selector = MockLinkSelector()
        action = MockAction()

        op = ApplyTo(selector=selector, action=action)

        with pytest.raises(exc.FailedOperationExecution):
            op.execute(fake_browser)

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

    def test_operations_are_executed_in_pipeline(self, to_element: ToElement):
        """
        Test that multiple browser operations can be executed in a pipeline
        in correct order.
        """
        browser = MockBrowser(...)

        text = """
            <div><a href="https://example.com">Example Link</a></div>
        """
        element = to_element(text)
        link = element.find_all("a")[0]
        browser.body = element

        op1 = Navigate("https://example.com")
        action = MockAction()
        op2 = ApplyTo(selector=MockLinkSelector(), action=action)
        pipe = op1 | op2
        result = pipe.execute(browser)

        assert result is browser
        assert browser.visited_urls == ["https://example.com"]
        assert action.interactions == [(browser, link)]

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
