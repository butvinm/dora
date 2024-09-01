"""Dora configuration options."""

import argparse

from mypy.build import BuildSource
from mypy.find_sources import create_source_list
from mypy.main import process_options
from mypy.options import Options as MypyOptions


class DoraOptions:
    """Dora configuration options."""

    def __init__(self) -> None:
        """Initialize default options."""
        # Use ANSI color codes for results highlighting.
        self.color = True

        # Show mypy errors after the search results.
        self.show_mypy_errors = False

        # The type expression to search for.
        self.type_expression = None

        # The sources to search in.
        self.sources: list[BuildSource] = []


def parse_cli_options(parser: argparse.ArgumentParser, args: list[str]) -> tuple[DoraOptions, MypyOptions]:
    """Parse command line arguments to Dora and Mypy options with a little trickery.

    Args before '--' correspond to Dora options, and args after '--' correspond to Mypy options.
    As argparse does not support '--' as we need it, we have to do some trickery to get the desired behavior.

    This function may produce mypy arguments parsing error and exit with a traceback if the mypy arguments are invalid.
    TODO: pass custom stdout to capture the traceback and handle it gracefully in the dora entry point.

    Args:
        parser (argparse.ArgumentParser): The Dora CLI argument parser.
        args (list[str]): The command line arguments. Assume executable is trimmed.

    Returns:
        Dora and Mypy options.
    """
    try:
        rest_sep = args.index('--')
        dora_args, mypy_args = args[:rest_sep], args[rest_sep + 1:]
    except ValueError:
        dora_args, mypy_args = args, []

    # mypy requires at least one file to be specified, so we pass dummy 'stub.py'
    _, mypy_options = process_options(mypy_args + ['stub.py'])

    ns = parser.parse_args(dora_args)
    dora_options = DoraOptions()
    dora_options.color = ns.color
    dora_options.show_mypy_errors = ns.show_mypy_errors
    dora_options.type_expression = ns.type_expression
    dora_options.sources = create_source_list(ns.paths, mypy_options)

    return dora_options, mypy_options
