"""Module for deprecation decorators and functions."""

import functools
import warnings
from typing import Callable, Type


def deprecated_function(
    message: str, warning: Type[Warning] = DeprecationWarning
) -> Callable:
    """
    Decorator for deprecating functions.
    It raises a warning when the decorated function is called.
    Use for functions that will be removed in future versions.
    Can be used as a decorator for methods as well.

    Parameters
    ----------
    message : str
        Message to be displayed in the warning.
    warning : Type[Warning], optional
        Type of warning to be raised, by default DeprecationWarning.

    Returns
    -------
    Callable
        Decorated function.
    """

    def decorator(func: Callable) -> Callable:

        @functools.wraps(func)
        def new(*args, **kwargs):
            deprecated(message, warning=warning)
            return func(*args, **kwargs)

        return new

    return decorator


def deprecated_class(
    message: str, warning: Type[Warning] = DeprecationWarning
) -> Callable:
    """
    Decorator for deprecating classes.
    It raises a warning when the decorated class is instantiated.
    Use for classes that will be removed in future versions.
    Wraps the __init__ method of the class to raise the warning.

    Parameters
    ----------
    message : str
        Message to be displayed in the warning.
    warning : Type[Warning], optional
        Type of warning to be raised, by default DeprecationWarning.

    Returns
    -------
    Callable
        Decorated class.
    """

    def decorator(cls: Type) -> Type:
        original_init = cls.__init__

        @functools.wraps(original_init)
        def new_init(self, *args, **kwargs):
            deprecated(message, warning=warning)
            original_init(self, *args, **kwargs)

        cls.__init__ = new_init
        return cls

    return decorator


def deprecated(message: str, warning: Type[Warning] = DeprecationWarning) -> None:
    """
    Function for raising warning on deprecated functionalities.
    It turns off the warning filter for specified warning,
    raises the warning and then turns it back on to the default.

    Parameters
    ----------
    message : str
        Message to be displayed in the warning.
    warning : Type[Warning], optional
        Type of warning to be raised, by default DeprecationWarning.
    """
    warnings.simplefilter("always", warning)
    warnings.warn(message, category=warning, stacklevel=2)
    warnings.simplefilter("default", warning)
