# Dora

> The project is still in development and may look like a crap. I'm actively working on it.
> Feel free to open an issue (or better yet, a PR) if you have any ideas or suggestions.

Dora is a Python search engine that allows you to search your codebase by type expressions.

It is initially aimed to assist with migrating large codebases from Pydantic 1.10 to Pydantic 2.0, especially in cases where Pydantic-specific functions overlap with other function names, such as `pydantic.BaseModel.json()` and `requests.models.Response.json()`.

Dora is deeply inspired by [Hoogle](https://hoogle.haskell.org/) and [Coogle](https://www.youtube.com/watch?v=wK1HjnwDQng&list=PLpM-Dvs8t0VYhYLxY-i7OcvBbDsG4izam&index=2).

## Installation

The package is still in development and is not yet available on PyPI. You can install and use it from the source code:

```bash
git clone https://github.com/butvinm/dora
cd dora
poetry install
```

Now the `dora` command is available in your shell.

## Usage

The current functionality is simple and allows you to search for the usage of objects with specific types in your codebase.

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

You can search for the usage of the `User` class in your codebase by running:

```bash
dora main.py __main__.User
```

This will produce the following output:

```
main.py:10:7 user = User(id=1, name='John Doe', age='invalid')
main.py:10:0 user = User(id=1, name='John Doe', age='invalid')
main.py:11:6 print(user)
```

You can also display the types of all expressions in your codebase by running:

```bash
dora main.py
```

The output will be verbose and may contain duplicates:

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

## Roadmap

- [x] Proof of concept: search for types in a single file using mypy as backend.
- [x] Search within multiple files, excluding some files or directories.
- [ ] More accurate output, pointing to the exact location of the expression.
- [ ] Improve searching algorithm: properly handle overlaods, default arguments, etc.
- [ ] More convenient expressions: aliases for builtin types (maybe can be stolen from mypy/nodes.py), trim package name (__main__)
- [ ] Search for declarations, be able to select search target: declarations, usages, or both.
- [ ] The very far future: search by metainfo and context ("has @xxx decorator", "call of method .a() on type B", "subclass of A")
- [ ] Move to some fancy CLI library.
