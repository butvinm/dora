"""Search engine."""

from random import random
from typing import Any, Generator, Iterable

from mypy.build import BuildManager, BuildResult, BuildSource, build
from mypy.find_sources import create_source_list
from mypy.nodes import MypyFile, Node
from mypy.options import Options
from mypy.plugin import Plugin, ReportConfigContext
from mypy.traverser import TraverserVisitor

from dora.ansi_colors import Ansi


class DoraPlugin(Plugin):
    """Plugin to force mypy revalidate source files.

    Inspired by MypycPlugin from mypyc.
    """

    def __init__(self, sources: list[BuildSource], options: Options) -> None:
        """Initialize the plugin.

        Args:
            sources: The build sources whose cache should be invalidated.
            options: The mypy options
        """
        super().__init__(options)
        self._sources = {source.path for source in sources}

    def report_config_data(self, ctx: ReportConfigContext) -> int | None:
        """Force revalidation of the source file.

        Args:
            ctx: The report configuration context.

        Returns:
            A random number to force revalidation of the source file.
        """
        if ctx.path in self._sources:
            return random()  # noqa: S311

        return None


class SearchResult:
    """Occurrence of a type expression in a source file."""

    def __init__(self, mypy_file: MypyFile, node: Node, type_expression: str) -> None:
        """Initialize the search result.

        Args:
            mypy_file: The source file where the type expression was found.
            node: The node where the type expression was found.
            type_expression: The type expression that was found.
        """
        self.mypy_file = mypy_file
        self.node = node
        self.type_expression = type_expression

    def to_str(self, color: bool = False) -> str:
        """Render the search result as a string.

        Args:
            color: Use ANSI colors to highlight expressions.

        Returns:
            A string representation of the search result.
        """
        node_type = self.node.__class__.__name__
        column_pointer_offset = ' ' * self.node.column

        node_text = self._extract_node_text(self.mypy_file.path, self.node)
        if color:
            end_column = self.node.end_column or self.node.column + 1
            node_text = node_text[:self.node.column] + Ansi.green.fg(node_text[self.node.column:end_column]) + node_text[end_column:]

        result_text = f'{self.mypy_file.path}:{self.node.line}:{self.node.column}\n'
        result_text += f'{column_pointer_offset}{self.type_expression} ({node_type})\n'
        result_text += f'{column_pointer_offset}v\n'
        result_text += node_text
        return result_text

    @classmethod
    def _extract_node_text(cls, path: str, node: Node) -> str:
        """Extract the text of a node from the source file.

        Args:
            path: The path to the source file.
            node: The node with location context.

        Returns:
            Node occurrence in the file.
        """
        # probably would be to slow
        # we can probably provide file content as an argument
        with open(path, 'r') as f:
            lines = f.readlines()

        line = node.line - 1
        end_line = node.end_line or node.line
        lines = lines[line:end_line]
        return ''.join(lines)


def search(paths: list[str], type_expression: str | None) -> Iterable[SearchResult]:
    """Search for a type expression in a source file.

    Args:
        paths: The source files to search in.
        type_expression: The type expression to search for.

    Returns:
        Found occurrences of the type expression.
    """
    options = Options()
    options.export_types = True
    options.preserve_asts = True

    sources = create_source_list(paths, options)

    build_result = build(
        sources=sources,
        options=options,
        extra_plugins=[DoraPlugin(sources, options)],
    )
    return _search(sources, type_expression, build_result)


def _search(
    sources: list[BuildSource],
    type_expression: str | None,
    build_result: BuildResult,
) -> Generator[SearchResult, None, None]:
    """Search for a type expression in a source file.

    Args:
        sources: The source files to search in.
        type_expression: The type expression to search for.
        build_result: The build result obtained from mypy.build.build().

    Yields:
        Found occurrences of the type expression.
    """
    for bs in sources:
        state = build_result.graph.get(bs.module)
        if state is None:
            continue

        if state.tree is None:
            continue

        visitor = SearchVisitor(state.tree, type_expression, build_result.manager)
        state.tree.accept(visitor)
        yield from visitor.search_results


class SearchVisitor(TraverserVisitor):
    """Performs a search for a type expression in a single ??? source file."""

    def __init__(
        self,
        mypy_file: MypyFile,
        type_expression: str | None,
        manager: BuildManager,
    ) -> None:
        """Initialize the search visitor.

        Args:
            mypy_file: Search source file and AST root.
            type_expression: The type expression to search for.
            manager: The mypy BuildManager obtained from mypy.build.build() result.
        """
        super().__init__()
        self.mypy_file = mypy_file
        self.type_expression = type_expression
        self.manager = manager
        self.search_results: list[SearchResult] = []

    def generic_visit(self, name: str, o: Node) -> None:
        """Check type_expression against given node.

        Args:
            name: Visitor name (visit_*: e.g. visit_var)
            o: Target node.

        Returns:
            Far traversing result.
        """
        node_type = self.manager.all_types.get(o)
        if node_type is not None:
            if self.type_expression is None:
                type_expression = str(node_type)
            else:
                type_expression = self.type_expression

            if str(node_type) == type_expression:
                self.search_results.append(SearchResult(self.mypy_file, o, type_expression))

        return super().__getattribute__(name)(o)

    def __getattribute__(self, name: str) -> Any:
        """Mock behavior of all possible visit_* methods.

        Args:
            name: Arg name.

        Returns:
            Visit method mock if name visit_* method acquired.
        """
        if name.startswith('visit_'):
            return lambda o: self.generic_visit(name, o)

        return super().__getattribute__(name)
