# Dora

> Project is in development and looks like total crap. I'm working on it.
> Be free to open an issue (and better a PR) if you have any ideas or suggestions.

Dora is a Python search engine, which allows you to search your Python codebase by expressions types.

It is initially aimed to help with migration of large codebase from Pydantic 1.10 to Pydantic 2.0 in cases when Pydantic-specific functions intersect with the names of the other functions, e.g. `pydantic.BaseModel.json()` and `requests.models.Response.json()`.

Dora is deeply inspired by the [Hoogle](https://hoogle.haskell.org/) and [Coogle](https://www.youtube.com/watch?v=wK1HjnwDQng&list=PLpM-Dvs8t0VYhYLxY-i7OcvBbDsG4izam&index=2).

## Installation

Package is still in development, so it is not available on PyPI. You can install and use it from the source code:

```bash
git clone https://github.com/butvinm/dora
cd dora
poetry install
```

and now you have `dora` command available in your shell.

## Usage

Current functionality is quite simple and allows you to search for the usage of object with specific type in your codebase.

Assume you have the following file `main.py`:

```python
from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    age: int


user = User(id=1, name='John Doe', age='invalid')
print(user)
```

You can search for the usage of `User` class in your codebase by running:

```bash
dora main.py __main__.User
```

and you will get the following output:

```
main.py:10:7 user = User(id=1, name='John Doe', age='invalid')
main.py:10:0 user = User(id=1, name='John Doe', age='invalid')
main.py:11:6 print(user)
```

You can also show types of all expressions in your codebase by running:

```bash
dora main.py
```

and you will get the following absolutely unreadable output with a lot of duplicates:

```
main.py:5:4
    Expr:     id: int
    Type: builtins.int
main.py:5:4
    Expr:     id: int
    Type: Any
main.py:6:4
    Expr:     name: str
    Type: builtins.str
main.py:6:4
    Expr:     name: str
    Type: Any
main.py:7:4
    Expr:     age: int
    Type: builtins.int
main.py:7:4
    Expr:     age: int
    Type: Any
main.py:10:7
    Expr: user = User(id=1, name='John Doe', age='invalid')
    Type: def (*, id: builtins.int, name: builtins.str, age: builtins.int) -> __main__.User
main.py:10:15
    Expr: user = User(id=1, name='John Doe', age='invalid')
    Type: Literal[1]?
main.py:10:23
    Expr: user = User(id=1, name='John Doe', age='invalid')
    Type: Literal['John Doe']?
main.py:10:39
    Expr: user = User(id=1, name='John Doe', age='invalid')
    Type: Literal['invalid']?
main.py:10:7
    Expr: user = User(id=1, name='John Doe', age='invalid')
    Type: __main__.User
main.py:10:0
    Expr: user = User(id=1, name='John Doe', age='invalid')
    Type: __main__.User
main.py:11:0
    Expr: print(user)
    Type: Overload(def (*values: builtins.object, sep: Union[builtins.str, None] =, end: Union[builtins.str, None] =, file: Union[_typeshed.SupportsWrite[builtins.str], None] =, flush: Literal[False] =), def (*values: builtins.object, sep: Union[builtins.str, None] =, end: Union[builtins.str, None] =, file: Union[builtins._SupportsWriteAndFlush[builtins.str], None] =, flush: builtins.bool))
main.py:11:6
    Expr: print(user)
    Type: __main__.User
main.py:11:0
    Expr: print(user)
    Type: None
```
