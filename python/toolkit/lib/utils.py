from typing import Any
from typing import Callable
from typing import TypeVar

T = TypeVar("T")


def format_doc(*args: Any, **kwargs: Any) -> Callable[..., Callable[..., T]]:
    """
    Function decorator that replaces the function's docstring with a formatted version
    using the specified `args` and `kwargs`.
    """

    def inner(func: Callable[..., T]) -> Callable[..., T]:
        func.__doc__ = func.__doc__.format(*args, **kwargs)
        return func

    return inner
