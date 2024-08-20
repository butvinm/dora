"""ANSI colors utils."""


from enum import Enum


class Color(Enum):
    """ANSI color codes."""

    black = 0
    red = 1
    green = 2
    yellow = 3
    blue = 4
    purple = 5
    cyan = 6
    white = 7


def bg(color: Color, text: str) -> str:
    """Add background color to the text.

    Args:
        color: Color of the background.
        text: Text to color.

    Returns:
        Text wrapped with ANSI background color and color reset.
    """
    return f'\x1b[4{color.value}m{text}\x1b[0m'


def fg(color: Color, text: str) -> str:
    """Add foreground color to the text.

    Args:
        color: Color of the foreground.
        text: Text to color.

    Returns:
        Text wrapped with ANSI foreground color and color reset.
    """
    return f'\x1b[3{color.value}m{text}\x1b[0m'
