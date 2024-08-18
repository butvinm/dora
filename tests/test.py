"""Snapshot-tests of dora CLI.

These tests run a dora binary and compare output with previously recorded.
"""
import os
import subprocess
from pathlib import Path

CODEBASE_PATH = Path(__file__).parent.joinpath('codebase').relative_to(Path.cwd())
RESULTS = Path(__file__).parent.joinpath('results').relative_to(Path.cwd())
RESULTS.mkdir(exist_ok=True)


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True)


def _build_result_text(title: str, result: subprocess.CompletedProcess) -> str:
    result_text = f'{title}\n'
    result_text += f'returncode: {result.returncode}\n'
    result_text += f'stdout:\n{result.stdout}\n'
    result_text += f'stderr:\n{result.stderr}\n'
    return result_text


def record_test_case(title: str, args: list[str]) -> None:
    golden_result_path = RESULTS.joinpath(title)
    result = _run(args)
    golden_result_text = _build_result_text(title, result)
    golden_result_path.write_text(golden_result_text)


def rerun_test_case(title: str, args: list[str]) -> str | None:
    golden_result_path = RESULTS.joinpath(title)
    golden_result_text = golden_result_path.read_text()

    result = _run(args)
    result_text = _build_result_text(title, result)
    if result_text != golden_result_text:
        failed_result_path = golden_result_path.with_suffix('.failed')
        failed_result_path.write_text(result_text)
        result = _run(['diff', '-u', golden_result_path, failed_result_path])
        return result.stdout

    return None


test_cases = [
    ('Given no args, help should be shown', ['dora']),
    ('Given extra args, help should be shown', ['dora', 'a', 'b', 'c']),
    ('Given non-existing file, error should be shown', ['dora', 'non-existing-file.py']),
    ('Given path only, all types should be displayed', ['dora', CODEBASE_PATH]),
    ('Search for builtins.str', ['dora', CODEBASE_PATH, 'builtins.str']),
]


def record_test_cases() -> None:
    print('RECORD')
    for title, args in test_cases:
        print(title, args)
        record_test_case(title, args)


def rerun_test_cases() -> bool:
    print('RERUN')
    failed = False
    for title, args in test_cases:
        print(title, args, end=' ')
        diff = rerun_test_case(title, args)
        if diff:
            print('FAILED')
            print(diff)
            failed = True
        else:
            print('OK')

    return failed


if __name__ == '__main__':
    if os.environ.get('DORA_SNAPSHOT_RECORD'):
        record_test_cases()
    else:
        if rerun_test_cases():
            exit(1)
