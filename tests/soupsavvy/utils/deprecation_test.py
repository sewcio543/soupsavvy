"""
Module for testing the deprecation module from utils.
It is respnsible for handling the deprecation of functions and warnings.
"""

import warnings
from typing import Type

import pytest

from soupsavvy.utils.deprecation import (
    deprecated,
    deprecated_class,
    deprecated_function,
)


class CustomWarning(Warning):
    """Custom warning class for testing purposes"""


@pytest.mark.deprecation
class TestDeprecated:
    """Class with unit tests for the deprecated function"""

    @pytest.mark.parametrize(
        argnames="message",
        argvalues=[
            "This function is deprecated",
            "DEPRECATED: This function is deprecated",
        ],
    )
    def test_message_of_warning_is_the_same_as_passed_string(self, message: str):
        """
        Tests if the message of the warning is the same
        as string passed as function argument.
        """

        with warnings.catch_warnings(record=True) as w:
            deprecated(message)

        assert len(w) == 1
        assert str(w[0].message) == message

    def test_default_warning_type_is_deprecation_warning(self):
        """Tests if the default warning type is DeprecationWarning."""

        with warnings.catch_warnings(record=True) as w:
            deprecated("DEPRECATED")

        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)

    @pytest.mark.parametrize(
        argnames="warning",
        argvalues=[
            DeprecationWarning,
            FutureWarning,
            CustomWarning,
        ],
        ids=[
            "DeprecationWarning",
            "FutureWarning",
            "CustomWarning",
        ],
    )
    def test_raises_warning_type_specified_as_parameter_with_expected_message(
        self, warning: Type[Warning]
    ):
        """
        Tests if the warning raised is of the type specified as parameter
        and has the expected message.
        """
        message = "DEPRECATED"

        with warnings.catch_warnings(record=True) as w:
            deprecated(message, warning=warning)

        assert len(w) == 1
        assert issubclass(w[0].category, warning)
        assert str(w[0].message) == message

    def test_raises_warning_when_called_not_directly(self):
        """
        Tests if the warning is raised when the deprecated function is called
        not directly, but as a result of another function call.
        """
        message = "DEPRECATED"

        def raises():
            deprecated(message)

        with warnings.catch_warnings(record=True) as w:
            raises()

        assert len(w) == 1
        assert str(w[0].message) == message

    @pytest.mark.parametrize(
        argnames="warning",
        argvalues=[
            DeprecationWarning,
            FutureWarning,
            CustomWarning,
        ],
        ids=[
            "DeprecationWarning",
            "FutureWarning",
            "CustomWarning",
        ],
    )
    def test_sets_to_always_temporarily_and_restores_warning_filter(
        self, warning: Type[Warning]
    ):
        """
        Tests if the warning filter is temporarily set to "always"
        and restored to the previous state after the deprecated function call.
        """
        message = "DEPRECATED"
        # set the warning filter to ignore the specific warning
        warnings.filterwarnings("ignore", category=warning)

        with warnings.catch_warnings(record=True) as w:
            # filter should be temporarily disabled with deprecated function
            deprecated(message, warning=warning)
            assert len(w) == 1

        with warnings.catch_warnings(record=True) as w:
            # filter should be enabled again and no warning should be raised
            warnings.warn("DEPRECATED", category=warning)
            assert len(w) == 0


@pytest.mark.deprecation
class TestDeprecatedFunction:
    """Class with unit tests for the deprecated_function decorator"""

    @pytest.mark.parametrize(
        argnames="message",
        argvalues=[
            "This function is deprecated",
            "DEPRECATED: This function is deprecated",
        ],
    )
    def test_has_the_same_warning_message_as_passed(self, message: str):
        """Tests if the warning message is the same as the one passed as parameter."""

        @deprecated_function(message)
        def func(): ...

        with warnings.catch_warnings(record=True) as w:
            func()

        assert len(w) == 1
        assert str(w[0].message) == message

    def test_default_warning_type_is_deprecation_warning(self):
        """Tests if the default warning type is DeprecationWarning."""

        @deprecated_function("DEPRECATED")
        def func(): ...

        with warnings.catch_warnings(record=True) as w:
            func()

        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)

    @pytest.mark.parametrize(
        argnames="warning",
        argvalues=[
            DeprecationWarning,
            FutureWarning,
            CustomWarning,
        ],
        ids=[
            "DeprecationWarning",
            "FutureWarning",
            "CustomWarning",
        ],
    )
    def test_raises_warning_type_specified_as_parameter_with_expected_message(
        self, warning: Type[Warning]
    ):
        """
        Tests if the warning raised is of the type specified as parameter
        and has the expected message.
        """
        message = "DEPRECATED"

        @deprecated_function(message, warning=warning)
        def func(): ...

        with warnings.catch_warnings(record=True) as w:
            func()

        assert len(w) == 1
        assert issubclass(w[0].category, warning)
        assert str(w[0].message) == message

    @pytest.mark.parametrize(
        argnames="warning",
        argvalues=[
            DeprecationWarning,
            FutureWarning,
            CustomWarning,
        ],
        ids=[
            "DeprecationWarning",
            "FutureWarning",
            "CustomWarning",
        ],
    )
    def test_sets_to_always_temporarily_and_restores_warning_filter(
        self, warning: Type[Warning]
    ):
        """
        Tests if the warning filter is temporarily set to "always"
        and restored to the previous state after the deprecated_function call.
        """

        @deprecated_function("DEPRECATED", warning=warning)
        def func(): ...

        # set the warning filter to ignore the specific warning
        warnings.filterwarnings("ignore", category=warning)

        with warnings.catch_warnings(record=True) as w:
            # filter should be temporarily disabled with deprecated_function decorator
            func()
            assert len(w) == 1

        with warnings.catch_warnings(record=True) as w:
            # filter should be enabled again and no warning should be raised
            warnings.warn("DEPRECATED", category=warning)
            assert len(w) == 0

    def test_function_is_wrapped(self):
        """
        Tests if the function is wrapped by the decorator properly.
        It should have the same attributes and return the same value.
        Functools.wraps should handle all of this.
        """

        def func(param1: int, param2: int) -> int:
            """Docstring"""
            return param1 + param2

        wrapped = deprecated_function("DEPRECATED")(func)

        # function attributes are the same
        assert wrapped.__annotations__ == func.__annotations__
        assert func.__doc__ == wrapped.__doc__
        assert func.__name__ == wrapped.__name__
        # retun of the call is the same
        with warnings.catch_warnings(record=True):
            assert wrapped(1, 2) == func(1, 2)

    def test_works_for_methods_as_well(self):
        """Tests if the decorator works for methods as well as for functions."""

        message = "DEPRECATED"

        class TestClass:

            @deprecated_function(message, warning=CustomWarning)
            def func(self, param1: int, param2: int) -> int:
                """Docstring"""
                return param1 + param2

        with warnings.catch_warnings(record=True) as w:
            test_instance = TestClass()
            result = test_instance.func(1, 2)

        assert len(w) == 1
        assert str(w[0].message) == message
        assert issubclass(w[0].category, CustomWarning)
        # check result of method call
        assert result == 3


@pytest.mark.deprecation
class TestDeprecatedClass:
    """Class with unit tests for the deprecated_class decorator"""

    @pytest.mark.parametrize(
        argnames="message",
        argvalues=[
            "This function is deprecated",
            "DEPRECATED: This function is deprecated",
        ],
    )
    def test_has_the_same_warning_message_as_passed(self, message: str):
        """Tests if the warning message is the same as the one passed as parameter."""
        message = "DEPRECATED"

        @deprecated_class(message)
        class TestClass: ...

        with warnings.catch_warnings(record=True) as w:
            TestClass()

        assert len(w) == 1
        assert str(w[0].message) == message

    def test_default_warning_type_is_deprecation_warning(self):
        """Tests if the default warning type is DeprecationWarning."""

        @deprecated_class("DEPRECATED")
        class TestClass: ...

        with warnings.catch_warnings(record=True) as w:
            TestClass()

        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)

    @pytest.mark.parametrize(
        argnames="warning",
        argvalues=[
            DeprecationWarning,
            FutureWarning,
            CustomWarning,
        ],
        ids=[
            "DeprecationWarning",
            "FutureWarning",
            "CustomWarning",
        ],
    )
    def test_raises_warning_type_specified_as_parameter_with_expected_message(
        self, warning: Type[Warning]
    ):
        """
        Tests if the warning raised is of the type specified as parameter
        and has the expected message.
        """
        message = "DEPRECATED"

        @deprecated_function(message, warning=warning)
        class TestClass: ...

        with warnings.catch_warnings(record=True) as w:
            TestClass()

        assert len(w) == 1
        assert issubclass(w[0].category, warning)
        assert str(w[0].message) == message

    @pytest.mark.parametrize(
        argnames="warning",
        argvalues=[
            DeprecationWarning,
            FutureWarning,
            CustomWarning,
        ],
        ids=[
            "DeprecationWarning",
            "FutureWarning",
            "CustomWarning",
        ],
    )
    def test_sets_to_always_temporarily_and_restores_warning_filter(
        self, warning: Type[Warning]
    ):
        """
        Tests if the warning filter is temporarily set to "always"
        and restored to the previous state after the deprecated_class call.
        """

        @deprecated_function("DEPRECATED", warning=warning)
        class TestClass: ...

        # set the warning filter to ignore the sepcific warning
        warnings.filterwarnings("ignore", category=warning)

        with warnings.catch_warnings(record=True) as w:
            # filter should be temporarily disabled with deprecated_class decorator
            TestClass()
            assert len(w) == 1

        with warnings.catch_warnings(record=True) as w:
            # filter should be enabled again and no warning should be raised
            warnings.warn("DEPRECATED", category=warning)
            assert len(w) == 0

    def test_if_warning_is_raised_only_on_init(self):
        """
        Tests if the warning is raised only on initialization of the class
        and not on method calls.
        """

        @deprecated_function("DEPRECATED", warning=CustomWarning)
        class TestClass:
            def __init__(self) -> None: ...
            def action(self) -> None: ...

        with warnings.catch_warnings(record=True) as w:
            # warns only on initialization
            instance = TestClass()
            assert len(w) == 1
            # does not warn on method call
            instance.action()
            assert len(w) == 1

    def test_if_class_is_wrapped_properly(self):
        """
        Tests if the class is wrapped by the decorator properly.
        It should only wrap __init__ method and not other methods.
        """

        class TestClass:
            def __init__(self, param1: int, param2: int) -> None:
                self.param1 = param1
                self.param2 = param2

            def action(self, param1: int, param2: int) -> int:
                return param1 + param2

        @deprecated_class("DEPRECATED", warning=CustomWarning)
        class WrappedClass(TestClass): ...

        # check if only WrappedClass raises the warning
        with warnings.catch_warnings(record=True) as w:
            test_instance = TestClass(1, 2)
            assert len(w) == 0
            wrapped_instance = WrappedClass(1, 2)
            assert len(w) == 1

        # check if other methods were not changed
        assert wrapped_instance.action(1, 2) == test_instance.action(1, 2)
        assert (
            wrapped_instance.action.__annotations__
            == test_instance.action.__annotations__
        )

        # check if __init__ was wrapped properly
        assert (
            WrappedClass.__init__.__annotations__ == TestClass.__init__.__annotations__
        )
        assert wrapped_instance.param1 == test_instance.param1
        assert wrapped_instance.param2 == test_instance.param2
