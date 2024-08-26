"""Snapshot-tests of dora CLI.

These tests run a dora binary and compare output with previously recorded.
"""
import os
import shutil
import subprocess
from pathlib import Path
from typing import TypeAlias

CODEBASE_PATH = Path(__file__).parent.joinpath('codebase').relative_to(Path.cwd())
RECORDS = Path(__file__).parent.joinpath('records').relative_to(Path.cwd())
RECORDS.mkdir(exist_ok=True)


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True)


def _build_result_text(title: str, args: list[str], result: subprocess.CompletedProcess) -> str:
    result_text = f'title: {title}\n'
    result_text += f'args: {args}\n'
    result_text += f'exitcode: {result.returncode}\n'
    result_text += f'stdout:\n{result.stdout}\n'
    result_text += f'stderr:\n{result.stderr}\n'
    return result_text


def record_test_case(title: str, args: list[str]) -> None:
    golden_result_path = RECORDS.joinpath(title)
    result = _run(args)
    golden_result_text = _build_result_text(title, args, result)
    golden_result_path.write_text(golden_result_text)


def replay_test_case(title: str, args: list[str]) -> str | None:
    golden_result_path = RECORDS.joinpath(title)
    golden_result_text = golden_result_path.read_text()

    result = _run(args)
    result_text = _build_result_text(title, args, result)
    if result_text != golden_result_text:
        failed_result_path = golden_result_path.with_suffix('.failed')
        failed_result_path.write_text(result_text)
        result = _run(['diff', '-u', '--color', golden_result_path, failed_result_path])
        return result.stdout

    return None


test_cases = [
    (
        'Given no args, usage should be shown',
        ['dora'],
    ),
    (
        'Given -h flag, help should be shown',
        ['dora', '-h'],
    ),
    (
        'Given non-existing file, error should be shown',
        ['dora', 'non-existing-file.py'],
    ),
    (
        'Without specified type expression, all types should be displayed',
        ['dora', CODEBASE_PATH],
    ),
    (
        'With --no-color flag output should not contain ansi colors',
        ['dora', '--no-color', CODEBASE_PATH],
    ),
    (
        'Given directory, all files should be analyzed recursively',
        ['dora', CODEBASE_PATH],
    ),
    (
        'Given duplicated pathes, mypy error expected',
        ['dora', CODEBASE_PATH / 'main.py', CODEBASE_PATH / 'main.py'],
    ),
    (
        'Search for `builtins.str`',
        ['dora', CODEBASE_PATH, '-t', 'builtins.str'],
    ),
    (
        'Search for `def (a: builtins.int, b: builtins.int) -> builtins.str`',
        ['dora', CODEBASE_PATH, '-t', 'def (a: builtins.int, b: builtins.int) -> builtins.str'],
    ),
    (
        'New type syntax without --show-mypy-errors flag',
        ['dora', CODEBASE_PATH / 'new_type_syntax.py'],
    ),
    (
        'New type syntax with --show-mypy-errors flag',
        ['dora', CODEBASE_PATH / 'new_type_syntax.py', '--show-mypy-errors'],
    ),
    (
        'New type syntax with --show-mypy-errors flag and mypy incomplete feature enabled via -- args',
        ['dora', CODEBASE_PATH / 'new_type_syntax.py', '--show-mypy-errors', '--', '--enable-incomplete-feature', 'NewGenericSyntax'],
    ),
]
TestCase: TypeAlias = tuple[str, list[str]]


def clear_cache() -> None:
    for path in Path.cwd().rglob('.mypy_cache'):
        shutil.rmtree(path)


def record_test_cases(test_cases: list[TestCase]) -> None:
    for title, args in test_cases:
        print(title, args)
        record_test_case(title, args)


def replay_test_cases(test_cases: list[TestCase]) -> bool:
    failed = False
    for title, args in test_cases:
        print(title, args, end=' ')
        diff = replay_test_case(title, args)
        if diff:
            print('FAILED')
            print(diff)
            failed = True
        else:
            print('OK')

    return failed


if __name__ == '__main__':
    # check if results contain redundant test cases
    recorded_test_cases = [result.name for result in RECORDS.glob('*')]
    redundant_test_cases = set(recorded_test_cases) - {title for title, _ in test_cases}
    if redundant_test_cases:
        print(f'Results directory contains redundant test cases: {redundant_test_cases}')
        exit(2)

    if os.environ.get('DORA_SNAPSHOT_RECORD'):
        print('Recording test cases')
        clear_cache()
        record_test_cases(test_cases)
    else:
        print('Replayning test cases w/o cache')
        clear_cache()

        if replay_test_cases(test_cases):
            exit(1)

        print()
        print('Replayning test cases with cache')
        if replay_test_cases(test_cases):
            exit(1)
