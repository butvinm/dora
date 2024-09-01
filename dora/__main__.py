"""Dora CLI."""

import argparse
import os
import sys

from mypy.errors import CompileError

from dora.options import parse_cli_options
from dora.search import search


def make_arg_parser() -> argparse.ArgumentParser:
    """Create arguments parser for Dora CLI.

    Usage is patched to add notion of mypy args that cannot be conveniently defined via argparse.

    Returns:
        Dora CLI arguments parser.
    """
    parser = argparse.ArgumentParser(
        description='Search source files by type expressions.',
        epilog='Arguments after "--" will be passed to mypy. Use `mypy --help` to show available options.',
    )
    parser.add_argument(
        '-t',
        '--type-expression',
        help='The type expression to search for. If not provided, all types in the file will be listed.',
    )
    parser.add_argument(
        'paths',
        nargs='+',
        help='The source files to search in.',
    )
    parser.set_defaults(color=True)
    parser.add_argument(
        '--no-color',
        dest='color',
        help='Suppress colored output.',
        action='store_false',
    )
    parser.set_defaults(show_mypy_errors=False)
    parser.add_argument(
        '--show-mypy-errors',
        help='Show mypy errors before the search results.',
        action='store_true',
    )
    default_usage = parser.format_usage()[7:-1]
    parser.usage = '{default_usage} [-- mypy_args]\n'.format(default_usage=default_usage)
    return parser


def main() -> None:
    """CLI entry point."""
    parser = make_arg_parser()
    dora_options, mypy_options = parse_cli_options(parser, sys.argv[1:])

    for source in dora_options.sources:
        if source.path is None or not os.path.exists(source.path):
            parser.error('The path "{path}" does not exist.'.format(path=source.path))

    try:
        build_result, search_results = search(dora_options, mypy_options)
        for search_result in search_results:
            print(search_result.to_str(dora_options.color), end='\n\n')

        if dora_options.show_mypy_errors:
            print(*build_result.errors, sep='\n', file=sys.stderr)
    except CompileError as e:
        print(e, file=sys.stderr)
        exit(1)


if __name__ == '__main__':
    main()
