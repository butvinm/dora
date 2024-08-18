from pathlib import Path
import sys
from typing import Iterable

from mypy.build import BuildSource, build
from mypy.nodes import Expression
from mypy.options import Options

HELP = """
Usage: dora <file> [<type_expression>]

Args:
    file:              The Python file to analyze
    type_expression:   The type expression to search for. If not provided, all types
                       in the file will be listed.
""".strip()


def _extract_expr_str(file_content: str, expr: Expression) -> str:
    lines = file_content.splitlines()
    start = expr.line - 1
    end = expr.end_line
    if end is None:
        end = expr.line

    return '\n'.join(lines[start:end])


def search_file(file: Path, type_expression: str | None) -> Iterable[str]:
    content = file.read_text()

    options = Options()
    options.export_types = True
    result = build(
        sources=[BuildSource(str(file), None)],
        options=options,
    )

    file_types = result.graph['__main__'].manager.all_types
    for expr, ty in file_types.items():
        if type_expression is None:
            expr_str = _extract_expr_str(content, expr)
            yield f'{file}:{expr.line}:{expr.column}\n    Expr: {expr_str}\n    Type: {ty}'
        elif str(ty) == type_expression:
            expr_str = _extract_expr_str(content, expr)
            yield f'{file}:{expr.line}:{expr.column} {expr_str}'


def main() -> None:
    args = sys.argv[1:]
    if len(args) == 1:
        file, type_expression = args[0], None
    elif len(args) == 2:
        file, type_expression = args
    else:
        print(HELP)
        sys.exit(1)

    file = Path(file)
    if not file.exists():
        print(f'File {file} does not exist')
        sys.exit(1)

    if file.is_dir():
        print('dir', file)
        for f in file.rglob('*.py'):
            print(f)
            for line in search_file(f, type_expression):
                print(line)
    elif file.is_file():
        for line in search_file(file, type_expression):
            print(line)


if __name__ == '__main__':
    main()
