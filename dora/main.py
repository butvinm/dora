import sys

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


def _extract_expr_location(file_content: str, expr: Expression) -> str:
    lines = file_content.splitlines()
    start = expr.line - 1
    end = expr.end_line
    if end is None:
        end = expr.line

    return '\n'.join(lines[start:end])


def main() -> None:
    args = sys.argv[1:]
    if len(args) == 1:
        file, type_expression = args[0], None
    elif len(args) == 2:
        file, type_expression = args
    else:
        print(HELP)
        sys.exit(1)

    with open(file, 'r') as f:
        file_content = f.read()

    options = Options()
    options.export_types = True
    result = build(
        sources=[BuildSource(file, None)],
        options=options,
    )

    file_types = result.graph['__main__'].manager.all_types
    for expr, ty in file_types.items():
        if type_expression is None:
            expr_str = _extract_expr_location(file_content, expr)
            print(f'{file}:{expr.line}:{expr.column}')
            print(f'    Expr: {expr_str}')
            print(f'    Type: {ty}')
        elif str(ty) == type_expression:
            expr_str = _extract_expr_location(file_content, expr)
            print(f'{file}:{expr.line}:{expr.column} {expr_str}')


if __name__ == '__main__':
    main()
