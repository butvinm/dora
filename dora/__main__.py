"""Dora CLI."""

import argparse

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

    for search_result in search(args.paths, args.type_expression):
        print(search_result, end='\n\n')


if __name__ == '__main__':
    main()
