"""Dora is a tool to search python source files by type expressions.

Example:
    my_module.py:

    def foo() -> int:
        return 42

    def bar() -> str:
        return 'spam'

    $ dora 'int' my_module.py
    my_module.py:1:0: def foo() -> int:
"""
