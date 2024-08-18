"""ANSI colors utils."""


from enum import IntEnum


class Ansi(IntEnum):
    """ANSI color codes."""

    black = 0
    red = 1
    green = 2
    yellow = 3
    blue = 4
    purple = 5
    cyan = 6
    white = 7

    def bg(self, text: str) -> str:
        """Add background color to the text.

        Args:
            text: Text to color.

        Returns:
            Text wrapped with ANSI background color and color reset.
        """
        return f'\x1b[4{self.value}m{text}\x1b[0m'

    def fg(self, text: str) -> str:
        """Add foreground color to the text.

        Args:
            text: Text to color.

        Returns:
            Text wrapped with ANSI foreground color and color reset.
        """
        return f'\x1b[3{self.value}m{text}\x1b[0m'
