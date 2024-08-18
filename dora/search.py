"""Search engine."""

from random import randint
from typing import Any, Generator, Iterable

from mypy.build import BuildManager, BuildResult, BuildSource, build
from mypy.find_sources import create_source_list
from mypy.nodes import (
    ARG_NAMED,
    ARG_POS,
    ARG_STAR,
    CONTRAVARIANT,
    COVARIANT,
    FUNC_NO_INFO,
    GDEF,
    IMPLICITLY_ABSTRACT,
    INVARIANT,
    IS_ABSTRACT,
    LDEF,
    LITERAL_TYPE,
    MDEF,
    NOT_ABSTRACT,
    AssertStmt,
    AssertTypeExpr,
    AssignmentExpr,
    AssignmentStmt,
    AwaitExpr,
    Block,
    BreakStmt,
    BytesExpr,
    CallExpr,
    CastExpr,
    ClassDef,
    ComparisonExpr,
    ComplexExpr,
    ConditionalExpr,
    Context,
    ContinueStmt,
    Decorator,
    DelStmt,
    DictExpr,
    DictionaryComprehension,
    EllipsisExpr,
    EnumCallExpr,
    Expression,
    ExpressionStmt,
    FloatExpr,
    ForStmt,
    FuncBase,
    FuncDef,
    FuncItem,
    GeneratorExpr,
    GlobalDecl,
    IfStmt,
    Import,
    ImportAll,
    ImportBase,
    ImportFrom,
    IndexExpr,
    IntExpr,
    LambdaExpr,
    ListComprehension,
    ListExpr,
    Lvalue,
    MatchStmt,
    MemberExpr,
    MypyFile,
    NamedTupleExpr,
    NameExpr,
    NewTypeExpr,
    Node,
    NonlocalDecl,
    OperatorAssignmentStmt,
    OpExpr,
    OverloadedFuncDef,
    ParamSpecExpr,
    PassStmt,
    PlaceholderNode,
    PromoteExpr,
    RaiseStmt,
    RefExpr,
    ReturnStmt,
    RevealExpr,
    SetComprehension,
    SetExpr,
    SliceExpr,
    StarExpr,
    Statement,
    StrExpr,
    SuperExpr,
    SymbolNode,
    SymbolTable,
    SymbolTableNode,
    TempNode,
    TryStmt,
    TupleExpr,
    TypeAlias,
    TypeAliasExpr,
    TypeAliasStmt,
    TypeApplication,
    TypedDictExpr,
    TypeInfo,
    TypeVarExpr,
    TypeVarTupleExpr,
    UnaryExpr,
    Var,
    WhileStmt,
    WithStmt,
    YieldExpr,
    YieldFromExpr,
    is_final_node,
)
from mypy.options import BuildType, Options
from mypy.patterns import (
    AsPattern,
    ClassPattern,
    MappingPattern,
    OrPattern,
    SequencePattern,
    SingletonPattern,
    StarredPattern,
    ValuePattern,
)
from mypy.plugin import Plugin, ReportConfigContext
from mypy.traverser import TraverserVisitor


class DoraPlugin(Plugin):
    """Plugin to force mypy revalidate source files.

    Inspired by MypycPlugin from mypyc.
    """

    def __init__(self, paths: list[str], options: Options) -> None:
        """Initialize the plugin.

        Args:
            paths: The source files whose cache should be invalidated.
            options: The mypy options
        """
        super().__init__(options)
        self._pathes = set(paths)

    def report_config_data(self, ctx: ReportConfigContext) -> int | None:
        """Force revalidation of the source file.

        Args:
            ctx: The report configuration context.

        Returns:
            A random number to force revalidation of the source file.
        """
        if ctx.path in self._pathes:
            return randint(0, 69)

        return None


class SearchResult:
    """Occurrence of a type expression in a source file."""


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
        extra_plugins=[DoraPlugin(paths, options)],
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

        visitor = SearchVisitor(type_expression, build_result.manager)
        state.tree.accept(visitor)
        yield from visitor.search_results


class SearchVisitor(TraverserVisitor):
    """Performs a search for a type expression in a single ??? source file."""

    def __init__(self, type_expression: str | None, manager: BuildManager) -> None:
        """Initialize the search visitor.

        Args:
            type_expression: The type expression to search for.
            manager: The mypy BuildManager obtained from mypy.build.build() result.
        """
        super().__init__()
        self.type_expression = type_expression
        self.manager = manager
        self.search_results: list[SearchResult] = []
