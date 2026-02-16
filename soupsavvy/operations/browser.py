"""
Module defining browser operations for web automation tasks.
Contains typical browser operations and actions on web elements.
"""

import functools
import inspect
import math
import time
from collections.abc import Callable
from contextlib import suppress
from typing import Any, Optional

import soupsavvy.exceptions as exc
from soupsavvy.base import (
    BaseOperation,
    BrowserOperation,
    ElementAction,
    SoupSelector,
    check_tag_searcher,
)
from soupsavvy.interfaces import Comparable, IBrowser, IElement, TagSearcher


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


class Condition(Comparable):
    """
    Wraps a predicate function and prepares it to be evaluated as a condition.
    `Condition` binds a subset of keyword arguments to the given predicate in
    advance, while deferring a specific set of arguments (``tag``, ``strict``,
    and ``recursive``) to be provided later when :meth:`check` is called.
    This is useful for building reusable conditions that can be evaluated
    against different elements or search configurations.

    Examples
    --------
    >>> from soupsavvy.operations.browser import Condition
    >>> condition = Condition(lambda tag, text: tag.text == text, params={"text": "Hello"})
    >>> condition.check(tag=some_element)
    True

    Conditions are typically used in conjunction with higher-level browser
    operations (such as waiting utilities) that repeatedly call
    :meth:`check` until the predicate is satisfied.
    """

    _FIND_ARGUMENTS = {"tag", "strict", "recursive"}

    def __init__(
        self,
        predicate: Callable[..., Any],
        params: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Initializes the Condition with a predicate function and bound parameters.

        Parameters
        ----------
        predicate : Callable
            A callable that represents the condition to evaluate.
            Any parameters required by ``predicate`` can be supplied
            via ``params``.
        params : dict[str, Any], optional
            Mapping of keyword arguments to bind to ``predicate`` at construction
            time. These parameters are validated against the callable's signature.

        predicate:
            It accepts ``TagSearcher`` parameters (``tag``, ``strict``, and ``recursive``)
            without the need to specify them in ``params``. They can be supplied
            when calling :meth:`check`. Bound parameters always take precedence.
            Function should return boolean value, but it is not strictly required
            as the result will be cast to bool.

        Raises
        ------
        InvalidParametersBinding
            If the provided ``params`` cannot be bound to ``predicate`` (for
            example, when required parameters other than ``tag``, ``strict``,
            or ``recursive`` are missing or unexpected parameters are supplied).
        """
        params = params or {}
        signature = inspect.signature(predicate)

        try:
            bound_args = signature.bind_partial(**params)
        except TypeError as e:
            raise exc.InvalidParametersBinding(
                f"Error binding provided parameters to predicate: {e}"
            ) from e

        first_args = bound_args.arguments
        missing = {x for x in signature.parameters if x not in first_args}
        missing_required = {
            x
            for x in missing
            if signature.parameters[x].default is inspect.Parameter.empty
            and signature.parameters[x].kind
            not in {inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD}
        }

        check = missing_required - self._FIND_ARGUMENTS

        if check:
            raise exc.InvalidParametersBinding(
                "Not all required parameters were provided for the predicate. "
                f"Missing: {', '.join(check)}"
            )

        kwargs_name = next(
            (
                x
                for x in signature.parameters
                if signature.parameters[x].kind is inspect.Parameter.VAR_KEYWORD
            ),
            None,
        )
        # unpacking kwargs if present
        first_args |= first_args.pop(kwargs_name, {})  # type: ignore

        self._to_provide = self._FIND_ARGUMENTS & missing
        self.predicate = functools.partial(predicate, **first_args)

    def check(
        self,
        tag: Optional[IElement] = None,
        strict: bool = False,
        recursive: bool = True,
    ) -> bool:
        """
        Evaluates the condition by calling the underlying predicate
        with bound parameters and provided `TagSearcher` arguments only if acceptable
        by the predicate's signature.

        Parameters
        ----------
        tag : IElement
            Any `IElement` object to process.
        strict : bool, optional
            If True, enforces results to be found in the element, by default False.
        recursive : bool, optional
            Specifies if search should be recursive.
            If set to `False`, only direct children of the element will be searched.
            By default `True`.

        Returns
        -------
        bool
            The result of evaluating the predicate, always cast to a boolean value.
        """
        dynamic_params = {
            "tag": tag,
            "strict": strict,
            "recursive": recursive,
        }

        to_provide = {k: v for k, v in dynamic_params.items() if k in self._to_provide}
        signature = inspect.signature(self.predicate)
        params = signature.bind_partial(**to_provide).arguments
        result = self.predicate(**params)
        return bool(result)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Condition):
            return NotImplemented

        return (
            self.predicate.func == other.predicate.func
            and self.predicate.args == other.predicate.args
            and self.predicate.keywords == other.predicate.keywords
        )


class WaitUntil(BrowserOperation):
    """
    Repeatedly evaluates a :class:`Condition` until it is satisfied or a timeout occurs.
    This operation polls the current browser document at a fixed interval, checking
    whether the provided :class:`Condition` returns ``True``.

    Examples
    --------
    >>> from soupsavvy.operations.browser import WaitUntil, Condition
    ...
    ... condition = Condition(lambda tag: tag.get_attribute("title") == "Dashboard")
    ... wait_op = WaitUntil(condition, timeout=20.0, poll_frequency=1.0)
    ... wait_op.execute(browser)

    Raises
    ------
    ConditionFailedException
        If the condition is not satisfied before the timeout expires.
    NotBrowserException
        If this operation is executed with an object that does not implement
        the :class:`IBrowser` interface.
    """

    def __init__(
        self,
        condition: Condition,
        timeout: float = 10.0,
        poll_frequency: Optional[float] = None,
        strict: bool = False,
        recursive: bool = True,
        ignored_exceptions: Optional[list[type[BaseException]]] = None,
    ) -> None:
        """
        Initializes the WaitUntil operation with the specified condition and parameters.

        Parameters
        ----------
        condition: Condition
            A :class:`Condition` instance encapsulating the predicate to be checked
            against the browser's current document.
        timeout: float
            Maximum time in seconds to wait for the condition to become ``True``.
            Must be a positive number.
        poll_frequency: float, optional
            Interval in seconds between condition checks. If ``None``,
            a default of ``timeout / 10`` is used. Must be positive and not greater
            than ``timeout``.
        strict: bool
            If ``True``, the underlying condition is evaluated with ``strict=True``.
        recursive: bool
            If ``True`` (the default), the condition is evaluated with ``recursive=True``.
        ignored_exceptions: list[type[BaseException]], optional
            A list of exception types that should be suppressed while evaluating
            the condition. If any of these exceptions are raised by the condition
            they are caught and ignored, and the condition
            is retried until the timeout is reached.

        Raises
        ------
        ValueError
            If ``timeout`` is not positive, if ``poll_frequency`` is not positive,
            or if ``poll_frequency`` is greater than ``timeout``.
        """
        if timeout <= 0:
            raise ValueError("Timeout must be a positive number.")

        if poll_frequency is None:
            poll_frequency = timeout / 10

        if poll_frequency <= 0:
            raise ValueError("Poll frequency must be a positive number.")

        if poll_frequency > timeout:
            raise ValueError("Poll frequency cannot be greater than timeout.")

        self.condition = condition
        self.timeout = timeout
        self.poll_frequency = poll_frequency
        self.strict = strict
        self.recursive = recursive
        self.ignored_exceptions = ignored_exceptions or []

    def _execute(self, browser: IBrowser) -> None:
        start = time.monotonic()
        deadline = start + self.timeout
        attempts = 0

        while True:
            attempts += 1
            document = browser.get_document()

            with suppress(*self.ignored_exceptions):
                if self.condition.check(
                    document,
                    strict=self.strict,
                    recursive=self.recursive,
                ):
                    return

            now = time.monotonic()

            if now >= deadline:
                raise exc.ConditionFailedException(
                    f"Condition {self.condition} was not met after "
                    f"{now - start:.2f}s "
                    f"({attempts} attempts, poll={self.poll_frequency}s)."
                )

            time.sleep(min(self.poll_frequency, max(0, deadline - now)))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, WaitUntil):
            return NotImplemented

        return (
            self.condition == other.condition
            and math.isclose(self.timeout, other.timeout)
            and math.isclose(self.poll_frequency, other.poll_frequency)
            and self.strict == other.strict
            and self.recursive == other.recursive
            and set(self.ignored_exceptions) == set(other.ignored_exceptions)
        )


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
        self.method = functools.partial(method, **kwargs)

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
