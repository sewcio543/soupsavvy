import functools
import warnings
from typing import Callable, Type


def deprecated_function(
    message: str, warning: Type[Warning] = DeprecationWarning
) -> Callable:

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
