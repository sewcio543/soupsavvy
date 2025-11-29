"""
Module defining browser operations for web automation tasks.
Contains typical browser operations and actions on web elements.
"""

import time
from collections.abc import Callable
from functools import partial
from typing import Any, Optional

import soupsavvy.exceptions as exc
from soupsavvy.base import (
    BaseOperation,
    BrowserOperation,
    Condition,
    ElementAction,
    SoupSelector,
    check_tag_searcher,
)
from soupsavvy.interfaces import IBrowser, IElement, TagSearcher


class ApplyTo(BrowserOperation):
    """
    Applies a given action to a single element selected from the browser document.

    This operation uses a :class:`SoupSelector` to find a target element
    within the browser's DOM and then executes the provided :class:`ElementAction`
    on it.

    Parameters
    ----------
    selector : SoupSelector
        Selector used to locate the target element in the document.
    action : ElementAction
        Action to execute on the selected element.

    Raises
    ------
    soupsavvy.exceptions.FailedOperationExecution
        If the element cannot be found using the provided selector.
    """

    def __init__(self, selector: SoupSelector, action: ElementAction) -> None:
        self.selector = selector
        self.action = action

    def _execute(self, browser: IBrowser) -> None:
        body = browser.get_document()

        try:
            element = self.selector.find(body, strict=True)
        except exc.TagNotFoundException as e:
            raise exc.FailedOperationExecution(
                f"Failed to find element using selector {self.selector} "
                f" - action {self.action} cannot be applied - {e}"
            )
        return self.action.execute(browser=browser, element=element)

    def __eq__(self, x: Any) -> bool:
        if not isinstance(x, self.__class__):
            return NotImplemented

        return self.selector == x.selector and self.action == x.action


class Navigate(BrowserOperation):
    """
    Operation for navigating the browser to a specified URL.

    Example
    -------
    >>> from soupsavvy.operations.browser import Navigate
    ... from soupsavvy.implementation.selenium import SeleniumBrowser
    ... from selenium import webdriver
    ...
    ... browser = SeleniumBrowser(webdriver.Chrome())
    ... operation = Navigate("https://example.com")
    ... operation.execute(browser)
    """

    def __init__(self, url: str) -> None:
        """
        Initializes the Navigate operation with the specified URL.

        Parameters
        ----------
        url : str
            The target URL to navigate to.
        """
        self.url = url

    def _execute(self, browser: IBrowser) -> None:
        browser.navigate(self.url)

    def __eq__(self, x: Any) -> bool:
        if not isinstance(x, self.__class__):
            return NotImplemented

        return self.url == x.url


class WaitImplicitly(BaseOperation):
    """
    Pauses execution for a specified number of seconds.
    Useful for browser operations that require waiting for a page to load
    or for dynamic content to render.

    Example
    -------
    >>> from soupsavvy.operations.browser import WaitImplicitly
    ... operation = WaitImplicitly(5)
    ... operation.execute(None)

    It proves more useful when chained with other browser operations.

    Example
    -------
    >>> from soupsavvy.operations.browser import WaitImplicitly, Navigate
    ... from soupsavvy.implementation.selenium import SeleniumBrowser
    ... from selenium import webdriver
    ...
    ... browser = SeleniumBrowser(webdriver.Chrome())
    ... operation = Navigate("https://example.com") | WaitImplicitly(5)
    ... operation.execute(browser)

    `WaitImplicitly` uses `time.sleep` under the hood, it does not require
    a browser instance to operate and can be used independently.
    """

    def __init__(self, seconds: float) -> None:
        """
        Initializes the WaitImplicitly operation with the specified wait time.

        Parameters
        ----------
        seconds : float
            Number of seconds to wait.
        """
        self.seconds = seconds

    def _execute(self, x: Any) -> None:
        time.sleep(self.seconds)
        return x

    def __eq__(self, x: Any) -> bool:
        if not isinstance(x, self.__class__):
            return NotImplemented

        return self.seconds == x.seconds


class WaitUntil(BrowserOperation):

    def __init__(
        self,
        condition: Condition,
        timeout: float,
        poll_frequency: float = 0.5,
        strict: bool = False,
        recursive: bool = True,
    ) -> None:
        """
        Initializes the WaitUntil operation with the specified condition and timeout.

        Parameters
        ----------
        condition : Condition
            Condition to be met for the wait to end.
        timeout : float
            Maximum number of seconds to wait for the condition to be met.
        poll_frequency : float, optional
            Frequency in seconds to check the condition. Default is 0.5 seconds.
        strict : bool, optional
            Whether to enforce strict finding in the condition. Default is False.
        recursive : bool, optional
            Whether to search recursively in the condition. Default is True.
        """
        self.condition = condition
        self.timeout = timeout
        self.poll_frequency = poll_frequency
        self.strict = strict
        self.recursive = recursive

    def _execute(self, browser: IBrowser) -> None:
        start_time = time.time()

        while True:
            body = browser.get_document()
            if self.condition.find(body, strict=self.strict, recursive=self.recursive):
                return

            elapsed_time = time.time() - start_time
            if elapsed_time >= self.timeout:
                raise Exception(
                    f"Condition {self.condition} was not met within {self.timeout} seconds."
                )

            time.sleep(self.poll_frequency)


class Click(ElementAction):
    """
    Clicks on a target element using the browser context.

    Example
    -------
    >>> from soupsavvy.operations.browser import Click
    ... from soupsavvy import TypeSelector
    ...
    ... operation = Click()
    ... selector = TypeSelector('button')
    ... element = selector.find(page, strict=True)
    ... operation.execute(browser)

    It proves more useful when used in conjunction with `ApplyTo` operation,
    which can be integrated into browser workflows.

    Example
    -------
    >>> from soupsavvy.operations.browser import ApplyTo, Click, Navigate
    ... from soupsavvy import TypeSelector
    ... from soupsavvy.implementation.selenium import SeleniumBrowser
    ... from selenium import webdriver
    ...
    ... browser = SeleniumBrowser(webdriver.Chrome())
    ... action = Click()
    ... selector = TypeSelector('a')
    ... operation = Navigate("https://example.com") | ApplyTo(selector, action)
    ... operation.execute(browser)
    """

    def _execute(self, browser: IBrowser, element: IElement) -> None:
        browser.click(element)

    def __eq__(self, x: Any) -> bool:
        if not isinstance(x, self.__class__):
            return NotImplemented

        return True


class SendKeys(ElementAction):
    """
    Sends a string of keys or text input to a target element.

    Example
    -------
    >>> from soupsavvy.operations.browser import SendKeys
    ... from soupsavvy import TypeSelector
    ...
    ... operation = SendKeys("Hello, World!")
    ... selector = TypeSelector('input')
    ... element = selector.find(page, strict=True)
    ... operation.execute(browser)

    It proves more useful when used in conjunction with `ApplyTo` operation,
    which can be integrated into browser workflows.

    Example
    -------
    >>> from soupsavvy.operations.browser import ApplyTo, SendKeys, Navigate
    ... from soupsavvy import TypeSelector
    ... from soupsavvy.implementation.selenium import SeleniumBrowser
    ... from selenium import webdriver
    ...
    ... browser = SeleniumBrowser(webdriver.Chrome())
    ... action = SendKeys("Hello, World!")
    ... selector = TypeSelector('input')
    ... operation = Navigate("https://example.com") | ApplyTo(selector, action)
    ... operation.execute(browser)
    """

    def __init__(self, value: str, clear: bool = True) -> None:
        """
        Initializes the SendKeys action with the specified input value.

        Parameters
        ----------
        value : str
            The string or keys to send to the element.
        clear : bool, optional
            Whether to clear the element's existing content before sending keys.
            Default is True.
        """
        self.value = value
        self.clear = clear

    def _execute(self, browser: IBrowser, element: IElement) -> None:
        browser.send_keys(element=element, value=self.value, clear=self.clear)

    def __eq__(self, x: Any) -> bool:
        if not isinstance(x, self.__class__):
            return NotImplemented

        return self.value == x.value and self.clear == x.clear


class _FindBase(BrowserOperation):
    """
    Base class for searching browser operations to share common functionality.
    """

    _PASSTHROUGH_BROWSER = False

    def __init__(self, selector: TagSearcher, method: Callable, kwargs: dict) -> None:
        self.selector = selector
        self.method = partial(method, **kwargs)

    def _execute(self, browser: IBrowser) -> Any:
        body = browser.get_document()
        return self.method(body)

    def __eq__(self, x: Any) -> bool:
        if not isinstance(x, self.__class__):
            return NotImplemented

        return self.selector == x.selector


class Find(_FindBase):
    """
    Finds and returns an element from the browser document using a specified selector.

    Example
    -------
    >>> from soupsavvy.operations.browser import Find
    ... from soupsavvy import TypeSelector
    ... from soupsavvy.implementation.selenium import SeleniumBrowser
    ... from selenium import webdriver
    ...
    ... browser = SeleniumBrowser(webdriver.Chrome())
    ... selector = TypeSelector('div')
    ... operation = Find(selector)
    ... operation.execute(browser)

    It can be used as an element of browser workflows to extract information
    from web pages, for example: navigate -> click -> wait -> find.
    """

    def __init__(self, selector: TagSearcher, strict: bool = False) -> None:
        """
        Initializes the Find operation with the specified selector.

        Parameters
        ----------
        selector : TagSearcher
            Selector used to locate the target element in the document.
        strict : bool, optional
            Whether to enforce strict finding (raise exception if not found).
            Default is False.
        """
        super().__init__(
            selector,
            method=check_tag_searcher(selector).find,
            kwargs={"strict": strict},
        )


class FindAll(_FindBase):
    """
    Finds and returns elements from the browser document using a specified selector.

    Example
    -------
    >>> from soupsavvy.operations.browser import FindAll
    ... from soupsavvy import TypeSelector
    ... from soupsavvy.implementation.selenium import SeleniumBrowser
    ... from selenium import webdriver
    ...
    ... browser = SeleniumBrowser(webdriver.Chrome())
    ... selector = TypeSelector('div')
    ... operation = FindAll(selector)
    ... operation.execute(browser)
    [...]

    It can be used as an element of browser workflows to extract information
    from web pages, for example: navigate -> click -> wait -> find_all.
    """

    def __init__(self, selector: TagSearcher, limit: Optional[int] = None) -> None:
        """
        Initializes the FindAll operation with the specified selector.

        Parameters
        ----------
        selector : TagSearcher
            Selector used to locate the target element in the document.
        limit : int, optional
            Maximum number of elements to find. Default is None (no limit).
        """
        super().__init__(
            selector,
            method=check_tag_searcher(selector).find_all,
            kwargs={"limit": limit},
        )
