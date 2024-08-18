"""Dora CLI."""

import argparse
import os
import sys

from mypy.errors import CompileError

from dora.search import search


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description='Search source files by type expressions.')
    parser.add_argument(
        '-t',
        '--type-expression',
        metavar='<type_expression>',
        help='The type expression to search for. If not provided, all types in the file will be listed.',
    )
    parser.add_argument(
        'paths',
        metavar='paths',
        nargs='+',
        help='The source files to search in.',
    )
    args = parser.parse_args()

    for path in args.paths:
        if not os.path.exists(path):
            parser.error(f'The path "{path}" does not exist.')

    try:
        for search_result in search(args.paths, args.type_expression):
            print(search_result, end='\n\n')
    except CompileError as e:
        print(e, file=sys.stderr)
        exit(1)


if __name__ == '__main__':
    main()
