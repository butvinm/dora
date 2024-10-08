# comment

# no-args stub function
from typing import TypeVar


def no_args_function():  # type: ignore
    pass


# no-args stub function with return type
def no_args_function_returns_none() -> None:
    return None


# positional arguments
def simple_args_function(a: int, b: int) -> int:
    return a + b


# keyword arguments
def simple_kwargs_function(a: int, b: int) -> int:
    return a + b


# positional and keyword arguments
def simple_args_kwargs_function(a: int, b: int, c: int) -> int:
    return a + b + c


# positional and keyword arguments with default values
def simple_args_kwargs_default_function(
    a: int,
    b: int,
    c: int = 1,
) -> int:
    return a + b + c


# positional-only arguments
def simple_args_only_function(a: int, b: int, /) -> int:
    return a + b


# keyword-only arguments
def simple_kwargs_only_function(*, a: int, b: int) -> int:
    return a + b


# positional-only and keyword-only arguments
def simple_args_only_kwargs_only_function(a: int, /, *, b: int) -> int:
    return a + b


T = TypeVar('T')

# generic function


def generic_function(a: T) -> T:
    return a


K = TypeVar('K')
V = TypeVar('V')

# very complex function definition


def very_complex_function_definition(
    a: K,
    b: V,
    c: dict[K, V] = {},
    /,
    *,
    d: int,
    e: int = 1,
) -> dict[K, V] | None:
    return None
